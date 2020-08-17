#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "annealing/annealing_api.h"
#include "annealing/gsl_siman.h"


int inc_counter = 0;
int increment_one(void){
    // returns 1 then 2 then 3....
    inc_counter++;
    return inc_counter;
}


int return_one(void){
    return 1;
}


int global_int = 0;
int return_global_int(void){
    return global_int;
}


int (*get_zeroed_xp(void))[ANNEAL_DIM]{
    // Don't forget to free it once you're done
    int (*xp)[ANNEAL_DIM] = (int(*)[ANNEAL_DIM])calloc(ANNEAL_DIM * ANNEAL_DIM, sizeof(int));
    for (int x = 0; x < ANNEAL_DIM; x++){
        for (int y = 0; y < ANNEAL_DIM; y++){
            xp[x][y] = 0;
        }
    }
    return xp;
}


void test_api_modify_elements_r1(void){
    printf("test_api_modify_elements_r\n");
    
    int (*xp)[ANNEAL_DIM] = get_zeroed_xp();
    
    api_modify_elements_r(xp, 1, return_one, return_one);
    
    for (int x = 0; x < ANNEAL_DIM; x++){
        for (int y = 0; y < ANNEAL_DIM; y++){
            if (x == 0 && y == 1) {
                assert(xp[x][y] == 1);
            } else {
                assert(xp[x][y] == 0);
            }
            xp[x][y] = 0;
        }
    }
    free(xp);
}


void test_api_modify_elements_r2(void){
    printf("test_api_modify_elements_r\n");
    
    // ToDo srand() with the time
    
    int (*xp)[ANNEAL_DIM] = get_zeroed_xp();
    
    api_modify_elements_r(xp, 1, rand, rand);
    
    for (int x = 0; x < ANNEAL_DIM; x++){
        for (int y = 0; y < ANNEAL_DIM; y++){
            int building_size = xp[x][y];
            assert(building_size <= ANNEAL_DIM - y);
            y += building_size;
        }
    }
    free(xp);
}


int main(void) {
    test_api_modify_elements_r1();
}


// mock widget functions
typedef int map_tile;
void build_start(const map_tile *tile)
{
    return;
}


//static 
void build_move(const map_tile *tile)
{
    return;
}


//static 
void build_end(void)
{
    return;
}