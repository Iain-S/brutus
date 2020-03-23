#include "SDL.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <gsl/gsl_siman.h>

#include "core/time.h"
#include "game/file.h"
#include "game/game.h"
#include "game/time.h"
#include "platform/screen.h"
#include "annealing/annealing_api.h"

/* set up parameters for this simulated annealing run */

/* how many points do we try before stepping */
#define N_TRIES 200

/* how many iterations for each T? */
#define ITERS_FIXED_T 1000

/* max step size in random walk */
#define STEP_SIZE 1.0

/* Boltzmann constant */
#define K 1.0

/* initial temperature */
#define T_INITIAL 0.008

/* damping factor for temperature */
#define MU_T 1.003
#define T_MIN 2.0e-6

/* These control a run of gsl_siman_solve(). */
gsl_siman_params_t params
  = {N_TRIES, ITERS_FIXED_T, STEP_SIZE,
     K, T_INITIAL, MU_T, T_MIN};

static void anneal_run_and_draw(void)
{
    time_set_millis(SDL_GetTicks());

    game_run();
    game_draw();

    platform_screen_render();
}

/* This function type should return the energy of a 
 * configuration xp */
double E1(void *xp)
{
    // load game
    game_file_load_saved_game("S1 01.sav");
    
    api_build_buildings(xp);
    
    int today = game_time_total_days();
    
    // run for some days
    while(game_time_total_days() - today < 90){
        anneal_run_and_draw();
    }
           
    int total_prosperity = api_score_random_3_by_3();
    return 1000 - total_prosperity;
}

/* This function should return the distance between two 
 configurations, xp and yp. */
double M1(void *xp, void *yp)
{
    int distance = 0;
    int** x_squares = (int**)xp;
    int** y_squares = (int**)yp;
    
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
    int** old_xp = (int**)xp;
    int** new_xp = (int**)calloc(sizeof(old_xp)/sizeof(old_xp[0]), 
                                 sizeof(old_xp[0]));
    
    for (int i = 0; i < sizeof(old_xp); i++){
        new_xp[i] = (int*)calloc(sizeof(old_xp[0])/sizeof(old_xp[0][0]), 
                                 sizeof(old_xp[0][0]));
        memcpy(new_xp[i], old_xp[i], sizeof(old_xp[0]));
    }
    
    // do a test
    for (int x = 0; x < 3; x++){
        for (int y = 0; y < 3; y++){
            if (old_xp[x][y] != new_xp[x][y]){
                printf("error at %d %d, %d is not equal to %d", 
                        x, y, old_xp[x][y], new_xp[x][y]);
            }
        }
    }
    
    // This function returns a random integer from 0 to n-1
    int i = gsl_rng_uniform_int(r, step_size);
    
    // Change up to r elements of new_xp
    api_modify_elements(new_xp, i);
    return new_xp;
}

/* This function should print the content of the 
 * configuration, xp. */
void P1(void *xp)
{
    int** squares = (int**)xp;
    for (int y = 0; y < 3; y++){
        printf("%d %d %d", squares[0][y], squares[1][y], squares[2][y]);
    }
}

int
gsl_siman_main(void)
{
  const gsl_rng_type * T;
  gsl_rng * r;

  // initialise with empty land
  int** xp_initial = {{0, 0, 0}, {0, 0, 0}, {0, 0, 0}};
  
  gsl_rng_env_setup();

  T = gsl_rng_default;
  r = gsl_rng_alloc(T);

  gsl_siman_solve(r, &xp_initial, E1, S1, M1, P1,
                  NULL, NULL, NULL,
                  sizeof(xp_initial), params);

  gsl_rng_free (r);
  return 0;
}