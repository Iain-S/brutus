#include "water_supply.h"

#include "building/building.h"
#include "building/model.h"
#include "core/image.h"
#include "map/grid.h"
#include "map/image.h"
#include "map/terrain.h"
#include "scenario/property.h"

#include <stdio.h>

#define APPEND(...) do { \
    int written = snprintf(output + used, capacity - used, __VA_ARGS__); \
    if (written < 0 || written >= capacity - used) return -1; \
    used += written; \
} while (0)

int gymnasium_get_water_supply(char *output, int capacity)
{
    if (!output || capacity <= 0) {
        return -1;
    }
    int used = 0;
    APPEND("{\"schema_version\":1,\"reservoir_radius\":10,\"fountain_radius\":%d,"
        "\"scope\":\"active water structures and aqueduct tiles; cached native supply state\",\"buildings\":[",
        scenario_property_climate() == CLIMATE_DESERT ? 3 : 4);
    int count = 0;
    for (int id = 1; id < MAX_BUILDINGS; id++) {
        const building *b = building_get(id);
        if (b->state != BUILDING_STATE_IN_USE) continue;
        const char *kind = b->type == BUILDING_RESERVOIR ? "reservoir" :
            b->type == BUILDING_FOUNTAIN ? "fountain" : b->type == BUILDING_WELL ? "well" : NULL;
        if (!kind) continue;
        APPEND("%s{\"id\":%d,\"kind\":\"%s\",\"type\":%d,\"x\":%d,\"y\":%d,\"size\":%d,"
            "\"workers\":%d,\"workers_required\":%d,\"water_access\":%d,\"near_water\":%d,"
            "\"in_reservoir_range\":%d}", count++ ? "," : "", id, kind, b->type, b->x, b->y, b->size,
            b->num_workers, model_get_building(b->type)->laborers, b->has_water_access,
            b->type == BUILDING_RESERVOIR && map_terrain_exists_tile_in_area_with_type(b->x - 1, b->y - 1, 5, TERRAIN_WATER),
            !!map_terrain_is(b->grid_offset, TERRAIN_RESERVOIR_RANGE));
    }
    APPEND("],\"aqueducts\":[");
    count = 0;
    int wet_image_base = image_group(GROUP_BUILDING_AQUEDUCT);
    for (int y = 0; y < map_grid_height(); y++) {
        for (int x = 0; x < map_grid_width(); x++) {
            int offset = map_grid_offset(x, y);
            if (map_terrain_is(offset, TERRAIN_AQUEDUCT)) {
                /* The aqueduct grid also stores topology offsets, not just 0/1 water. */
                int image_id = map_image_at(offset);
                int water = image_id >= wet_image_base && image_id < wet_image_base + 15;
                APPEND("%s{\"x\":%d,\"y\":%d,\"water\":%d}", count++ ? "," : "", x, y, water);
            }
        }
    }
    APPEND("]}");
    return 0;
}
