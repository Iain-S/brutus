#include "building/building.h"
#include "gymnasium/observation.h"

#include <stdio.h>

int main(void)
{
    building_clear_all();
    building *head = building_create(BUILDING_HIPPODROME, 1, 1);
    building *middle = building_create(BUILDING_HIPPODROME, 6, 1);
    building *tail = building_create(BUILDING_HIPPODROME, 11, 1);
    head->next_part_building_id = middle->id;
    middle->prev_part_building_id = head->id;
    middle->next_part_building_id = tail->id;
    tail->prev_part_building_id = middle->id;

    gymnasium_observation_t observation;
    if (gymnasium_get_observation(&observation) || observation.buildings.entertainment != 1) {
        fprintf(stderr, "One linked hippodrome must count as one venue; got %d\n",
            observation.buildings.entertainment);
        return 1;
    }

    building_create(BUILDING_WINE_WORKSHOP, 1, 10);
    building_create(BUILDING_SCHOOL, 5, 10);
    building_create(BUILDING_THEATER, 10, 10);
    gymnasium_get_observation(&observation);
    if (observation.buildings.industrial_buildings != 1 || observation.buildings.education != 1 ||
        observation.buildings.entertainment != 2 || observation.buildings.total_buildings != 6) {
        fprintf(stderr, "Created workshop, school, theater or physical-record counts are incorrect\n");
        return 1;
    }
    building_clear_all();
    gymnasium_get_observation(&observation);
    if (observation.buildings.total_buildings || observation.buildings.industrial_buildings ||
        observation.buildings.education || observation.buildings.entertainment) {
        fprintf(stderr, "Cleared buildings retained stale aggregates\n");
        return 1;
    }
    puts("Asset-free aggregate and linked-venue counts passed.");
    return 0;
}
