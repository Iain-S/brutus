/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   annealing_api.h
 * Author: iain
 *
 * Created on 15 February 2020, 16:56
 */

#ifndef ANNEALING_API_H
#define ANNEALING_API_H

#ifdef __cplusplus
extern "C" {
#endif

    //void api_place_house(int x, int y);
//    void api_init_random_3_by_3(void);
    int api_score_random_3_by_3(void);
    void api_change_a_square(void);
    void api_build_buildings(void*);
    void api_modify_elements(void*, int);
    char* api_get_building_name(int);

    
#ifdef __cplusplus
}
#endif

#endif /* ANNEALING_API_H */

