#include <stdlib.h>
#include <assert.h>

#include "annealing_api.h"
#include "building/construction.h"
#include "building/construction_routed.h"
#include "building/construction_building.h"
#include "building/type.h"
#include "building/building.h"
#include "building/model.h"


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

void api_init_random_3_by_3(){
    // These are our choice of buildings
    typedef void (*place_building_func)(int, int);  
    place_building_func place_building_funcs[5] = {
        &api_place_house, 
        &api_place_road, 
        &api_place_engineer, 
        &api_place_prefecture,
        &api_place_nothing
    }; 
    
//    place_building_func* buildings_placed = (place_building_func*) calloc(9 * 
//            sizeof(place_building_func));
    
    // For each tile in our 3 x 3, place a building
    for(int x=0; x < 3; x++){
        for(int y=0; y < 3; y++){
            int random_index = rand() % 5;
            place_building_funcs[random_index](x + 7, y + 7);
//            buildings_placed[x * 3 + y] = place_building_funcs[random_index];
        }
    } 
//    return buildings_placed;
};

int api_score_random_3_by_3(){
    // The same as ratings.calculate_max_prosperity but we take the total
    // prosperity, not the average per house
    
    int points = 0;
    for (int i = 1; i < MAX_BUILDINGS; i++) {
        building *b = building_get(i);
        if (b->state && b->house_size) {
            points += model_get_house(b->subtype.house_level)->prosperity;
        }
    }
    return points;
}

void api_change_a_square(){
    // Change one square of our housing block
    return;   
}