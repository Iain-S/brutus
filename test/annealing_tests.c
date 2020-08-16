#include <stdio.h>
#include <assert.h>
#include "annealing/annealing_api.h"

int main(void) {
    printf("api_test_func(8) == 16\n");
    assert(api_test_func(8) == 16);

}

typedef int map_tile;

// mock widget functions
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