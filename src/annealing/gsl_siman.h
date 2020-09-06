/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   gsl_siman_trivial.h
 * Author: iain
 *
 * Created on 18 March 2020, 13:09
 */

#ifndef GSL_SIMAN_SMALL_H
#define GSL_SIMAN_SMALL_H

#ifdef __cplusplus
extern "C" {
#endif

    int gsl_siman_main(void);
    int anneal_next_loop;
    void gsl_provision_city(void);
    // an annealing building

    typedef struct {
        int building_type;
        unsigned int uid;
    } ab;

    #define ANNEAL_X_DIM 8
    #define ANNEAL_Y_DIM 2
    
#ifdef __cplusplus
}
#endif

#endif /* GSL_SIMAN_SMALL_H */

