#ifndef SRC_ANNEALING_GSL_SIMAN_H_
#define SRC_ANNEALING_GSL_SIMAN_H_

#ifdef __cplusplus
extern "C" {
#endif

    int gsl_siman_main(int, int, int, int);

    int anneal_next_loop;
    void gsl_provision_city(void);

    // An "annealing building"
    typedef struct {
        // Different to Caesar's building type, ours an index into an array
        int building_index;
        // Each building has a uid
        unsigned int uid;
    } ab;

    int ANNEAL_X_DIM;
    int ANNEAL_Y_DIM;
    int ANNEAL_X_OFFSET;
    int ANNEAL_Y_OFFSET;

#ifdef __cplusplus
}
#endif

#endif  // SRC_ANNEALING_GSL_SIMAN_H_
