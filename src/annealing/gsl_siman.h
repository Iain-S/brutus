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

    int gsl_siman_main(int, int, int, int);
//    int gsl_siman_main(void);

    int anneal_next_loop;
    void gsl_provision_city(void);

    // an annealing building
    typedef struct {
        // different to Caesar's building type, ours an index into an array
        int building_index;
        // each building has a uid
        unsigned int uid;
    } ab;

    int ANNEAL_X_DIM;
    int ANNEAL_Y_DIM;
    int ANNEAL_X_OFFSET;
    int ANNEAL_Y_OFFSET;

#ifdef __cplusplus
}
#endif

#endif /* GSL_SIMAN_SMALL_H */

