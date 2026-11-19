#ifndef GYMNASIUM_GYMNASIUM_H
#define GYMNASIUM_GYMNASIUM_H

#include "observation.h"
#include "action.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Environment handle (opaque pointer for Python)
 */
typedef struct julius_env julius_env_t;

/**
 * Saved environment state. The representation is intentionally opaque so the
 * backing store can move from a temporary save file to memory later.
 */
typedef struct julius_snapshot julius_snapshot_t;

/**
 * Environment configuration
 */
typedef struct {
    const char *data_directory;     // Path to Caesar III data files
    const char *scenario_file;      // Path to scenario file (optional, can be NULL for sandbox)
    int32_t max_ticks;             // Maximum ticks per episode (0 = unlimited)
    int32_t tick_speed_ms;         // Milliseconds per tick (1 = fastest)
} julius_env_config_t;

/**
 * Step result structure
 * Returned after each env_step() call
 */
typedef struct {
    gymnasium_observation_t observation;  // Current state
    float reward;                        // Reward for this step
    int32_t terminated;                  // Episode ended (goal reached or failed)
    int32_t truncated;                   // Episode cut off (max steps reached)
    char info[256];                      // Additional information
} julius_env_step_result_t;

/**
 * Create and initialize a Julius environment
 * @param config Configuration for the environment
 * @return Environment handle, or NULL on error
 */
julius_env_t *julius_env_create(const julius_env_config_t *config);

/**
 * Destroy an environment and free resources
 * @param env Environment handle
 */
void julius_env_destroy(julius_env_t *env);

/**
 * Reset the environment to initial state
 * @param env Environment handle
 * @param observation Output: initial observation (can be NULL)
 * @return 0 on success, -1 on error
 */
int julius_env_reset(julius_env_t *env, gymnasium_observation_t *observation);

/** Select a peaceful campaign rank (0..11) for subsequent resets.
 * Rejects environments configured with a scenario filename. Does not load yet.
 */
int julius_env_select_campaign(julius_env_t *env, int rank);

/** Write JSON mission identity and scheduled combat events to a caller buffer.
 * Returns -1 for an inactive episode or an insufficient buffer.
 */
int julius_env_get_mission_info(julius_env_t *env, char *output, int capacity);

/** Query a valid bridge span; returns length, or zero for an invalid site.
 * Direction uses engine cardinal directions 0,2,4,6. Requires active episode.
 */
int julius_env_bridge_span(julius_env_t *env, int x, int y, int *direction);

/** Read active buildings as JSON for supply/service diagnostics; no time advance.
 * Returns -1 on invalid handle or insufficient buffer. Existing ABI unchanged.
 */
int julius_env_get_buildings(julius_env_t *env, char *output, int capacity);
int julius_env_get_food_supply(julius_env_t *env, char *output, int capacity);
int julius_env_get_population_info(julius_env_t *env, char *output, int capacity);
/** Read imperial personal finances and gift quotes, including after episode end. */
int julius_env_get_imperial_state(julius_env_t *env, char *output, int capacity);
int julius_env_get_water_supply(julius_env_t *env, char *output, int capacity);
int julius_env_get_housing_state(julius_env_t *env, char *output, int capacity);
/** Read cached finance accounting and current coverage, including after episode end.
 * Monthly tax bases are raw units, not actual income at the current tax rate.
 */
int julius_env_get_finance_state(julius_env_t *env, char *output, int capacity);

/**
 * Capture the current environment state.
 *
 * Snapshots are valid only for the environment that created them. Call
 * julius_env_snapshot_destroy() when the snapshot is no longer needed.
 *
 * @param env Environment handle
 * @return Snapshot handle, or NULL on error
 */
julius_snapshot_t *julius_env_snapshot_create(julius_env_t *env);

/**
 * Restore a previously captured environment state.
 * @param env Environment handle that created the snapshot
 * @param snapshot Snapshot handle
 * @return 0 on success, -1 on error
 */
int julius_env_snapshot_restore(julius_env_t *env, const julius_snapshot_t *snapshot);

/**
 * Destroy a snapshot and remove its private temporary save file.
 * @param snapshot Snapshot handle (may be NULL)
 */
void julius_env_snapshot_destroy(julius_snapshot_t *snapshot);

/**
 * Execute one step in the environment
 * @param env Environment handle
 * @param action Action to execute
 * @param result Output: step result
 * @return 0 on success, -1 on error
 */
int julius_env_step(julius_env_t *env, const gymnasium_action_t *action, julius_env_step_result_t *result);

/**
 * Get current observation without advancing time
 * @param env Environment handle
 * @param observation Output: current observation
 * @return 0 on success, -1 on error
 */
int julius_env_get_observation(julius_env_t *env, gymnasium_observation_t *observation);

/** Opaque state identity. Advances on reset/step; snapshots restore their identity.
 * The issuance counter is not restored, so divergent branches never share IDs.
 */
uint64_t julius_env_get_state_token(julius_env_t *env);
/** Export a persistent standard save, including after termination/truncation.
 * Caller supplies an absolute filename. Does not advance the simulation.
 */
int julius_env_export_save(julius_env_t *env, const char *filename);
/** -1 lost, 0 ongoing, 1 won; -2 invalid handle. */
int julius_env_get_victory_state(julius_env_t *env);

/**
 * Get last error message
 * @param env Environment handle
 * @return Error message string, or NULL if no error
 */
const char *julius_env_get_error(julius_env_t *env);

/**
 * Check if environment is initialized
 * @param env Environment handle
 * @return 1 if initialized, 0 otherwise
 */
int julius_env_is_initialized(julius_env_t *env);

/**
 * Get map data for rendering
 * @param env Environment handle
 * @param terrain_data Output: 162x162 array of terrain flags (must be pre-allocated)
 * @param building_data Output: 162x162 array of building IDs (must be pre-allocated)
 * @param width Output: actual map width
 * @param height Output: actual map height
 * @return 0 on success, -1 on error
 */
int julius_env_get_map_data(julius_env_t *env, uint16_t *terrain_data,
                             uint16_t *building_data, int *width, int *height);

#ifdef __cplusplus
}
#endif

#endif // GYMNASIUM_GYMNASIUM_H
