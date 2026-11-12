#include "food_supply.h"

#include "building/building.h"
#include "building/industry.h"
#include "building/model.h"
#include "game/resource.h"
#include "map/road_access.h"

#include <stdio.h>

int gymnasium_get_food_supply(char *output, int capacity)
{
    if (!output || capacity <= 0) {
        return -1;
    }
    int used = snprintf(output, capacity,
        "{\"schema_version\":1,\"units_per_load\":100,"
        "\"food_order\":[\"wheat\",\"vegetables\",\"fruit\",\"meat\"],"
        "\"scope\":\"active food farms, granaries and markets; excludes cargo, warehouses and households\","
        "\"buildings\":[");
    if (used < 0 || used >= capacity) {
        return -1;
    }
    int count = 0;
    for (int id = 1; id < MAX_BUILDINGS; id++) {
        const building *b = building_get(id);
        if (b->state != BUILDING_STATE_IN_USE) {
            continue;
        }
        const char *kind;
        char details[512];
        int written;
        if (building_is_farm(b->type) && resource_is_food(b->output_resource_id)) {
            kind = "farm";
            written = snprintf(details, sizeof(details),
                "\"output_resource_id\":%d,\"progress_points\":%d,\"progress_max\":%d,"
                "\"blessing_days\":%d,\"curse_days\":%d",
                b->output_resource_id, b->data.industry.progress, building_industry_max_progress(b),
                b->data.industry.blessing_days_left, b->data.industry.curse_days_left);
        } else if (b->type == BUILDING_GRANARY) {
            kind = "granary";
            written = snprintf(details, sizeof(details),
                "\"food_units\":[%d,%d,%d,%d],\"free_space_units\":%d",
                b->data.granary.resource_stored[RESOURCE_WHEAT],
                b->data.granary.resource_stored[RESOURCE_VEGETABLES],
                b->data.granary.resource_stored[RESOURCE_FRUIT],
                b->data.granary.resource_stored[RESOURCE_MEAT],
                b->data.granary.resource_stored[RESOURCE_NONE]);
        } else if (b->type == BUILDING_MARKET) {
            kind = "market";
            written = snprintf(details, sizeof(details),
                "\"food_units\":[%d,%d,%d,%d]",
                b->data.market.inventory[INVENTORY_WHEAT], b->data.market.inventory[INVENTORY_VEGETABLES],
                b->data.market.inventory[INVENTORY_FRUIT], b->data.market.inventory[INVENTORY_MEAT]);
        } else {
            continue;
        }
        if (written < 0 || written >= (int)sizeof(details)) {
            return -1;
        }
        int road_access = b->type == BUILDING_GRANARY ? map_has_road_access_granary(b->x, b->y, NULL) :
            map_has_road_access(b->x, b->y, b->size, NULL);
        written = snprintf(output + used, capacity - used,
            "%s{\"id\":%d,\"kind\":\"%s\",\"type\":%d,\"x\":%d,\"y\":%d,"
            "\"workers\":%d,\"workers_required\":%d,\"houses_covered\":%d,"
            "\"road_access\":%d,\"road_access_cached\":%d,\"road_network_id\":%d,\"distance_from_entry\":%d,"
            "\"primary_figure_id\":%d,\"shared_figure_id\":%d,%s}",
            count ? "," : "", b->id, kind, b->type, b->x, b->y,
            b->num_workers, model_get_building(b->type)->laborers, b->houses_covered,
            road_access, b->has_road_access, b->road_network_id, b->distance_from_entry,
            b->figure_id, b->figure_id2, details);
        if (written < 0 || written >= capacity - used) {
            return -1;
        }
        used += written;
        count++;
    }
    int written = snprintf(output + used, capacity - used, "]}");
    return written < 0 || written >= capacity - used ? -1 : 0;
}
