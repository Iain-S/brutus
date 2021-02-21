// Search for optimal housing blocks using GSL simulated annealing library
#include "SDL.h"

#include <math.h>
#include <time.h>
#include <stdlib.h>
#include <string.h>
#include <gsl/gsl_siman.h>
#include <unistd.h>
#include <assert.h>

#include "core/time.h"
#include "game/file.h"
#include "game/game.h"
#include "game/time.h"
#include "platform/screen.h"
#include "annealing/annealing_api.h"
#include "annealing/gsl_siman.h"
#include "input/mouse.h"
#include "platform/keyboard_input.h"
#include "graphics/window.h"
#include "sound/city.h"
#include "game/settings.h"
#include "game/resource.h"
#include "game/state.h"
#include "graphics/video.h"
#include "window/city.h"
#include "building/granary.h"
#include "building/warehouse.h"
#include "building/construction_clear.h"
#include "city/finance.h"
#include "map/terrain.h"
#include "map/tiles.h"
#include "map/property.h"

// Set up parameters for this simulated annealing run

// How many points do we try before stepping
#define N_TRIES 200

// ToDo - Why doesn't changing this seem to affect the run time?
// How many iterations for each T?
#define ITERS_FIXED_T 700  // GSL example:1000

// ToDo does this need to be related to ANNEAL_DIM?
// Max step size in random walk
#define STEP_SIZE 40

// Boltzmann constant
#define K 1.0

// Initial temperature
#define T_INITIAL 0.118  // use 0.008 for quicker anneal

// Damping factor for temperature
#define MU_T 1.09

// Final temperature
#define T_MIN 2.0e-6  // use e-3 for quicker anneal

int ANNEAL_X_DIM;
int ANNEAL_Y_DIM;
int ANNEAL_X_OFFSET;
int ANNEAL_Y_OFFSET;

#define INTPTR(d) (*(int*)(d))

enum {
    USER_EVENT_QUIT,
    USER_EVENT_RESIZE,
    USER_EVENT_FULLSCREEN,
    USER_EVENT_WINDOWED,
    USER_EVENT_CENTER_WINDOW,
};

static void anneal_run(void) {
    // Simplified version of run() from julius.c
    time_set_millis(SDL_GetTicks());
    game_run();
}

static void anneal_draw(void) {
    // Simplified version of draw() from julius.c
    window_draw(1);
    platform_screen_render();
}

static void anneal_run_and_draw(void) {
    // Simplified version of run_and_draw() from julius.c
    anneal_run();
    anneal_draw();
}

static void anneal_handle_mouse_button(SDL_MouseButtonEvent *event, int is_down) {
    // Simplified version of handle_mouse_button() from julius.c
    mouse_set_position(event->x, event->y);
    if (event->button == SDL_BUTTON_LEFT) {
        mouse_set_left_down(is_down);
    } else if (event->button == SDL_BUTTON_RIGHT) {
        mouse_set_right_down(is_down);
    }
}

static void anneal_handle_window_event(SDL_WindowEvent *event, int *window_active) {
    // Simplified version of handle_window_event() from julius.c
    switch (event->event) {
        case SDL_WINDOWEVENT_ENTER:
            mouse_set_inside_window(1);
            break;
        case SDL_WINDOWEVENT_LEAVE:
            mouse_set_inside_window(0);
            break;
        case SDL_WINDOWEVENT_SIZE_CHANGED:
            SDL_Log("Window resized to %d x %d", (int) event->data1, (int) event->data2);
            platform_screen_resize(event->data1, event->data2);
            break;
        case SDL_WINDOWEVENT_RESIZED:
            SDL_Log("System resize to %d x %d", (int) event->data1, (int) event->data2);
            break;
        case SDL_WINDOWEVENT_MOVED:
            SDL_Log("Window move to coordinates x: %d y: %d\n",
                    (int) event->data1, (int) event->data2);
            platform_screen_move(event->data1, event->data2);
            break;
        case SDL_WINDOWEVENT_SHOWN:
            SDL_Log("Window %d shown", (unsigned int) event->windowID);
            *window_active = 1;
            break;
        case SDL_WINDOWEVENT_HIDDEN:
            SDL_Log("Window %d hidden", (unsigned int) event->windowID);
            *window_active = 0;
            break;
    }
}

static void anneal_handle_event(SDL_Event *event, int *active, int *quit) {
    // Simplified version of handle_event() from julius.c
    switch (event->type) {
        case SDL_WINDOWEVENT:
            anneal_handle_window_event(&event->window, active);
            break;
        case SDL_KEYDOWN:
            platform_handle_key_down(&event->key);
            break;
        case SDL_TEXTINPUT:
            platform_handle_text(&event->text);
            break;
        case SDL_MOUSEMOTION:
            if (event->motion.which != SDL_TOUCH_MOUSEID) {
                mouse_set_position(event->motion.x, event->motion.y);
            }
            break;
        case SDL_MOUSEBUTTONDOWN:
            if (event->button.which != SDL_TOUCH_MOUSEID) {
                anneal_handle_mouse_button(&event->button, 1);
            }
            break;
        case SDL_MOUSEBUTTONUP:
            if (event->button.which != SDL_TOUCH_MOUSEID) {
                anneal_handle_mouse_button(&event->button, 0);
            }
            break;
        case SDL_MOUSEWHEEL:
            if (event->wheel.which != SDL_TOUCH_MOUSEID) {
                mouse_set_scroll(event->wheel.y > 0
                                 ? SCROLL_UP : event->wheel.y < 0
                                 ? SCROLL_DOWN : SCROLL_NONE);
            }
            break;

        case SDL_QUIT:
            *quit = 1;
            break;

        case SDL_USEREVENT:
            if (event->user.code == USER_EVENT_QUIT) {
                *quit = 1;
            } else if (event->user.code == USER_EVENT_RESIZE) {
                platform_screen_set_window_size(INTPTR(event->user.data1),
                                                INTPTR(event->user.data2));
            } else if (event->user.code == USER_EVENT_FULLSCREEN) {
                platform_screen_set_fullscreen();
            } else if (event->user.code == USER_EVENT_WINDOWED) {
                platform_screen_set_windowed();
            } else if (event->user.code == USER_EVENT_CENTER_WINDOW) {
                platform_screen_center_window();
            }
            break;

        default:
            break;
    }
}

void gsl_provision_city(void) {
    // Give the city lots of food, goods and money
    // ToDo Move this to the API file

    for (int i = 1; i < MAX_BUILDINGS; i++) {
        building *b = building_get(i);
        if (b->type == BUILDING_GRANARY) {
            for (int x = 0; x < 20; x++) {
                // Add all food types needed by palaces
                building_granary_add_resource(b, RESOURCE_WHEAT, 0);
                building_granary_add_resource(b, RESOURCE_VEGETABLES, 0);
                building_granary_add_resource(b, RESOURCE_FRUIT, 0);
                building_granary_add_resource(b, RESOURCE_MEAT, 0);
            }
        } else if (b->type == BUILDING_WAREHOUSE) {
            for (int x = 0; x < 20; x++) {
                // Add all resource types needed by palaces
                building_warehouse_add_resource(b, RESOURCE_POTTERY);
                building_warehouse_add_resource(b, RESOURCE_FURNITURE);
                building_warehouse_add_resource(b, RESOURCE_OIL);
                building_warehouse_add_resource(b, RESOURCE_WINE);
                building_warehouse_add_resource(b, RESOURCE_MARBLE);
            }
        }
    }

    // Fill the treasury
    city_finance_process_donation(10000);
}

static void gsl_teardown(void) {
    // Close resources prior to exit
    SDL_Log("Exiting game");
    video_shutdown();
    platform_screen_destroy();
}

void gsl_print_xp(void* xp) {
    // Print the configuration to stdout (useful for debugging)

    ab(*squares)[ANNEAL_Y_DIM] = (ab(*)[ANNEAL_Y_DIM])xp;

    // ToDo Resize this as needed
    char output[500];

    for (int x = 0; x < ANNEAL_X_DIM; x++) {
        int offset = 0;
        for (int y = 0; y < ANNEAL_Y_DIM; y++) {
            // ToDo We should pad these numbers to 2-3 places like 023 or 03
            offset += snprintf(output + offset,
                               500 - offset,
                               "%d ",
                               api_get_type_from_index(squares[x][y].building_index));
        }
        SDL_Log(output);
    }
}

double E1(void *xp) {
    // This function type should return the energy of a configuration xp

    assert(1 == game_file_load_saved_game("annealing.sav"));

    gsl_print_xp(xp);

    api_build_buildings(xp);

    int first_day = game_time_total_days();
    int active = 1;
    int quit = 0;

    // To give some indication of how long each iteration takes
    time_t rawtime;
    struct tm * timeinfo;
    time(&rawtime);
    timeinfo = localtime(&rawtime);

    int deleted = 0;
    int placed = 0;

    // Run for just long enough for fire and collapse to happen
    while (game_time_total_days() - first_day < 300) {
        // Delete whatever is in the area...
        if (deleted == 0) {
            deleted = 1;
            SDL_Log("day 1: %s", asctime(timeinfo));

            building_construction_clear_land(0,
                                             ANNEAL_X_OFFSET,
                                             ANNEAL_Y_OFFSET,
                                             ANNEAL_X_OFFSET + ANNEAL_X_DIM,
                                             ANNEAL_Y_OFFSET + ANNEAL_Y_DIM);
        }
        // Busy-wait until everything has dissapeared (including inhabitants)
        if (deleted == 1 && placed == 0) {
            int all_clear = 1;  // TRUE

            for (int x = 0; x < ANNEAL_X_DIM; x++) {
                for (int y = 0; y < ANNEAL_Y_DIM; y++) {
                int xx = x + ANNEAL_X_OFFSET;
                int yy = y + ANNEAL_Y_OFFSET;
                    // ToDo Check that we can still anneal in meadows.
                    if (!map_tiles_are_clear(xx, yy, 1, TERRAIN_ALL)) {
                        all_clear = 0;
                    }
                }
            }

            if (all_clear == 1) {
                placed = 1;
                SDL_Log("day 2");
                api_build_buildings(xp);
            }
        }

        SDL_Event event;

        while (SDL_PollEvent(&event)) {
            anneal_handle_event(&event, &active, &quit);

            if (quit == 1) {
                gsl_teardown();
                exit(0);
            }
        }

        if (active) {
            anneal_run_and_draw();
        } else {
            SDL_WaitEvent(NULL);
        }
    }
    int total_prosperity = api_score_city(ANNEAL_X_OFFSET,
                                          ANNEAL_Y_OFFSET,
                                          ANNEAL_X_OFFSET + ANNEAL_X_DIM,
                                          ANNEAL_Y_OFFSET + ANNEAL_Y_DIM);
    //    SDL_Log("total prosperity: %d", total_prosperity);
    return 1000 - total_prosperity;
}

double M1(void *xp, void *yp) {
    // Return the "distance" between two configurations, xp and yp
    int distance = 0;
    ab(*a_squares)[ANNEAL_Y_DIM] = (ab(*)[ANNEAL_Y_DIM])xp;
    ab(*b_squares)[ANNEAL_Y_DIM] = (ab(*)[ANNEAL_Y_DIM])yp;

    // For now, just add the number of different squares
    for (int x = 0; x < ANNEAL_X_DIM; x++) {
        for (int y = 0; y < ANNEAL_Y_DIM; y++) {
            if (a_squares[x][y].building_index != b_squares[x][y].building_index) {
                distance++;
            }
        }
    }

    return distance;
}

void S1(const gsl_rng* r, void *xp, double step_size) {
    // Modify xp using a random step taken from the generator up to a maximum
    // distance of step_size
    ab(*old_xp)[ANNEAL_Y_DIM] = (ab(*)[ANNEAL_Y_DIM])xp;

    //    SDL_Log("step size: %f", step_size);

    // This function returns a random integer from 0 to n-1
    int i = gsl_rng_uniform_int(r, step_size);
    //    SDL_Log("i: %d", i);

    api_modify_elements(old_xp, i);
}

void P1(void *xp) {
    // Don't print anything because the annealing table is nice as it is
}

void initialise_xp(void* xp) {
    // Get our initial configuration by checking what is already in the annealing area
    ab(*xp_initial)[ANNEAL_Y_DIM] = (ab(*)[ANNEAL_Y_DIM])xp;

    // Initialise with empty land
    for (int x = 0; x < ANNEAL_X_DIM; x++) {
        for (int y = 0; y < ANNEAL_Y_DIM; y++) {
            xp_initial[x][y].building_index = 0;
            xp_initial[x][y].uid = global_building_uid_counter;
            global_building_uid_counter++;
        }
    }

    // Add any existing buildings

    int highest_id = building_get_highest_id();

    // There always seems to be an empty building in the 0th element of
    // the master buildings array!
    int unused_or_deleted;
    for (int i = 1; i <= highest_id; i++) {
        building* b = building_get(i);

        // ToDo There seems to be a short (few seconds) lag between building a
        //      building and it being recognised.  Not sure if it's an issue in practice.
        if ((int) b->state > BUILDING_STATE_UNUSED
            && (int) b->state < BUILDING_STATE_DELETED_BY_GAME) {
            if (b->x >= ANNEAL_X_OFFSET && b->x < ANNEAL_X_OFFSET + ANNEAL_X_DIM &&
                b->y >= ANNEAL_Y_OFFSET && b->y < ANNEAL_Y_OFFSET + ANNEAL_Y_DIM) {
                api_replace_building(xp,
                                     b->x - ANNEAL_X_OFFSET,
                                     b->y - ANNEAL_Y_OFFSET,
                                     api_get_index_from_type(b->type));
            }
        } else {
            // ToDo Put a breakpoint here and see if we hit it
            unused_or_deleted++;
        }
    }

    // Roads and gardens get handled separately as they do not appear in the all_buildings array
    for (int x = 0; x < ANNEAL_X_DIM; x++) {
        for (int y = 0; y < ANNEAL_Y_DIM; y++) {
            int yy = ANNEAL_Y_OFFSET + y;
            int xx = ANNEAL_X_OFFSET + x;
            if (map_terrain_exists_tile_in_area_with_type(xx, yy, 1, TERRAIN_ROAD)) {
                api_replace_building(xp, x, y, api_get_index_from_type(BUILDING_ROAD));

            } else if (map_terrain_exists_tile_in_area_with_type(xx, yy, 1, TERRAIN_GARDEN)) {
                api_replace_building(xp, x, y, api_get_index_from_type(BUILDING_GARDENS));
            }
            // ToDo We may need to do this for aquaducts too
        }
    }

    return;
}

int gsl_siman_main(int x_start, int y_start, int x_end, int y_end) {
    // Start the simulated annealing
    const gsl_rng_type * T;
    gsl_rng * r;

    ANNEAL_X_DIM = x_end - x_start;
    ANNEAL_Y_DIM = y_end - y_start;

    // ToDo We've assumed that the cursor is being dragged top to bottom and
    //      left to right but we should handle the other possibilities too
    assert(ANNEAL_X_DIM >= 1);
    assert(ANNEAL_Y_DIM >= 1);

    ANNEAL_X_OFFSET = x_start;
    ANNEAL_Y_OFFSET = y_start;

    ab(*xp_initial)[ANNEAL_Y_DIM] = (ab(*)[ANNEAL_Y_DIM])calloc(ANNEAL_Y_DIM * ANNEAL_X_DIM,
                                                                sizeof (ab));

    initialise_xp(xp_initial);

    gsl_rng_env_setup();
    srand(time(NULL));

    T = gsl_rng_default;
    r = gsl_rng_alloc(T);

    window_city_show();

    int original_speed = setting_game_speed();

    // Higher speeds do not actually run any quicker
    setting_reset_speeds(100000, setting_scroll_speed());

    assert(1 == game_file_write_saved_game("annealing.sav"));
    SDL_Log("Annealing started");

    // These control a run of gsl_siman_solve()
    gsl_siman_params_t params
        = {N_TRIES, ITERS_FIXED_T, STEP_SIZE,
        K, T_INITIAL, MU_T, T_MIN};


    gsl_siman_solve(r, xp_initial, E1, S1, M1, P1,
        NULL, NULL, NULL,
        sizeof (ab) * ANNEAL_Y_DIM * ANNEAL_X_DIM, params);

    SDL_Log("Annealing finished");

    // Now that gsl_simal_solve is done, xp_initial contains
    // the best solution so we run E1 once more to find out what it is
    int best_prosperity = 1000 - E1(xp_initial);
    SDL_Log("best prosperity: %d", best_prosperity);

    // Write the best solution to the log in case we can't see it on
    // the screen
    ab(*squares)[ANNEAL_Y_DIM] = (ab(*)[ANNEAL_Y_DIM])xp_initial;

    gsl_print_xp(xp_initial);

    // ToDo Explain what the numbers mean

    // Clean up
    gsl_rng_free(r);

    // Set the game speed back to normal
    setting_reset_speeds(original_speed, setting_scroll_speed());

    // Pause so that nothing changes from now on
    game_state_unpause();
    game_state_toggle_paused();

    return 0;
}
