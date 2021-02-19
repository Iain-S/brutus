#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "annealing/annealing_api.h"
#include "annealing/gsl_siman.h"


int inc_counter = 0;

int increment_one(void) {
    // returns 1 then 2 then 3....
    inc_counter++;
    return inc_counter;
}

int return_one(void) {
    return 1;
}


int global_int = 0;

int return_global_int(void) {
    return global_int;
}


//int (*get_zeroed_xp(void))[ANNEAL_DIM]{
//    // Don't forget to free it once you're done
//    ab (*xp)[ANNEAL_DIM] = (ab(*)[ANNEAL_DIM])calloc(ANNEAL_DIM * ANNEAL_DIM, sizeof(ab));
//    return xp;
//}

void test_api_modify_elements_r1(void) {
    printf("test_api_modify_elements_r\n");

    ab(*xp)[ANNEAL_DIM] = (ab(*)[ANNEAL_DIM])calloc(ANNEAL_DIM * ANNEAL_DIM, sizeof (ab));

    for (int x = 0; x < ANNEAL_DIM; x++) {
        for (int y = 0; y < ANNEAL_DIM; y++) {
            xp[x][y].building_type = 0;
            xp[x][y].uid = global_building_uid_counter;
            global_building_uid_counter++;
        }
    }
    
    api_modify_elements_r(xp, 1, return_one, return_one);

    for (int x = 0; x < ANNEAL_DIM; x++) {
        for (int y = 0; y < ANNEAL_DIM; y++) {
            if (x == 0 && y == 1) {
                assert(xp[x][y].building_type == 1);
            } else {
                assert(xp[x][y].building_type == 0);
            }
            xp[x][y].building_type = 0;
        }
    }
    free(xp);
}

void test_api_modify_elements_r2(void) {
    printf("test_api_modify_elements_r\n");

    // ToDo srand() with the time

    ab(*xp)[ANNEAL_DIM] = (ab(*)[ANNEAL_DIM])calloc(ANNEAL_DIM * ANNEAL_DIM, sizeof (ab));

    api_modify_elements_r(xp, 1, rand, rand);

    //    for (int x = 0; x < ANNEAL_DIM; x++){
    //        for (int y = 0; y < ANNEAL_DIM; y++){
    //            int building_size = building_sizes[xp[x][y].building_type];
    //            assert(building_size <= ANNEAL_DIM - y);
    //            y += building_size;
    //        }
    //    }
    free(xp);
}

void test_api_pave_over(void) {
    printf("test_api_pave_over\n");
    ab(*xp)[ANNEAL_DIM] = (ab(*)[ANNEAL_DIM])calloc(ANNEAL_DIM * ANNEAL_DIM, sizeof (ab));

    // set everything to empty land
    for (int x = 0; x < ANNEAL_DIM; x++) {
        for (int y = 0; y < ANNEAL_DIM; y++) {
            xp[x][y].building_type = 0;
            xp[x][y].uid = global_building_uid_counter;
            global_building_uid_counter++;
        }
    }

    xp[0][0].building_type = 6;
    xp[0][0].uid = 876;
    xp[0][1].building_type = 6;
    xp[0][1].uid = 876;
    xp[1][0].building_type = 6;
    xp[1][0].uid = 876;
    xp[1][1].building_type = 6;
    xp[1][1].uid = 876;

    api_pave_over(xp, 1, 1);
    assert(xp[0][0].building_type == 2); // road
    assert(xp[0][1].building_type == 2); // road
    assert(xp[1][0].building_type == 2); // road
    assert(xp[1][1].building_type == 2); // road
}

void test_api_replace_building(void) {
    printf("test_api_replace_building\n");
    ab(*xp)[ANNEAL_DIM] = (ab(*)[ANNEAL_DIM])calloc(ANNEAL_DIM * ANNEAL_DIM, sizeof (ab));

    // set everything to empty land
    for (int x = 0; x < ANNEAL_DIM; x++) {
        for (int y = 0; y < ANNEAL_DIM; y++) {
            xp[x][y].building_type = 0;
            xp[x][y].uid = global_building_uid_counter;
            global_building_uid_counter++;
        }
    }

    xp[0][0].building_type = 6;
    xp[0][0].uid = 876;
    xp[0][1].building_type = 6;
    xp[0][1].uid = 876;
    xp[1][0].building_type = 6;
    xp[1][0].uid = 876;
    xp[1][1].building_type = 6;
    xp[1][1].uid = 876;

    api_replace_building(xp, 1, 1, 6);
    assert(xp[0][0].building_type == 2); // road
    assert(xp[0][1].building_type == 2); // road
    assert(xp[1][0].building_type == 2); // road
    assert(xp[1][1].building_type == 6); // market
    assert(xp[1][2].building_type == 6); // market
    assert(xp[2][1].building_type == 6); // market
    assert(xp[2][2].building_type == 6); // market
    assert(xp[3][3].building_type == 0); // empty land
    assert(xp[3][2].building_type == 0); // empty land
    assert(xp[2][3].building_type == 0); // empty land
}

void test_api_get_biggest_building_index(void) {
    printf("test_api_get_biggest_building_index\n");

    assert(api_get_biggest_building_index(0, 0) == 7);
    assert(api_get_biggest_building_index(ANNEAL_DIM-1, ANNEAL_DIM-1) == 5);
}

int main(void) {
    test_api_get_biggest_building_index();
    test_api_modify_elements_r1();
    test_api_pave_over();
    test_api_replace_building();
}


// mock widget functions
typedef int map_tile;

void build_start(const map_tile *tile) {
    return;
}


//static 

void build_move(const map_tile *tile) {
    return;
}


//static 

void build_end(void) {
    return;
}

int gsl_siman_main(void) {
    return 0;
}