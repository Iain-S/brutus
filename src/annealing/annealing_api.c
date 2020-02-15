#include <stdlib.h>
#include <assert.h>

#include "annealing_api.h"
#include "building/construction.h"
#include "building/construction_routed.h"
#include "building/construction_building.h"
#include "building/type.h"


void api_place_house(int x, int y){
    int placed = place_houses(0, x, y, x, y);
    assert(placed == 1);
}


void api_place_road(int x, int y){
    int placed = building_construction_place_road(0, x, y, x, y);
    assert(placed == 1);
}


void api_place_engineer(int x, int y){
    int placed = building_construction_place_building(BUILDING_ENGINEERS_POST, x, y);
    assert(placed == 1);
}


void api_place_prefecture(int x, int y){
    int placed = building_construction_place_building(BUILDING_PREFECTURE, x, y);
    assert(placed == 1);
}


void api_place_nothing(int x, int y){
    // pass
}

void api_place_random_3_by_3(){
    // These are our choice of buildings
    typedef void (*place_building_func)(int, int);  
    place_building_func place_building_funcs[5] = {
        &api_place_house, 
        &api_place_road, 
        &api_place_engineer, 
        &api_place_prefecture,
        &api_place_nothing
    }; 
    
    // For each tile in our 3 x 3, place a building
    for(int x=0; x < 3; x++){
        for(int y=0; y < 3; y++){
            int random_index = rand() % 5;
            place_building_funcs[random_index](x + 7, y + 7);
        }
    } 
};

