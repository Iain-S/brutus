#include "gymnasium.h"
#include "building/building.h"
#include "city/data_private.h"

#include "city/finance.h"
#include "city/ratings.h"
#include "city/victory.h"
#include "core/config.h"
#include "core/file.h"
#include "core/hotkey_config.h"
#include "game/file.h"
#include "game/game.h"
#include "game/mission.h"
#include "game/resource.h"
#include "game/time.h"
#include "game/tick.h"
#include "map/building.h"
#include "map/bridge.h"
#include "map/grid.h"
#include "map/terrain.h"
#include "platform/file_manager.h"
#include "scenario/criteria.h"
#include "scenario/data.h"
#include "scenario/property.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <direct.h>
#define get_current_dir _getcwd
#else
#include <unistd.h>
#define get_current_dir getcwd
#endif

/**
 * Internal environment state
 */
struct julius_env {
    int initialized;
    int game_initialized;
    char error_message[512];

    // Configuration
    julius_env_config_t config;

    // Episode state
    int current_tick;
    int episode_active;
    int campaign_rank;
    int campaign_selected;

    // Previous ratings for reward calculation
    int prev_culture;
    int prev_prosperity;
    int prev_peace;
    int prev_favor;
    int prev_treasury;

    unsigned int next_snapshot_id;
};

struct julius_snapshot {
    julius_env_t *owner;
    char filename[2 * FILE_NAME_MAX];
    int current_tick;
    int episode_active;
    int prev_culture;
    int prev_prosperity;
    int prev_peace;
    int prev_favor;
    int prev_treasury;
};

static char initial_cwd[FILE_NAME_MAX];
static int initial_cwd_set = 0;

/**
 * Calculate reward based on rating changes and other factors
 */
static float calculate_reward(julius_env_t *env)
{
    float reward = 0.0f;

    // Get current ratings
    int culture = city_rating_culture();
    int prosperity = city_rating_prosperity();
    int peace = city_rating_peace();
    int favor = city_rating_favor();
    int treasury = city_finance_treasury();

    // Reward for improving ratings (scale by importance)
    reward += (culture - env->prev_culture) * 0.1f;
    reward += (prosperity - env->prev_prosperity) * 0.1f;
    reward += (peace - env->prev_peace) * 0.1f;
    reward += (favor - env->prev_favor) * 0.1f;

    // Small reward for maintaining positive treasury
    if (treasury > 0) {
        reward += 0.01f;
    }

    // Penalty for bankruptcy
    if (treasury < 0) {
        reward -= 1.0f;
    }

    // Update previous values
    env->prev_culture = culture;
    env->prev_prosperity = prosperity;
    env->prev_peace = peace;
    env->prev_favor = favor;
    env->prev_treasury = treasury;

    return reward;
}

/**
 * Check if episode should end
 */
static void check_termination(julius_env_t *env, julius_env_step_result_t *result)
{
    int victory = city_victory_state();

    if (victory == VICTORY_STATE_WON) {
        result->terminated = 1;
        result->reward += 100.0f;  // Large bonus for winning
        snprintf(result->info, sizeof(result->info), "Victory achieved!");
        return;
    }

    if (victory == VICTORY_STATE_LOST) {
        result->terminated = 1;
        result->reward -= 50.0f;  // Penalty for losing
        snprintf(result->info, sizeof(result->info), "Defeat - scenario lost");
        return;
    }

    // Check if max ticks reached
    if (env->config.max_ticks > 0 && env->current_tick >= env->config.max_ticks) {
        result->truncated = 1;
        snprintf(result->info, sizeof(result->info), "Max ticks reached");
        return;
    }

    // Check bankruptcy (severe treasury deficit)
    int treasury = city_finance_treasury();
    if (treasury < -5000) {
        result->terminated = 1;
        result->reward -= 50.0f;
        snprintf(result->info, sizeof(result->info), "Bankruptcy - treasury too low");
        return;
    }
}

julius_env_t *julius_env_create(const julius_env_config_t *config)
{
    if (!config) {
        return NULL;
    }

    julius_env_t *env = (julius_env_t *)calloc(1, sizeof(julius_env_t));
    if (!env) {
        return NULL;
    }

    if (!initial_cwd_set) {
        if (get_current_dir(initial_cwd, sizeof(initial_cwd))) {
            initial_cwd_set = 1;
        }
    }
    if (initial_cwd_set) {
        char config_path[FILE_NAME_MAX];
        char hotkey_path[FILE_NAME_MAX];
        snprintf(config_path, sizeof(config_path), "%s/%s", initial_cwd, "julius.ini");
        snprintf(hotkey_path, sizeof(hotkey_path), "%s/%s", initial_cwd, "julius-hotkeys.ini");
        config_set_file_path(config_path);
        hotkey_config_set_file_path(hotkey_path);
    }

    // Copy configuration
    if (config->data_directory) {
        env->config.data_directory = strdup(config->data_directory);
    }
    if (config->scenario_file) {
        env->config.scenario_file = strdup(config->scenario_file);
    }
    env->config.max_ticks = config->max_ticks;
    env->config.tick_speed_ms = config->tick_speed_ms;

    // Set base path for game data
    if (config->data_directory) {
        if (!platform_file_manager_set_base_path(config->data_directory)) {
            snprintf(env->error_message, sizeof(env->error_message),
                    "Failed to set data directory: %s", config->data_directory);
            free(env);
            return NULL;
        }
    }

    // Pre-initialize game
    if (!game_pre_init()) {
        snprintf(env->error_message, sizeof(env->error_message),
                "Game pre-initialization failed");
        free(env);
        return NULL;
    }

    // Initialize game
    if (!game_init()) {
        snprintf(env->error_message, sizeof(env->error_message),
                "Game initialization failed");
        free(env);
        return NULL;
    }

    env->game_initialized = 1;
    env->initialized = 1;

    return env;
}

void julius_env_destroy(julius_env_t *env)
{
    if (!env) {
        return;
    }

    if (env->game_initialized) {
        game_exit();
    }

    if (env->config.data_directory) {
        free((void *)env->config.data_directory);
    }
    if (env->config.scenario_file) {
        free((void *)env->config.scenario_file);
    }

    free(env);
}

int julius_env_reset(julius_env_t *env, gymnasium_observation_t *observation)
{
    if (!env || !env->initialized) {
        return -1;
    }

    if (env->campaign_selected) {
        scenario_set_custom(0);
        scenario_set_campaign_rank(env->campaign_rank);
        scenario_set_campaign_mission(game_mission_peaceful());
        // The campaign path ignores the filename and loads mission1.pak.
        if (!game_file_start_scenario("")) {
            env->episode_active = 0;
            snprintf(env->error_message, sizeof(env->error_message), "Failed to load campaign rank %d", env->campaign_rank);
            return -1;
        }
    } else if (env->config.scenario_file) {
        if (!game_file_start_scenario(env->config.scenario_file)) {
            snprintf(env->error_message, sizeof(env->error_message),
                    "Failed to load scenario: %s", env->config.scenario_file);
            return -1;
        }
    }

    // Reset episode state
    env->current_tick = 0;
    env->episode_active = 1;

    // Initialize previous ratings for reward calculation
    env->prev_culture = city_rating_culture();
    env->prev_prosperity = city_rating_prosperity();
    env->prev_peace = city_rating_peace();
    env->prev_favor = city_rating_favor();
    env->prev_treasury = city_finance_treasury();

    // Reset victory state
    city_victory_reset();

    // Get initial observation
    if (observation) {
        if (gymnasium_get_observation(observation) != 0) {
            snprintf(env->error_message, sizeof(env->error_message),
                    "Failed to get initial observation");
            return -1;
        }
    }

    return 0;
}

int julius_env_select_campaign(julius_env_t *env, int rank)
{
    if (!env || !env->initialized) {
        return -1;
    }
    if (rank < 0 || rank > 11 || env->config.scenario_file) {
        snprintf(env->error_message, sizeof(env->error_message),
            "Campaign rank must be 0..11 and cannot be combined with a scenario file");
        return -1;
    }
    env->campaign_rank = rank;
    env->campaign_selected = 1;
    env->episode_active = 0;
    return 0;
}

int julius_env_bridge_span(julius_env_t *env, int x, int y, int *direction)
{
    if (!env || !env->episode_active || !direction || x <= 0 || y <= 0 ||
        x >= map_grid_width() - 1 || y >= map_grid_height() - 1) {
        return 0;
    }
    int length = 0;
    int valid = map_bridge_calculate_length_direction(x, y, &length, direction);
    map_bridge_reset_building_length();
    return valid ? length : 0;
}

int julius_env_get_population_info(julius_env_t *env, char *output, int capacity)
{
    if (!env || !env->initialized || !output || capacity <= 0) {
        return -1;
    }
    int written = snprintf(output, capacity,
        "{\"yearly_deaths\":%d,\"yearly_births\":%d,\"lost_homeless\":%d,"
        "\"lost_removal\":%d,\"health\":%d}",
        city_data.population.yearly_deaths, city_data.population.yearly_births,
        city_data.population.lost_homeless, city_data.population.lost_removal,
        city_data.health.value);
    return written < 0 || written >= capacity ? -1 : 0;
}

int julius_env_get_buildings(julius_env_t *env, char *output, int capacity)
{
    if (!env || !env->initialized || !output || capacity < 3) {
        return -1;
    }
    int used = 1, count = 0;
    output[0] = '[';
    for (int i = 1; i < MAX_BUILDINGS; i++) {
        const building *b = building_get(i);
        if (b->state != BUILDING_STATE_IN_USE) {
            continue;
        }
        int house = building_is_house(b->type);
        int food = 0;
        if (house) {
            for (int j = INVENTORY_MIN_FOOD; j < INVENTORY_MAX_FOOD; j++) {
                food += b->data.house.inventory[j];
            }
        }
        int written = snprintf(output + used, capacity - used,
            "%s{\"id\":%d,\"type\":%d,\"x\":%d,\"y\":%d,\"size\":%d,"
            "\"workers\":%d,\"houses_covered\":%d,\"population\":%d,\"food\":%d,"
            "\"well\":%d,\"fountain\":%d,\"level\":%d}",
            count ? "," : "", b->id, b->type, b->x, b->y, b->size,
            b->num_workers, b->houses_covered, house ? b->house_population : 0, food,
            house ? b->has_well_access : 0, house ? b->has_water_access : 0,
            house ? b->subtype.house_level : -1);
        if (written < 0 || written >= capacity - used) {
            return -1;
        }
        used += written;
        count++;
    }
    int written = snprintf(output + used, capacity - used, "]");
    return written < 0 || written >= capacity - used ? -1 : 0;
}

int julius_env_get_mission_info(julius_env_t *env, char *output, int capacity)
{
    if (!env || !env->initialized || !env->episode_active || !output || capacity <= 0) {
        return -1;
    }
    int used = snprintf(output, capacity,
        "{\"campaign_rank\":%d,\"campaign_mission\":%d,\"is_custom\":%d,"
        "\"is_tutorial\":%d,\"start_year\":%d,\"gladiator_revolt\":%d,"
        "\"entry\":[%d,%d],\"combat_events\":[",
        scenario_campaign_rank(), scenario_campaign_mission(), scenario_is_custom(),
        scenario_is_tutorial_1() || scenario_is_tutorial_2() || scenario_is_tutorial_3(),
        scenario.start_year, scenario.gladiator_revolt.enabled,
        scenario.entry_point.x, scenario.entry_point.y);
    if (used < 0 || used >= capacity) {
        return -1;
    }
    int count = 0;
    for (int i = 0; i < MAX_INVASIONS; i++) {
        const invasion_t *event = &scenario.invasions[i];
        if (!event->type) {
            continue;
        }
        int written = snprintf(output + used, capacity - used,
            "%s{\"type\":%d,\"year_offset\":%d,\"month\":%d,\"amount\":%d}",
            count ? "," : "", event->type, event->year, event->month, event->amount);
        if (written < 0 || written >= capacity - used) {
            return -1;
        }
        used += written;
        count++;
    }
    int written = snprintf(output + used, capacity - used, "]}");
    return written < 0 || written >= capacity - used ? -1 : 0;
}

julius_snapshot_t *julius_env_snapshot_create(julius_env_t *env)
{
    if (!env || !env->initialized || !env->episode_active) {
        if (env) {
            snprintf(env->error_message, sizeof(env->error_message),
                "Cannot snapshot an inactive environment");
        }
        return NULL;
    }

    if (!initial_cwd_set) {
        snprintf(env->error_message, sizeof(env->error_message),
            "Unable to determine a writable snapshot directory");
        return NULL;
    }

    julius_snapshot_t *snapshot = calloc(1, sizeof(*snapshot));
    if (!snapshot) {
        snprintf(env->error_message, sizeof(env->error_message),
            "Unable to allocate snapshot");
        return NULL;
    }

    snapshot->owner = env;
    int filename_length = snprintf(snapshot->filename, sizeof(snapshot->filename),
        "%s/julius-gym-snapshot-%p-%u.sav", initial_cwd, (void *)env,
        env->next_snapshot_id++);
    if (filename_length < 0 || filename_length >= (int)sizeof(snapshot->filename)) {
        snprintf(env->error_message, sizeof(env->error_message),
            "Snapshot path is too long");
        free(snapshot);
        return NULL;
    }

    if (!game_file_write_saved_game(snapshot->filename)) {
        snprintf(env->error_message, sizeof(env->error_message),
            "Failed to save snapshot");
        free(snapshot);
        return NULL;
    }

    snapshot->current_tick = env->current_tick;
    snapshot->episode_active = env->episode_active;
    snapshot->prev_culture = env->prev_culture;
    snapshot->prev_prosperity = env->prev_prosperity;
    snapshot->prev_peace = env->prev_peace;
    snapshot->prev_favor = env->prev_favor;
    snapshot->prev_treasury = env->prev_treasury;
    return snapshot;
}

int julius_env_snapshot_restore(julius_env_t *env, const julius_snapshot_t *snapshot)
{
    if (!env || !env->initialized || !snapshot || snapshot->owner != env) {
        if (env) {
            snprintf(env->error_message, sizeof(env->error_message),
                "Snapshot does not belong to this environment");
        }
        return -1;
    }

    if (!game_file_load_saved_game(snapshot->filename)) {
        snprintf(env->error_message, sizeof(env->error_message),
            "Failed to restore snapshot");
        return -1;
    }

    env->current_tick = snapshot->current_tick;
    env->episode_active = snapshot->episode_active;
    env->prev_culture = snapshot->prev_culture;
    env->prev_prosperity = snapshot->prev_prosperity;
    env->prev_peace = snapshot->prev_peace;
    env->prev_favor = snapshot->prev_favor;
    env->prev_treasury = snapshot->prev_treasury;
    env->error_message[0] = '\0';
    return 0;
}

void julius_env_snapshot_destroy(julius_snapshot_t *snapshot)
{
    if (!snapshot) {
        return;
    }

    game_file_delete_saved_game(snapshot->filename);
    free(snapshot);
}

int julius_env_step(julius_env_t *env, const gymnasium_action_t *action,
                    julius_env_step_result_t *result)
{
    if (!env || !env->initialized || !action || !result) {
        if (env) {
            snprintf(env->error_message, sizeof(env->error_message),
                    "Invalid parameters to julius_env_step");
        }
        return -1;
    }

    if (!env->episode_active) {
        snprintf(env->error_message, sizeof(env->error_message),
                "Episode not active, call reset first");
        return -1;
    }

    // Initialize result
    memset(result, 0, sizeof(julius_env_step_result_t));

    // Execute the action
    gymnasium_action_result_t action_result;
    int action_status = gymnasium_execute_action(action, &action_result);

    // Small penalty for failed actions
    if (action_status != 0) {
        result->reward -= 0.1f;
    }

    // Run one game tick
    game_tick_run();
    env->current_tick++;

    // Calculate reward based on state changes
    result->reward += calculate_reward(env);

    // Get current observation
    if (gymnasium_get_observation(&result->observation) != 0) {
        snprintf(env->error_message, sizeof(env->error_message),
                "Failed to get observation after step");
        return -1;
    }

    // Check for episode termination
    check_termination(env, result);

    if (result->terminated || result->truncated) {
        env->episode_active = 0;
    }

    // Add action result info if no termination info
    if (strlen(result->info) == 0) {
        snprintf(result->info, sizeof(result->info), "%s", action_result.message);
    }

    return 0;
}

int julius_env_get_observation(julius_env_t *env, gymnasium_observation_t *observation)
{
    if (!env || !env->initialized || !observation) {
        return -1;
    }

    return gymnasium_get_observation(observation);
}

const char *julius_env_get_error(julius_env_t *env)
{
    if (!env) {
        return NULL;
    }

    if (strlen(env->error_message) > 0) {
        return env->error_message;
    }

    return NULL;
}

int julius_env_is_initialized(julius_env_t *env)
{
    return env && env->initialized;
}

int julius_env_get_map_data(julius_env_t *env, uint16_t *terrain_data,
                             uint16_t *building_data, int *width, int *height)
{
    if (!env || !env->initialized || !terrain_data || !building_data || !width || !height) {
        return -1;
    }

    // Get actual map dimensions
    *width = map_grid_width();
    *height = map_grid_height();

    // Extract terrain and building data for each grid cell
    for (int y = 0; y < GRID_SIZE; y++) {
        for (int x = 0; x < GRID_SIZE; x++) {
            int index = y * GRID_SIZE + x;
            if (x >= *width || y >= *height) {
                terrain_data[index] = 0;
                building_data[index] = 0;
                continue;
            }
            int grid_offset = map_grid_offset(x, y);

            // Get terrain flags
            terrain_data[index] = (uint16_t) map_terrain_get(grid_offset);

            // Get building ID
            building_data[index] = (uint16_t) map_building_at(grid_offset);
        }
    }

    return 0;
}
