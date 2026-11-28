#ifndef GYMNASIUM_FINANCE_H
#define GYMNASIUM_FINANCE_H

/** Read finance JSON without refreshing caches or advancing the simulation.
 * Monthly tax bases are raw cached units, not denarii at the current rate.
 * Returns 0 on success, -1 for invalid output/capacity or insufficient space.
 */
int gymnasium_get_finance_state(char *output, int capacity);

#endif
