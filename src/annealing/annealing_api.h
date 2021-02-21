// API functions that can be used outside of annealing_api.c
#ifndef SRC_ANNEALING_ANNEALING_API_H_
#define SRC_ANNEALING_ANNEALING_API_H_

#include "building/type.h"

#ifdef __cplusplus
extern "C" {
#endif

    int api_score_city(int, int, int, int);
    void api_change_a_square(void);
    void api_list_buildings(void);
    void api_build_buildings(void*);
    void api_modify_elements(void*, int);
    char* api_get_building_name(int);
    void api_modify_elements_r(void*, int, int (*)(void), int (*)(void));
    void api_pave_over(void*, int, int);
    void api_replace_building(void*, int, int, int);
    int api_get_biggest_building_index(int, int);
    int global_building_uid_counter;
    int api_get_index_from_type(building_type);
    building_type api_get_type_from_index(int);

#ifdef __cplusplus
}
#endif

#endif  // SRC_ANNEALING_ANNEALING_API_H_
