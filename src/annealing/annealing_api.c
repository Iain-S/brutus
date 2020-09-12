#include <stdlib.h>
#include <assert.h>
#include <stdio.h>

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

typedef void (*place_building_func)(int, int, building_type);

typedef struct {
    char* name;
    int size;
    building_type type;
} building_row;

//void api_place_engineer(int x, int y){
//    int placed = building_construction_place_building(BUILDING_ENGINEERS_POST, x, y);
//    assert(placed == 1);
//}

void api_place_building(int x, int y, building_type building_type) {
    int placed = 0;
    switch (building_type) {
        case BUILDING_NONE:
            break;
        case BUILDING_HOUSE_VACANT_LOT:
            placed = place_houses(0, x, y, x, y);
            assert(placed == 1);
            break;
        case BUILDING_PREFECTURE:
        case BUILDING_WELL:
        case BUILDING_ROAD:
        case BUILDING_MARKET:
        case BUILDING_GARDENS:
        case BUILDING_SCHOOL:
            building_construction_set_type(building_type);
            map_tile tile;
            tile.x = x;
            tile.y = y;
            tile.grid_offset = 1;
            build_start(&tile);
            build_move(&tile);
            build_end();
            // ToDo - Check that we could place the building
            break;
        default:
            printf("got - %d\n", building_type);
            //	    exit();
    }

}

building_row building_table[8] = {
    // These must be sorted in ascending size
    // and are the size in one dimension (i.e. width not area)
    {"empty land", 1, BUILDING_NONE},
    {"house", 1, BUILDING_HOUSE_VACANT_LOT},
    {"road", 1, BUILDING_ROAD},
    {"prefecture", 1, BUILDING_PREFECTURE},
    {"garden", 1, BUILDING_GARDENS},
    {"well", 1, BUILDING_WELL},
    {"market", 2, BUILDING_MARKET},
    {"school", 2, BUILDING_SCHOOL}
};

int global_building_uid_counter = 1;

char* api_get_building_name(int i) {
    return building_table[i].name;
}

int api_score_city() {
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

int already_built(int* built_uids, int max, int uid) {
    // does c have bool?
    for (int i = 0; i < max; i++) {
        if (built_uids[i] == uid) {
            return 1;
        }
    }
    return 0;
}

void api_build_buildings(void* xp) {
    map_property_clear_constructing_and_deleted();
    ab(*squares)[ANNEAL_Y_DIM] = (ab(*)[ANNEAL_Y_DIM])xp;

    int built_uids[ANNEAL_Y_DIM * ANNEAL_X_DIM];
    int uid_index = 0;

    for (int x = 0; x < ANNEAL_X_DIM; x++) {
        for (int y = 0; y < ANNEAL_Y_DIM; y++) {
            if (already_built(built_uids, uid_index, squares[x][y].uid)) {
                continue;
            } else {
                ab my_building = squares[x][y];
                api_place_building(ANNEAL_X_OFFSET + x, ANNEAL_Y_OFFSET + y, building_table[my_building.building_type].type);
                built_uids[uid_index] = my_building.uid;
                uid_index++;
            }
        }
    }
}

int api_max(uint a, uint b) {
    if (a >= b) {
        return a;
    } else {
        return b;
    }
}

int api_min(uint a, uint b) {
    if (a <= b) {
        return a;
    } else {
        return b;
    }
}

int api_get_biggest_building_index(int x, int y) {
    // Get the index of the largest building that can be built here

    // The size of the largest building we can put at x,y
    int biggest_y_dimension = ANNEAL_Y_DIM - y;
    int biggest_x_dimension = ANNEAL_X_DIM - x;
    //    int biggest_building_size = api_min(ANNEAL_Y_DIM, ANNEAL_X_DIM) - api_max(x, y);
    int biggest_building_size = api_min(biggest_x_dimension, biggest_y_dimension);

    int number_of_buildings = sizeof (building_table) / sizeof (building_table[0]);
    int i = 0;
    for (; i < number_of_buildings; i++) {
        if (building_table[i].size > biggest_building_size) {
            break;
        }
    }
    assert(i > 0);
    return (i - 1);
}

void api_modify_elements_r(void* xp, int num_elements, int (*rand_a)(void), int (*rand_b)(void)) {
    // Modify up to num_elements of xp, in place
    // Decide on the square to change with rand_a and the new building with rand_b

    //    ab(*squares)[ANNEAL_DIM] = (ab(*)[ANNEAL_DIM])xp;

    for (int i = 0; i < num_elements; i++) {
        int x = rand_a() % ANNEAL_X_DIM;
        int y = rand_a() % ANNEAL_Y_DIM;

        // The index of the largest building we can put at x,y
        int biggest_buildable_building = api_get_biggest_building_index(x, y);

        int new_building_type = rand_b() % (biggest_buildable_building + 1);
        api_replace_building(xp, x, y, new_building_type);
    }
    return;
}

void api_replace_building(void* xp, int x, int y, int new_building_type) {
    // replace the building at xp[x][y] with new_building
    // paving over any buildings that get in the way
    ab(*squares)[ANNEAL_Y_DIM] = (ab(*)[ANNEAL_Y_DIM])xp;

    // firstly, pave over anything that would be touched by the building
    int new_building_size = building_table[new_building_type].size;

    for (int i = 0; i < new_building_size; i++) {
        for (int j = 0; j < new_building_size; j++) {
            api_pave_over(squares, x + i, y + j);
        }
    }

    // secondly, place the new building down
    for (int i = 0; i < new_building_size; i++) {
        for (int j = 0; j < new_building_size; j++) {
            squares[x + i][y + j].building_type = new_building_type;
            squares[x + i][y + j].uid = global_building_uid_counter;
        }
    }
    global_building_uid_counter++;
}

void api_pave_over(void* xp, int x, int y) {
    // pave over the square at xp[x][y] and any other tiles that
    // that building covers
    ab(*squares)[ANNEAL_Y_DIM] = (ab(*)[ANNEAL_Y_DIM])xp;

    int uid = squares[x][y].uid;
    int building_type = squares[x][y].building_type;

    for (int i = 0; i < ANNEAL_X_DIM; i++) {
        for (int j = 0; j < ANNEAL_Y_DIM; j++) {
            if (squares[i][j].uid == uid) {
                assert(squares[i][j].building_type == building_type);

                //                if (squares[i][j].building_type != building_type){
                //                    printf("x:%d  y:%d  i:%d  j:%d uid:%d\n", x, y, i, j, uid);
                //
                //
                //                    for (int y = 0; y < 4; y++) {
                //                        printf("%d %d %d %d\n", squares[0][y].building_type, squares[1][y].building_type, squares[2][y].building_type, squares[3][y].building_type);
                //                    }
                //
                //                    for (int y = 0; y < 4; y++) {
                //                        printf("%d %d %d %d\n", squares[0][y].uid, squares[1][y].uid, squares[2][y].uid, squares[3][y].uid);
                //                    }
                //                    // for debugging
                //                    assert(squares[x][y].building_type == squares[i][j].building_type);
                //
                //                }
                squares[i][j].building_type = 2; // road
                squares[i][j].uid = global_building_uid_counter;
                global_building_uid_counter++;
            }
        }
    }
}

void api_modify_elements(void* xp, int num_elements) {
    // Modify up to num_elements of xp, in place,
    // specifying which random number generators to use
    api_modify_elements_r(xp, num_elements, rand, rand);
}
