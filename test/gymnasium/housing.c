#include "building/building.h"
#include "building/house_evolution.h"
#include "building/model.h"
#include "city/data_private.h"
#include "city/houses.h"
#include "game/resource.h"
#include "gymnasium/housing.h"
#include "map/desirability.h"
#include "map/grid.h"

#include <stdio.h>
#include <string.h>

#define CHECK(condition) do { if (!(condition)) { \
    fprintf(stderr, "Housing check failed at line %d: %s\n", __LINE__, #condition); return 1; \
} } while (0)

int main(void)
{
    map_grid_init(64, 64, 0, 98);
    building_clear_all();
    memset(&city_data, 0, sizeof(city_data));
    model_house *current = (model_house *) model_get_house(HOUSE_LARGE_TENT);
    model_house *next = (model_house *) model_get_house(HOUSE_SMALL_SHACK);
    memset(current, 0, sizeof(*current));
    memset(next, 0, sizeof(*next));
    current->devolve_desirability = -12;
    current->evolve_desirability = -5;
    current->water = next->water = 1;
    next->food_types = 1;
    building *house = building_create(BUILDING_HOUSE_LARGE_TENT, 5, 5);
    house->state = BUILDING_STATE_IN_USE;
    house->house_size = 1;
    house->house_population = 7;
    house->desirability = -6;
    house->has_well_access = 1;
    unsigned char before[sizeof(*house)];
    memcpy(before, house, sizeof(*house));
    static unsigned char city_before[sizeof(city_data)];
    memcpy(city_before, &city_data, sizeof(city_data));
    house_demands demands = *city_houses_demands();
    char output[32768];
    CHECK(building_house_goods_services_pass(house, 0) == 1);
    CHECK(building_house_goods_services_pass(house, 1) == 0);
    CHECK(gymnasium_get_housing_state(output, sizeof(output)) == 0);
    CHECK(strstr(output, "\"desirability_cached\":-6"));
    CHECK(strstr(output, "\"tile_desirability_cached\":0"));
    CHECK(strstr(output, "\"desirability_allows_upgrade\":false"));
    CHECK(strstr(output, "\"current_goods_services_pass\":true,\"next_goods_services_pass\":false"));
    CHECK(memcmp(before, house, sizeof(*house)) == 0);
    CHECK(memcmp(city_before, &city_data, sizeof(city_data)) == 0);
    CHECK(memcmp(&demands, city_houses_demands(), sizeof(demands)) == 0);
    house->data.house.inventory[INVENTORY_MEAT] = 28;
    CHECK(building_house_goods_services_pass(house, 1) == 1);
    next->wine = 2;
    house->data.house.inventory[INVENTORY_WINE] = 1;
    CHECK(building_house_goods_services_pass(house, 1) == 0);
    city_data.resource.wine_types_available = 2;
    CHECK(building_house_goods_services_pass(house, 1) == 1);
    house->desirability = -12;
    current->evolve_desirability = -12;
    CHECK(gymnasium_get_housing_state(output, sizeof(output)) == 0);
    CHECK(strstr(output, "\"desirability_allows_upgrade\":false"));
    house->desirability = -11;
    CHECK(gymnasium_get_housing_state(output, sizeof(output)) == 0);
    CHECK(strstr(output, "\"desirability_allows_upgrade\":true"));
    CHECK(building_house_goods_services_pass(NULL, 0) == -1);
    house->subtype.house_level = HOUSE_SMALL_TENT - 1;
    CHECK(building_house_goods_services_pass(house, 0) == -1);
    CHECK(building_house_goods_services_pass(house, 1) == -1);
    CHECK(gymnasium_get_housing_state(output, sizeof(output)) == -1);
    house->subtype.house_level = HOUSE_LUXURY_PALACE + 1;
    CHECK(building_house_goods_services_pass(house, 0) == -1);
    CHECK(gymnasium_get_housing_state(output, sizeof(output)) == -1);
    house->subtype.house_level = HOUSE_LARGE_TENT;
    house->state = BUILDING_STATE_CREATED;
    CHECK(building_house_goods_services_pass(house, 0) == -1);
    house->state = BUILDING_STATE_IN_USE;
    building *well = building_create(BUILDING_WELL, 15, 15);
    well->state = BUILDING_STATE_IN_USE;
    CHECK(building_house_goods_services_pass(well, 0) == -1);
    building *palace = building_create(BUILDING_HOUSE_LUXURY_PALACE, 10, 10);
    palace->state = BUILDING_STATE_IN_USE;
    CHECK(building_house_goods_services_pass(palace, 1) == -1);
    CHECK(gymnasium_get_housing_state(output, sizeof(output)) == 0);
    CHECK(strstr(output, "\"next_level\":null") && strstr(output, "\"next_goods_services_pass\":null"));
    char tiny[16];
    memset(tiny, 'X', sizeof(tiny));
    CHECK(gymnasium_get_housing_state(tiny, 4) == -1 && tiny[4] == 'X');
    CHECK(gymnasium_get_housing_state(NULL, 4) == -1 && gymnasium_get_housing_state(output, 0) == -1);
    puts("Housing model/service gates, maximum-level guards, immutable query and buffer checks passed.");
    return 0;
}
