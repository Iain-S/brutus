#include "building/building.h"
#include "core/image.h"
#include "gymnasium/action.h"
#include "gymnasium/water_supply.h"
#include "map/aqueduct.h"
#include "map/grid.h"
#include "map/image.h"
#include "map/terrain.h"

#include <stdio.h>
#include <string.h>

#define CHECK(condition) do { if (!(condition)) { \
    fprintf(stderr, "Water check failed at line %d: %s\n", __LINE__, #condition); return 1; \
} } while (0)

int main(void)
{
    map_grid_init(64, 64, 0, 98);
    building_clear_all();
    building *reservoir = building_create(BUILDING_RESERVOIR, 4, 4);
    reservoir->state = BUILDING_STATE_IN_USE;
    reservoir->has_water_access = 1;
    building *fountain = building_create(BUILDING_FOUNTAIN, 8, 8);
    fountain->state = BUILDING_STATE_IN_USE;
    fountain->num_workers = 2;
    fountain->has_water_access = 1;
    int tile = map_grid_offset(7, 5);
    map_terrain_add(tile, TERRAIN_AQUEDUCT);
    map_aqueduct_set(tile, 9); /* Rendering/topology offsets are not water flags. */
    int base = image_group(GROUP_BUILDING_AQUEDUCT);
    map_image_set(tile, base + 15);
    int wet = map_grid_offset(8, 5);
    map_terrain_add(wet, TERRAIN_AQUEDUCT);
    map_aqueduct_set(wet, 0);
    map_image_set(wet, base + 3);
    char output[4096];
    unsigned char before[sizeof(*reservoir)];
    memcpy(before, reservoir, sizeof(*reservoir));
    CHECK(gymnasium_get_water_supply(output, sizeof(output)) == 0);
    CHECK(strstr(output, "\"kind\":\"reservoir\""));
    CHECK(strstr(output, "\"kind\":\"fountain\""));
    CHECK(strstr(output, "{\"x\":7,\"y\":5,\"water\":0}"));
    CHECK(strstr(output, "{\"x\":8,\"y\":5,\"water\":1}"));
    CHECK(memcmp(before, reservoir, sizeof(*reservoir)) == 0 && map_aqueduct_at(tile) == 9);
    CHECK(map_image_at(tile) == base + 15 && map_image_at(wet) == base + 3);
    char tiny[16];
    memset(tiny, 'X', sizeof(tiny));
    CHECK(gymnasium_get_water_supply(tiny, 4) == -1 && tiny[4] == 'X');
    CHECK(gymnasium_get_water_supply(NULL, 20) == -1 && gymnasium_get_water_supply(output, 0) == -1);
    CHECK(ACTION_SEND_LAVISH_GIFT == 58 && ACTION_BUILD_RESERVOIR == 59 && ACTION_BUILD_AQUEDUCT == 60);
    CHECK(ACTION_COUNT == 61);
    puts("Water structure/tile diagnostics, read-only state, IDs and buffer guards passed.");
    return 0;
}
