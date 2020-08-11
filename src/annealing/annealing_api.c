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
#include "gsl_siman_small.h"
#include "annealing/annealing_api.h"
#include "widget/city.h"



void api_place_house(int x, int y){
    int placed = place_houses(0, x, y, x, y);
    assert(placed == 1);
}


void api_place_road(int x, int y){
//    int placed = building_construction_place_road(0, x, y, x, y);
//    assert(placed == 1);
    building_construction_set_type(BUILDING_ROAD);
    map_tile tile;
    tile.x = x;
    tile.y = y;
    build_start(&tile);
    build_move(&tile);
    build_end();
}


void api_place_engineer(int x, int y){
//    int placed = building_construction_place_building(BUILDING_ENGINEERS_POST, x, y);
//    assert(placed == 1);
}


void api_place_prefecture(int x, int y){
    int placed = building_construction_place_building(BUILDING_PREFECTURE, x, y);
    assert(placed == 1);
    
}


void api_place_nothing(int x, int y){
    // pass
}

void api_place_well(int x, int y){
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

//void build_buildings(void* xp){
//    return;
//}

// These are our choice of buildings
typedef void (*place_building_func)(int, int);  
place_building_func place_building_funcs[6] = {
    &api_place_nothing,
    &api_place_house, 
    &api_place_road, 
//    &api_place_engineer, 
    &api_place_prefecture,
    &api_place_garden,
    &api_place_well
}; 

char* place_building_names[6] = {
    "empty land",
    "house",
    "road",
//    "engineer's post",
    "prefecture",
    "garden",
    "well"
};

char* api_get_building_name(int i){
    return place_building_names[i];
}

//void api_init_random_3_by_3(){
//
//    
////    place_building_func* buildings_placed = (place_building_func*) calloc(9 * 
////            sizeof(place_building_func));
//    
//    // For each tile in our 3 x 3, place a building
//    for(int x=0; x < 3; x++){
//        for(int y=0; y < 3; y++){
//            int random_index = rand() % (sizeof(place_building_names) / sizeof(place_building_names[0]));
//            place_building_funcs[random_index](x + 7, y + 7);
////            buildings_placed[x * 3 + y] = place_building_funcs[random_index];
//        }
//    } 
////    return buildings_placed;
//};

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


void api_build_buildings(void* xp){
//    int squares[ANNEAL_DIM][ANNEAL_DIM] = (int[ANNEAL_DIM][ANNEAL_DIM]) xp;
    map_property_clear_constructing_and_deleted();
    int (*squares)[ANNEAL_DIM] = (int(*)[ANNEAL_DIM])xp;
    for (int x = 0; x < 3; x++){
        for (int y = 0; y < 3; y++){
            place_building_funcs[squares[x][y]](x + 7, y + 7);
        }
    }
}


void api_change_a_square(){
    // Change one square of our housing block
    return;   
}

void api_modify_elements(void* xp, int num_elements){
    // Modify up to num_elements of xp, in place
    int (*squares)[ANNEAL_DIM] = (int(*)[ANNEAL_DIM])xp;
    //int number_of_squares = (sizeof(squares)/sizeof(squares[0])) * (sizeof(squares[0]) / sizeof(squares[0][0]));
    
    for(int i = 0; i < num_elements; i++){
        int square_index = rand() % 9;
        int x = square_index / 3;
        int y = square_index % 3;
        
        int new_building_type = rand() % (sizeof(place_building_funcs) / sizeof(place_building_funcs[0]));
        squares[x][y] = new_building_type;
    } 
    return;
}