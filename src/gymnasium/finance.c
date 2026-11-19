#include "finance.h"

#include "building/building.h"
#include "city/data_private.h"
#include "map/road_access.h"

#include <stdio.h>

#define APPEND(...) do { \
    int written = snprintf(output + used, capacity - used, __VA_ARGS__); \
    if (written < 0 || written >= capacity - used) return -1; \
    used += written; \
} while (0)

static int append_overview(char *output, int capacity, const finance_overview *overview)
{
    int written = snprintf(output, capacity,
        "{\"income\":{\"taxes\":%d,\"exports\":%d,\"donated\":%d,\"total\":%d},"
        "\"expenses\":{\"imports\":%d,\"wages\":%d,\"construction\":%d,\"interest\":%d,"
        "\"salary\":%d,\"sundries\":%d,\"tribute\":%d,\"total\":%d},"
        "\"net_in_out\":%d,\"balance\":%d}",
        overview->income.taxes, overview->income.exports, overview->income.donated, overview->income.total,
        overview->expenses.imports, overview->expenses.wages, overview->expenses.construction,
        overview->expenses.interest, overview->expenses.salary, overview->expenses.sundries,
        overview->expenses.tribute, overview->expenses.total, overview->net_in_out, overview->balance);
    return written < 0 || written >= capacity ? -1 : written;
}

int gymnasium_get_finance_state(char *output, int capacity)
{
    if (!output || capacity <= 0) return -1;
    int used = 0;
    int covered_population = 0;
    int occupied_population = 0;
    for (int i = 1; i < MAX_BUILDINGS; i++) {
        const building *b = building_get(i);
        if (b->state == BUILDING_STATE_IN_USE && b->house_size && b->house_population > 0) {
            occupied_population += b->house_population;
            if (b->house_tax_coverage) covered_population += b->house_population;
        }
    }
    APPEND("{\"schema_version\":1,"
        "\"scope\":\"all in-use house_size records and senate/forum buildings; coverage population computed now; tax population and overview cached; yearly tax counters reset at native year change; monthly bases are not denarii or bound to the current tax rate\","
        "\"treasury\":%d,\"tax_percentage\":%d,\"wages\":%d,\"wages_rome\":%d,"
        "\"estimated_tax_income_cached\":%d,\"estimated_wages_cached\":%d,"
        "\"yearly_collected_denarii\":%lld,"
        "\"wages_so_far\":%d,\"interest_so_far\":%d,\"salary_so_far\":%d,"
        "\"covered_population\":%d,\"occupied_population\":%d,",
        city_data.finance.treasury, city_data.finance.tax_percentage, city_data.labor.wages, city_data.labor.wages_rome,
        city_data.finance.estimated_tax_income, city_data.finance.estimated_wages,
        (long long) city_data.taxes.yearly.collected_plebs + city_data.taxes.yearly.collected_patricians,
        city_data.finance.wages_so_far, city_data.finance.interest_so_far, city_data.finance.salary_so_far,
        covered_population, occupied_population);
    APPEND("\"tax_population_cached\":{\"taxed_plebs\":%d,\"taxed_patricians\":%d,"
        "\"untaxed_plebs\":%d,\"untaxed_patricians\":%d,\"percentage_taxed_plebs\":%d,"
        "\"percentage_taxed_patricians\":%d,\"percentage_taxed_people\":%d},",
        city_data.taxes.taxed_plebs, city_data.taxes.taxed_patricians,
        city_data.taxes.untaxed_plebs, city_data.taxes.untaxed_patricians,
        city_data.taxes.percentage_taxed_plebs, city_data.taxes.percentage_taxed_patricians,
        city_data.taxes.percentage_taxed_people);
    APPEND("\"monthly_tax_base_units_cached\":{\"collected_plebs\":%d,\"collected_patricians\":%d,"
        "\"uncollected_plebs\":%d,\"uncollected_patricians\":%d},"
        "\"yearly_tax_denarii\":{\"collected_plebs\":%d,\"collected_patricians\":%d,"
        "\"uncollected_plebs\":%d,\"uncollected_patricians\":%d},",
        city_data.taxes.monthly.collected_plebs, city_data.taxes.monthly.collected_patricians,
        city_data.taxes.monthly.uncollected_plebs, city_data.taxes.monthly.uncollected_patricians,
        city_data.taxes.yearly.collected_plebs, city_data.taxes.yearly.collected_patricians,
        city_data.taxes.yearly.uncollected_plebs, city_data.taxes.yearly.uncollected_patricians);
    APPEND("\"overview_cached\":{\"this_year\":");
    int written = append_overview(output + used, capacity - used, &city_data.finance.this_year);
    if (written < 0) return -1;
    used += written;
    APPEND(",\"last_year\":");
    written = append_overview(output + used, capacity - used, &city_data.finance.last_year);
    if (written < 0) return -1;
    used += written;
    APPEND("},\"collectors\":[");
    int count = 0;
    for (int i = 1; i < MAX_BUILDINGS; i++) {
        const building *b = building_get(i);
        if (b->state != BUILDING_STATE_IN_USE ||
            b->type < BUILDING_SENATE_1_UNUSED || b->type > BUILDING_FORUM_2_UNUSED) continue;
        int road_access = b->size >= 1 && b->size <= 5 && map_has_road_access(b->x, b->y, b->size, NULL);
        APPEND("%s{\"id\":%d,\"type\":%d,\"x\":%d,\"y\":%d,\"workers\":%d,"
            "\"road_access_cached\":%s,\"road_access_native\":%s,\"houses_covered_activity_cached\":%d,\"figure_id\":%d}",
            count ? "," : "", i, b->type, b->x, b->y, b->num_workers,
            b->has_road_access ? "true" : "false", road_access ? "true" : "false", b->houses_covered, b->figure_id);
        count++;
    }
    APPEND("],\"houses\":[");
    count = 0;
    for (int i = 1; i < MAX_BUILDINGS; i++) {
        const building *b = building_get(i);
        if (b->state != BUILDING_STATE_IN_USE || !b->house_size) continue;
        APPEND("%s{\"id\":%d,\"population\":%d,\"tax_coverage\":%d}",
            count ? "," : "", i, b->house_population, b->house_tax_coverage);
        count++;
    }
    APPEND("]}");
    return 0;
}
