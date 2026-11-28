#include "housing.h"

#include "building/building.h"
#include "building/house_evolution.h"
#include "building/model.h"
#include "city/data_private.h"
#include "city/resource.h"
#include "game/resource.h"
#include "map/desirability.h"

#include <stdio.h>

#define APPEND(...) do { \
    int written = snprintf(output + used, capacity - used, __VA_ARGS__); \
    if (written < 0 || written >= capacity - used) return -1; \
    used += written; \
} while (0)

int gymnasium_get_housing_state(char *output, int capacity)
{
    if (!output || capacity <= 0) return -1;
    int used = 0;
    const model_building *garden = model_get_building(BUILDING_GARDENS);
    APPEND("{\"schema_version\":1,\"scope\":\"active houses; cached values and independent goods/service checks; not an upgrade guarantee\","
        "\"inventory_order\":[\"wheat\",\"vegetables\",\"fruit\",\"meat\",\"wine\",\"oil\",\"furniture\",\"pottery\"],"
        "\"native_cached_prosperity_cap\":%d,\"multiple_wine_available\":%s,"
        "\"garden_model\":{\"cost\":%d,\"desirability_value\":%d,\"desirability_step\":%d,\"desirability_step_size\":%d,\"desirability_range\":%d},"
        "\"models\":[", city_data.ratings.prosperity_max, city_resource_multiple_wine_available() ? "true" : "false",
        garden->cost, garden->desirability_value, garden->desirability_step, garden->desirability_step_size, garden->desirability_range);
    for (int level = HOUSE_SMALL_TENT; level <= HOUSE_LUXURY_PALACE; level++) {
        const model_house *m = model_get_house(level);
        APPEND("%s{\"level\":%d,\"devolve_desirability\":%d,\"evolve_desirability\":%d,"
            "\"entertainment\":%d,\"water\":%d,\"religion\":%d,\"education\":%d,"
            "\"barber\":%d,\"bathhouse\":%d,\"health\":%d,\"food_types\":%d,"
            "\"pottery\":%d,\"oil\":%d,\"furniture\":%d,\"wine\":%d,"
            "\"prosperity\":%d,\"max_people\":%d,\"tax_multiplier\":%d}", level ? "," : "",
            level, m->devolve_desirability, m->evolve_desirability, m->entertainment, m->water,
            m->religion, m->education, m->barber, m->bathhouse, m->health, m->food_types,
            m->pottery, m->oil, m->furniture, m->wine, m->prosperity, m->max_people, m->tax_multiplier);
    }
    APPEND("],\"houses\":[");
    int count = 0;
    for (int id = 1; id < MAX_BUILDINGS; id++) {
        const building *b = building_get(id);
        if (b->state != BUILDING_STATE_IN_USE || !building_is_house(b->type)) continue;
        int level = b->subtype.house_level;
        if (level < HOUSE_SMALL_TENT || level > HOUSE_LUXURY_PALACE) return -1;
        int at_max = level == HOUSE_LUXURY_PALACE;
        const model_house *m = model_get_house(level);
        int desirability_allows = !at_max && b->desirability > m->devolve_desirability && b->desirability >= m->evolve_desirability;
        char next_level[16];
        if (at_max) snprintf(next_level, sizeof(next_level), "null");
        else snprintf(next_level, sizeof(next_level), "%d", level + 1);
        int food_types = 0;
        for (int i = INVENTORY_MIN_FOOD; i < INVENTORY_MAX_FOOD; i++) {
            if (b->data.house.inventory[i]) food_types++;
        }
        APPEND("%s{\"id\":%d,\"type\":%d,\"x\":%d,\"y\":%d,\"size\":%d,\"house_size\":%d,\"merged\":%d,"
            "\"population\":%d,\"level\":%d,\"next_level\":%s,\"desirability_cached\":%d,\"tile_desirability_cached\":%d,"
            "\"desirability_allows_upgrade\":%s,\"current_goods_services_pass\":%s,\"next_goods_services_pass\":%s,"
            "\"no_space_to_expand_cached\":%d,\"devolve_delay_cached\":%d,\"well\":%d,\"fountain\":%d,"
            "\"food_types_checked\":%d,\"num_foods_cached\":%d,\"entertainment\":%d,\"education\":%d,"
            "\"num_gods\":%d,\"barber\":%d,\"bathhouse\":%d,\"health\":%d,"
            "\"inventory_units\":[%d,%d,%d,%d,%d,%d,%d,%d]}",
            count++ ? "," : "", id, b->type, b->x, b->y, b->size, b->house_size, b->house_is_merged,
            b->house_population, level, next_level, b->desirability, map_desirability_get(b->grid_offset),
            desirability_allows ? "true" : "false", building_house_goods_services_pass(b, 0) ? "true" : "false",
            at_max ? "null" : building_house_goods_services_pass(b, 1) ? "true" : "false",
            b->data.house.no_space_to_expand, b->data.house.devolve_delay, b->has_well_access, b->has_water_access,
            food_types, b->data.house.num_foods, b->data.house.entertainment, b->data.house.education,
            b->data.house.num_gods, b->data.house.barber, b->data.house.bathhouse, b->data.house.health,
            b->data.house.inventory[0], b->data.house.inventory[1], b->data.house.inventory[2], b->data.house.inventory[3],
            b->data.house.inventory[4], b->data.house.inventory[5], b->data.house.inventory[6], b->data.house.inventory[7]);
    }
    APPEND("]}");
    return 0;
}
