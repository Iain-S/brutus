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
#include "annealing/gsl_siman.h"
#include "annealing/annealing_api.h"
#include "widget/city.h"

typedef void (*place_building_func)(int, int, building_type);

typedef struct {
    char* name;
    int size;
    building_type type;
} building_row;

void api_place_building(int x, int y, building_type building_type) {
    int placed = 0;
    switch (building_type) {
        case BUILDING_NONE:
            break;
        case BUILDING_HOUSE_VACANT_LOT:
            placed = place_houses(0, x, y, x, y);
            // assert(placed == 1);
            break;
        case BUILDING_PLAZA:
            api_place_building(x, y, BUILDING_ROAD);
            // note: no break; because we want to build the plaza on the road
        default:
            building_construction_set_type(building_type);
            map_tile tile;
            tile.x = x;
            tile.y = y;
            tile.grid_offset = 1;
            build_start(&tile);
            build_move(&tile);
            build_end();
            // ToDo - Check that we could place the building
    }
}

building_row building_table[] = {
    // These must be sorted in ascending size
    // and the sizes are along one dimension (i.e. width not area)
    {"empty land", 1, BUILDING_NONE},
    {"house", 1, BUILDING_HOUSE_VACANT_LOT},
    {"road", 1, BUILDING_ROAD},
    {"prefecture", 1, BUILDING_PREFECTURE},
    {"garden", 1, BUILDING_GARDENS},
    {"well", 1, BUILDING_WELL},
    {"engineer's post", 1, BUILDING_ENGINEERS_POST},
    {"doctor", 1, BUILDING_DOCTOR},
    {"barber", 1, BUILDING_BARBER},
    {"small statue", 1, BUILDING_SMALL_STATUE},
    {"fountain", 1, BUILDING_FOUNTAIN},
    {"plaza", 1, BUILDING_PLAZA},
    {"market", 2, BUILDING_MARKET},
    {"school", 2, BUILDING_SCHOOL},
    {"bath house", 2, BUILDING_BATHHOUSE},
    {"library", 2, BUILDING_LIBRARY},
    {"small temple to ceres", 2, BUILDING_SMALL_TEMPLE_CERES},
    {"small temple to neptune", 2, BUILDING_SMALL_TEMPLE_NEPTUNE},
    {"small temple to mercury", 2, BUILDING_SMALL_TEMPLE_MERCURY},
    {"small temple to mars", 2, BUILDING_SMALL_TEMPLE_MARS},
    {"small temple to venus", 2, BUILDING_SMALL_TEMPLE_VENUS},
    {"oracle", 2, BUILDING_ORACLE},
    {"theatre", 2, BUILDING_THEATER},
    {"medium statue", 2, BUILDING_MEDIUM_STATUE},
    {"large statue", 3, BUILDING_LARGE_STATUE},
    {"academy", 3, BUILDING_ACADEMY},
    {"hospital", 3, BUILDING_HOSPITAL},
    {"amphitheatre", 3, BUILDING_AMPHITHEATER},
    {"colosseum", 5, BUILDING_COLOSSEUM}
};

int global_building_uid_counter = 1;

char* api_get_building_name(int i) {
    return building_table[i].name;
}

/* Get the index in building_table of this type of building */
int api_get_index_from_type(building_type building_type) {
    int array_length = sizeof (building_table) / sizeof (building_table[0]);
    for (int i = 0; i < array_length; i++) {
        if (building_table[i].type == building_type) {
            return i;
        }
    }
    // We should never get this far
    assert(0);
}

/* Get the C3 building type from the index of this building */
building_type api_get_type_from_index(int building_index) {
    return building_table[building_index].type;
}

void api_list_buildings() {
    int highest_id = building_get_highest_id();

    // There always seems to be an empty building in the 0th element of
    // the master buildings array
    for (int i = 1; i <= highest_id; i++) {
        building* b = building_get(i);

        // ToDo There seems to be a short (few seconds) lag between building a
        //      building and it being picked up.  Not sure if it's an issue in practice.
        if ((int) b->state > BUILDING_STATE_UNUSED
            && (int) b->state < BUILDING_STATE_DELETED_BY_GAME) {
            printf("x: %u, y: %u, s:%u, t:%hi\n",
                   (unsigned) b->x,
                   (unsigned) b->y,
                   (unsigned) b->size,
                   b->type);
        }
    }
}

int api_score_city(int x_start, int y_start, int x_end, int y_end) {
    // The same as ratings.calculate_max_prosperity but we take the total
    // prosperity, not the average per house

    int points = 0;
    for (int i = 1; i < MAX_BUILDINGS; i++) {
        building *b = building_get(i);
        if (b->state && b->house_size) {
            if (b->x >= x_start && b->x <= x_end && b->y >= y_start && b->y <= y_end) {
                points += model_get_house(b->subtype.house_level)->prosperity;
            }
        }
    }
    return points;
}

int already_built(int* built_uids, int max, int uid) {
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
                api_place_building(ANNEAL_X_OFFSET + x,
                                   ANNEAL_Y_OFFSET + y,
                                   building_table[my_building.building_index].type);
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
    // Replace the building at xp[x][y] with new_building
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
            squares[x + i][y + j].building_index = new_building_type;
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
    int building_type = squares[x][y].building_index;

    for (int i = 0; i < ANNEAL_X_DIM; i++) {
        for (int j = 0; j < ANNEAL_Y_DIM; j++) {
            if (squares[i][j].uid == uid) {
                assert(squares[i][j].building_index == building_type);

                squares[i][j].building_index = 2;  // road
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
