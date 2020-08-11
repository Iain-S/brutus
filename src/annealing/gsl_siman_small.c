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
#include "annealing/gsl_siman_small.h"
#include "input/mouse.h"
#include "platform/keyboard_input.h"
#include "graphics/window.h"
#include "sound/city.h"
#include "game/settings.h"
#include "window/city.h"

/* set up parameters for this simulated annealing run */

/* how many points do we try before stepping */
#define N_TRIES 3 //200

/* how many iterations for each T? */
#define ITERS_FIXED_T 3  //1000

/* max step size in random walk */
#define STEP_SIZE 9

/* Boltzmann constant */
#define K 1.0

/* initial temperature */
#define T_INITIAL 0.008

/* damping factor for temperature */
#define MU_T 1.09
//#define T_MIN 2.0e-4
#define T_MIN 2.0e-3

/* These control a run of gsl_siman_solve(). */
gsl_siman_params_t params
  = {N_TRIES, ITERS_FIXED_T, STEP_SIZE,
     K, T_INITIAL, MU_T, T_MIN};

#define INTPTR(d) (*(int*)(d))

enum {
    USER_EVENT_QUIT,
    USER_EVENT_RESIZE,
    USER_EVENT_FULLSCREEN,
    USER_EVENT_WINDOWED,
    USER_EVENT_CENTER_WINDOW,
};

static void anneal_run(void){
    time_set_millis(SDL_GetTicks());
    game_run();
}

static void anneal_draw(void){
    window_draw(1);
    platform_screen_render();
}

static void anneal_run_and_draw(void)
{
    anneal_run();
    anneal_draw();
}

static void anneal_handle_mouse_button(SDL_MouseButtonEvent *event, int is_down)
{
    mouse_set_position(event->x, event->y);
    if (event->button == SDL_BUTTON_LEFT) {
        mouse_set_left_down(is_down);
    } else if (event->button == SDL_BUTTON_RIGHT) {
        mouse_set_right_down(is_down);
    }
}

static void anneal_handle_window_event(SDL_WindowEvent *event, int *window_active){
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
            SDL_Log("Window move to coordinates x: %d y: %d\n", (int) event->data1, (int) event->data2);
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

static void anneal_handle_event(SDL_Event *event, int *active, int *quit)
{
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
                mouse_set_scroll(event->wheel.y > 0 ? SCROLL_UP : event->wheel.y < 0 ? SCROLL_DOWN : SCROLL_NONE);
            }
            break;

        case SDL_USEREVENT:
            if (event->user.code == USER_EVENT_QUIT) {
                *quit = 1;
            } else if (event->user.code == USER_EVENT_RESIZE) {
                platform_screen_set_window_size(INTPTR(event->user.data1), INTPTR(event->user.data2));
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

/* This function type should return the energy of a 
 * configuration xp */
double E1(void *xp)
{
    // load game
    assert(1 == game_file_load_saved_game("S1 01.sav"));

    api_build_buildings(xp);

    int first_day = game_time_total_days();
    int active = 1;
    int quit = 0;
    
    
    // run for just long enough for fires to happen
    while(game_time_total_days() - first_day < 90){
        SDL_Event event;
        
        while (SDL_PollEvent(&event)) {   
            anneal_handle_event(&event, &active, &quit);
        }
        
        if (active) {
            anneal_run_and_draw();
        } else {
            SDL_WaitEvent(NULL);
        }
    
    }
    int total_prosperity = api_score_random_3_by_3();
//    SDL_Log("total prosperity: %d", total_prosperity);      
    return 1000 - total_prosperity;
}

/* This function should return the distance between two 
 configurations, xp and yp. */
double M1(void *xp, void *yp)
{
    int distance = 0;
    int (*x_squares)[ANNEAL_DIM] = (int(*)[ANNEAL_DIM])xp;
    int (*y_squares)[ANNEAL_DIM] = (int(*)[ANNEAL_DIM])yp;
    
    // for now, just add the number of different squares
    for (int x = 0; x < 3; x++){
        for (int y = 0; y < 3; y++){
            if(x_squares[x][y] != y_squares[x][y]){
                distance++;
            }
        }
    }
    
    return distance;
}

/* This function should modify the xp, using a random
 step taken from the generator, r, up to a max distance of 
 step size. */
void S1(const gsl_rng* r, void *xp, double step_size)
{
    int (*old_xp)[ANNEAL_DIM] = (int(*)[ANNEAL_DIM])xp;
//    SDL_Log("step size: %f", step_size);
    
    // This function returns a random integer from 0 to n-1
    int i = gsl_rng_uniform_int(r, step_size);
//    SDL_Log("i: %d", i);
    
    api_modify_elements(old_xp, i);
}

/* This function should print the content of the 
 * configuration, xp. */
void P1(void *xp)
{
    // Don't print anything because the annealing table
    // is nice as it is
}

int
gsl_siman_main(void)
{    
    const gsl_rng_type * T;
    gsl_rng * r;

    // initialise with empty land
    int (*xp_initial)[ANNEAL_DIM] = (int(*)[ANNEAL_DIM])calloc(ANNEAL_DIM * ANNEAL_DIM, sizeof(int));//{{{0, 0, 0}, {0, 0, 0}, {0, 0, 0}};

    gsl_rng_env_setup();
    srand(time(NULL));

    T = gsl_rng_default;
    r = gsl_rng_alloc(T);

//    game_file_load_saved_game("S1 01.sav");
    SDL_Log("showing window");
    window_city_show();
    setting_reset_speeds(10000, setting_scroll_speed());

    
    SDL_Log("Annealing started");
    gsl_siman_solve(r, xp_initial, E1, S1, M1, P1,
                    NULL, NULL, NULL,
                    sizeof(int) * 9, params);
   
    SDL_Log("Annealing finished");
    
    // Now that gsl_simal_solve is done, xp_inital contains
    // the best solution so we run E1 once more to find out what it is
    int best_prosperity = 1000 - E1(xp_initial);
    SDL_Log("best prosperity: %d", best_prosperity);
    
    // Write the best solution to the log in case we can't see it on
    // the screen
    int (*squares)[ANNEAL_DIM] = (int(*)[ANNEAL_DIM])xp_initial;
    for (int y = 0; y < 3; y++){
        SDL_Log("%d %d %d", squares[0][y], squares[1][y], squares[2][y]);

    }
    
    // Explain what the numbers mean
    for (int i = 0; i < 6 ; i++){
        SDL_Log("%d = %s", i, api_get_building_name(i));
    }
    
    // Clean up
    gsl_rng_free(r);

    // Set the game speed to 0 so that nothing changes from now on
    setting_reset_speeds(0, setting_scroll_speed());
    
    // Save and load because it refreshes the window nicely
//    game_file_write_saved_game("S1 01 annealed.sav");
//    game_file_load_saved_game("S1 01 annealed.sav");

    return 0;
}