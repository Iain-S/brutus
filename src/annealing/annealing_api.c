#include <stdlib.h>
#include <assert.h>

#include "building/construction.h"
#include "building/construction_routed.h"
#include "building/construction_building.h"
#include "building/type.h"
#include "building/building.h"
#include "building/model.h"
#include "map/property.h"
#include "map/point.h"
#include "gsl_siman.h"
#include "annealing/annealing_api.h"
#include "widget/city.h"



void api_place_house(int x, int y){
    // Place a house at the tile given by x and y
    int placed = place_houses(0, x, y, x, y);
    assert(placed == 1);
}


void api_place_road(int x, int y){
    // Place a road at the tile given by x and y
    building_construction_set_type(BUILDING_ROAD);
    map_tile tile;
    tile.x = x;
    tile.y = y;
    build_start(&tile);
    build_move(&tile);
    build_end();
}


//void api_place_engineer(int x, int y){
//    int placed = building_construction_place_building(BUILDING_ENGINEERS_POST, x, y);
//    assert(placed == 1);
//}


void api_place_prefecture(int x, int y){
    // Place a prefecture at the tile given by x and y
    int placed = building_construction_place_building(BUILDING_PREFECTURE, x, y);
    assert(placed == 1);
    
}


void api_place_nothing(int x, int y){
    // By not placing anything, we leave empty grass
    // ToDo We should probably delete what was at x and y
    // pass
}


void api_place_well(int x, int y){
    // Place a well at the tile given by x and y
    int placed = building_construction_place_building(BUILDING_WELL, x, y);
    assert(placed == 1);
}


void api_place_garden(int x, int y){
//    int placed = place_garden(x, y, x, y); //building_construction_place_building(BUILDING_GARDENS, x, y);
//    assert(placed == 1);
//    data.start.x = x;
//    data.start.y = y;
//    data.end.x = x;
//    data.end.y = y;
//    data.type = BUILDING_GARDENS;
//    building_construction_place();
    building_construction_set_type(BUILDING_GARDENS);
    map_tile tile;
    tile.x = x;
    tile.y = y;
    build_start(&tile);
    build_move(&tile);
    build_end();
}


void api_place_market(int x, int y){
    // Place a market at the tile given by x and y
    building_construction_set_type(BUILDING_MARKET);
    map_tile tile;
    tile.x = x;
    tile.y = y;
    build_start(&tile);
    build_move(&tile);
    build_end();
}


typedef void (*place_building_func)(int, int);  
place_building_func place_building_funcs[7] = {
// These are our choice of buildings
    &api_place_nothing,
    &api_place_house, 
    &api_place_road, 
//    &api_place_engineer, 
    &api_place_prefecture,
    &api_place_garden,
    &api_place_well,
    &api_place_market
}; 


char* place_building_names[7] = {
    "empty land",
    "house",
    "road",
//    "engineer's post",
    "prefecture",
    "garden",
    "well",
    "market"
};


int place_building_sizes[7] = {
// These must be sorted in ascending size
    1,
    1,
    1,
    1,
    1,
    1,
    4
};


char* api_get_building_name(int i){
    return place_building_names[i];
}


int api_score_city(){
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


void api_build_buildings(void* xp){
//    int squares[ANNEAL_DIM][ANNEAL_DIM] = (int[ANNEAL_DIM][ANNEAL_DIM]) xp;
    map_property_clear_constructing_and_deleted();
    int (*squares)[ANNEAL_DIM] = (int(*)[ANNEAL_DIM])xp;
    for (int x = 0; x < ANNEAL_DIM; x++){
        for (int y = 0; y < ANNEAL_DIM; y++){
            place_building_funcs[squares[x][y]](x + 7, y + 7);
        }
    }
}


void api_modify_elements(void* xp, int num_elements){
    // Modify up to num_elements of xp, in place
    int (*squares)[ANNEAL_DIM] = (int(*)[ANNEAL_DIM])xp;
    
    for(int i = 0; i < num_elements; i++){
        int square_index = rand() % (ANNEAL_DIM * ANNEAL_DIM);
        int x = square_index / ANNEAL_DIM;
        int y = square_index % ANNEAL_DIM;
        
//        int biggest_buildable_building = 
        
        int new_building_type = rand() % (sizeof(place_building_funcs) / sizeof(place_building_funcs[0]));
        squares[x][y] = new_building_type;
    } 
    return;
}


int api_test_func(int a) {
    return a * 2;
}