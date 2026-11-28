#ifndef BUILDING_HOUSE_EVOLUTION_H
#define BUILDING_HOUSE_EVOLUTION_H

#include "building/building.h"

/**
 * Evolves/devolves houses if appropriate, and consumes pottery/furniture/oil/wine
 */
void building_house_process_evolve_and_consume_goods(void);

/** Read only the native current/next goods-and-services predicate, using local
 * demand counters. Returns -1 for an invalid/inactive house or no next model.
 * Does not test desirability, population, merging, space or evolution timing.
 */
int building_house_goods_services_pass(const building *house, int for_upgrade);

/**
 * Determine the text to show for evolution of a house, stored in house->evolve_text_id
 * @param house House to determine text for
 * @param worst_desirability_building The ID of the building with worst contribution to desirability
 */
void building_house_determine_evolve_text(building *house, int worst_desirability_building);

/**
 * Determine building with worst contribution to desirability
 * @param house House to determine worst building for
 * @return Worst desirability building ID
 */
int building_house_determine_worst_desirability_building(const building *house);

#endif // BUILDING_HOUSE_EVOLUTION_H
