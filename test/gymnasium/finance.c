#include "building/building.h"
#include "city/data_private.h"
#include "gymnasium/finance.h"
#include "gymnasium/gymnasium.h"
#include "map/building.h"
#include "map/grid.h"
#include "map/road_network.h"
#include "map/terrain.h"

#include <stdio.h>
#include <string.h>

#define CHECK(condition) do { if (!(condition)) { \
    fprintf(stderr, "Finance check failed at line %d: %s\n", __LINE__, #condition); return 1; \
} } while (0)

static unsigned char city_before[sizeof(city_data)];
static building buildings_before[MAX_BUILDINGS];
static char output[262144];
static char guarded[262146];
static int terrain_before[GRID_SIZE * GRID_SIZE];
static int map_buildings_before[GRID_SIZE * GRID_SIZE];
static int road_network_before[GRID_SIZE * GRID_SIZE];

static void snapshot(void)
{
    memcpy(city_before, &city_data, sizeof(city_data));
    for (int i = 0; i < MAX_BUILDINGS; i++) {
        memcpy(&buildings_before[i], building_get(i), sizeof(building));
    }
    for (int i = 0; i < GRID_SIZE * GRID_SIZE; i++) {
        terrain_before[i] = map_terrain_get(i);
        map_buildings_before[i] = map_building_at(i);
        road_network_before[i] = map_road_network_get(i);
    }
}

static int unchanged(void)
{
    if (memcmp(city_before, &city_data, sizeof(city_data))) return 0;
    for (int i = 0; i < MAX_BUILDINGS; i++) {
        if (memcmp(&buildings_before[i], building_get(i), sizeof(building))) return 0;
    }
    for (int i = 0; i < GRID_SIZE * GRID_SIZE; i++) {
        if (terrain_before[i] != map_terrain_get(i) || map_buildings_before[i] != map_building_at(i) ||
            road_network_before[i] != map_road_network_get(i)) return 0;
    }
    return 1;
}

int main(void)
{
    map_grid_init(64, 64, 0, 98);
    map_terrain_clear();
    map_road_network_clear();
    building_clear_all();
    memset(&city_data, 0, sizeof(city_data));
    snapshot();
    CHECK(gymnasium_get_finance_state(output, sizeof(output)) == 0);
    CHECK(strstr(output, "\"collectors\":[],\"houses\":[]"));
    CHECK(unchanged());

    city_data.finance.treasury = -123;
    city_data.finance.tax_percentage = 17;
    city_data.labor.wages = 32;
    city_data.labor.wages_rome = 30;
    city_data.finance.estimated_tax_income = 901;
    city_data.finance.estimated_wages = 802;
    city_data.finance.wages_so_far = 101;
    city_data.finance.interest_so_far = 12;
    city_data.finance.salary_so_far = 23;
    city_data.taxes.taxed_plebs = 777;
    city_data.taxes.untaxed_patricians = 888;
    city_data.taxes.percentage_taxed_people = 42;
    city_data.taxes.monthly.collected_plebs = 101;
    city_data.taxes.monthly.collected_patricians = 203;
    city_data.taxes.monthly.uncollected_plebs = 305;
    city_data.taxes.monthly.uncollected_patricians = 407;
    city_data.taxes.yearly.collected_plebs = 11;
    city_data.taxes.yearly.collected_patricians = 13;
    city_data.taxes.yearly.uncollected_plebs = 17;
    city_data.taxes.yearly.uncollected_patricians = 19;
    city_data.finance.this_year.income.taxes = 999;
    city_data.finance.this_year.expenses.total = 321;
    city_data.finance.this_year.net_in_out = -222;
    city_data.finance.last_year.income.exports = 543;
    city_data.finance.last_year.balance = -456;

    building *house = building_get(1);
    house->state = BUILDING_STATE_IN_USE;
    house->type = BUILDING_HOUSE_LARGE_TENT;
    house->house_size = 1;
    house->house_population = 7;
    house->house_tax_coverage = 1;
    building *untaxed = building_get(2);
    *untaxed = *house;
    untaxed->house_population = 9;
    untaxed->house_tax_coverage = 0;
    building *empty = building_get(3);
    *empty = *house;
    empty->house_population = 0;
    empty->house_tax_coverage = 50;
    building *inactive = building_get(4);
    *inactive = *house;
    inactive->state = BUILDING_STATE_CREATED;
    building *forum = building_get(5);
    forum->state = BUILDING_STATE_IN_USE;
    forum->type = BUILDING_FORUM;
    forum->size = 2;
    forum->x = 12;
    forum->y = 13;
    forum->num_workers = 6;
    forum->has_road_access = 1;
    forum->houses_covered = 8;
    forum->figure_id = 123;
    building *senate = building_get(6);
    *senate = *forum;
    senate->type = BUILDING_SENATE;
    senate->num_workers = 0;
    senate->has_road_access = 0;
    senate->figure_id = 0;
    building *removed = building_get(7);
    *removed = *forum;
    removed->state = BUILDING_STATE_DELETED_BY_PLAYER;
    /* Scan the complete building array, not a compact active-ID prefix. */
    building *last = building_get(MAX_BUILDINGS - 1);
    *last = *house;
    last->house_population = 5;
    snapshot();
    CHECK(gymnasium_get_finance_state(output, sizeof(output)) == 0);
    CHECK(strstr(output, "\"treasury\":-123,\"tax_percentage\":17,\"wages\":32,\"wages_rome\":30"));
    CHECK(strstr(output, "\"estimated_tax_income_cached\":901,\"estimated_wages_cached\":802"));
    CHECK(strstr(output, "\"yearly_collected_denarii\":24"));
    CHECK(strstr(output, "\"wages_so_far\":101,\"interest_so_far\":12,\"salary_so_far\":23"));
    CHECK(strstr(output, "\"covered_population\":12,\"occupied_population\":21"));
    CHECK(strstr(output, "\"taxed_plebs\":777"));
    CHECK(strstr(output, "\"untaxed_patricians\":888"));
    CHECK(strstr(output, "\"percentage_taxed_people\":42"));
    CHECK(strstr(output, "\"monthly_tax_base_units_cached\":{\"collected_plebs\":101,\"collected_patricians\":203,\"uncollected_plebs\":305,\"uncollected_patricians\":407}"));
    CHECK(strstr(output, "\"yearly_tax_denarii\":{\"collected_plebs\":11,\"collected_patricians\":13,\"uncollected_plebs\":17,\"uncollected_patricians\":19}"));
    CHECK(strstr(output, "\"this_year\":{\"income\":{\"taxes\":999"));
    CHECK(strstr(output, "\"total\":321},\"net_in_out\":-222"));
    CHECK(strstr(output, "\"last_year\":{\"income\":{\"taxes\":0,\"exports\":543"));
    CHECK(strstr(output, "\"balance\":-456"));
    CHECK(strstr(output, "\"id\":5,\"type\":86,\"x\":12,\"y\":13,\"workers\":6,\"road_access_cached\":true,\"road_access_native\":false,\"houses_covered_activity_cached\":8,\"figure_id\":123"));
    CHECK(strstr(output, "\"id\":6,\"type\":85,\"x\":12,\"y\":13,\"workers\":0,\"road_access_cached\":false,\"road_access_native\":false"));
    CHECK(!strstr(output, "\"road_access\":") && !strstr(output, "\"houses_covered\":"));
    CHECK(!strstr(output, "\"id\":4,") && !strstr(output, "\"id\":7,"));
    CHECK(strstr(output, "\"id\":1,\"population\":7,\"tax_coverage\":1"));
    CHECK(strstr(output, "\"id\":2,\"population\":9,\"tax_coverage\":0"));
    CHECK(strstr(output, "\"id\":3,\"population\":0,\"tax_coverage\":50"));
    CHECK(strstr(output, "\"id\":1999,\"population\":5,\"tax_coverage\":1"));
    CHECK(unchanged());
    CHECK(julius_env_get_finance_state(NULL, output, sizeof(output)) == -1);
    CHECK(gymnasium_get_finance_state(NULL, 10) == -1);
    CHECK(gymnasium_get_finance_state(output, 0) == -1);
    CHECK(gymnasium_get_finance_state(output, -1) == -1);

    int length = (int) strlen(output);
    /* Exercise failure in both fixed metadata and variable-length arrays. */
    const int capacities[] = {1, 4, 128, length - 20, length, length + 1};
    for (unsigned i = 0; i < sizeof(capacities) / sizeof(capacities[0]); i++) {
        int capacity = capacities[i];
        memset(guarded, 'X', sizeof(guarded));
        int result = gymnasium_get_finance_state(guarded + 1, capacity);
        CHECK(result == (capacity > length ? 0 : -1));
        CHECK(guarded[0] == 'X' && guarded[capacity + 1] == 'X');
        CHECK(guarded[capacity] == '\0');
        CHECK(unchanged());
    }
    city_data.finance.tax_percentage = 0;
    snapshot();
    CHECK(gymnasium_get_finance_state(output, sizeof(output)) == 0);
    CHECK(strstr(output, "\"covered_population\":12,\"occupied_population\":21"));
    CHECK(strstr(output, "\"yearly_collected_denarii\":24"));
    CHECK(strstr(output, "\"collected_plebs\":101,\"collected_patricians\":203"));
    CHECK(unchanged());

    map_terrain_add(map_grid_offset(11, 13), TERRAIN_ROAD);
    map_road_network_update();
    snapshot();
    CHECK(gymnasium_get_finance_state(output, sizeof(output)) == 0);
    CHECK(strstr(output, "\"workers\":6,\"road_access_cached\":true,\"road_access_native\":true"));
    CHECK(strstr(output, "\"workers\":0,\"road_access_cached\":false,\"road_access_native\":true"));
    CHECK(unchanged());
    const int invalid_sizes[] = {0, 6};
    for (unsigned i = 0; i < sizeof(invalid_sizes) / sizeof(invalid_sizes[0]); i++) {
        forum->size = invalid_sizes[i];
        snapshot();
        CHECK(gymnasium_get_finance_state(output, sizeof(output)) == 0);
        CHECK(strstr(output, "\"workers\":6,\"road_access_cached\":true,\"road_access_native\":false"));
        CHECK(unchanged());
    }

    for (int i = 1; i < MAX_BUILDINGS; i++) *building_get(i) = *house;
    snapshot();
    CHECK(gymnasium_get_finance_state(output, sizeof(output)) == 0);
    CHECK(strstr(output, "\"id\":1999,"));
    CHECK(unchanged());
    puts("Finance raw units, cached accounting, current coverage, collectors, immutability and buffer guards passed.");
    return 0;
}
