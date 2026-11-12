#include "building/building.h"
#include "building/model.h"
#include "city/data_private.h"
#include "city/labor.h"

#include <limits.h>
#include <stdio.h>
#include <string.h>

#define CHECK(condition) do { if (!(condition)) { \
    fprintf(stderr, "Labor snapshot check failed at line %d: %s\n", __LINE__, #condition); return 1; \
} } while (0)

typedef struct {
    unsigned char city[sizeof(city_data)];
    building buildings[MAX_BUILDINGS];
    int cursor;
} allocation_snapshot;

static allocation_snapshot before;
static allocation_snapshot allocated;

static void capture(allocation_snapshot *snapshot)
{
    memcpy(snapshot->city, &city_data, sizeof(city_data));
    for (int i = 0; i < MAX_BUILDINGS; i++) {
        memcpy(&snapshot->buildings[i], building_get(i), sizeof(building));
    }
    snapshot->cursor = city_labor_water_allocation_cursor();
}

static void restore_data(const allocation_snapshot *snapshot)
{
    memcpy(&city_data, snapshot->city, sizeof(city_data));
    for (int i = 0; i < MAX_BUILDINGS; i++) {
        memcpy(building_get(i), &snapshot->buildings[i], sizeof(building));
    }
}

static int data_equal(const allocation_snapshot *snapshot)
{
    if (memcmp(snapshot->city, &city_data, sizeof(city_data))) return 0;
    for (int i = 0; i < MAX_BUILDINGS; i++) {
        if (memcmp(&snapshot->buildings[i], building_get(i), sizeof(building))) return 0;
    }
    return 1;
}

static void seed_water_scarcity(void)
{
    building_clear_all();
    memset(&city_data, 0, sizeof(city_data));
    model_building *fountain = (model_building *) model_get_building(BUILDING_FOUNTAIN);
    fountain->laborers = 4;
    city_data.labor.workers_available = 4;
    city_data.labor.categories[3].workers_needed = 12;
    city_data.labor.categories[3].buildings = 3;
    city_data.labor.categories[3].priority = 1;
    for (int i = 1; i <= 3; i++) {
        building *b = building_get(i);
        b->state = BUILDING_STATE_IN_USE;
        b->type = BUILDING_FOUNTAIN;
        b->size = 1;
    }
}

static int workers_are(int first, int second, int third)
{
    return building_get(1)->num_workers == first && building_get(2)->num_workers == second &&
        building_get(3)->num_workers == third;
}

int main(void)
{
    CHECK(city_labor_water_allocation_cursor() == 1);
    seed_water_scarcity();
    capture(&before);
    CHECK(city_labor_water_allocation_cursor() == 1 && data_equal(&before));

    /* Capture/restore helpers must not alter city data or any building. */
    const int valid[] = {1, 2, MAX_BUILDINGS - 1};
    for (unsigned i = 0; i < sizeof(valid) / sizeof(valid[0]); i++) {
        city_labor_restore_water_allocation_cursor(valid[i]);
        CHECK(city_labor_water_allocation_cursor() == valid[i] && data_equal(&before));
    }
    const int invalid[] = {INT_MIN, -1, 0, MAX_BUILDINGS, MAX_BUILDINGS + 1, INT_MAX};
    for (unsigned i = 0; i < sizeof(invalid) / sizeof(invalid[0]); i++) {
        city_labor_restore_water_allocation_cursor(2);
        city_labor_restore_water_allocation_cursor(invalid[i]);
        CHECK(city_labor_water_allocation_cursor() == 1 && data_equal(&before));
    }

    city_labor_allocate_workers();
    CHECK(city_data.labor.categories[3].workers_allocated == 4);
    CHECK(city_data.labor.workers_employed == 4 && city_data.labor.workers_needed == 8);
    CHECK(workers_are(0, 0, 4));
    CHECK(city_labor_water_allocation_cursor() == 3);
    capture(&allocated);

    /* This models the old incomplete rollback: identical visible state, wrong next result. */
    restore_data(&before);
    CHECK(data_equal(&before) && city_labor_water_allocation_cursor() == 3);
    city_labor_allocate_workers();
    CHECK(workers_are(0, 4, 0) && city_labor_water_allocation_cursor() == 2);
    CHECK(!data_equal(&allocated));
    restore_data(&before);
    city_labor_allocate_workers();
    CHECK(workers_are(4, 0, 0) && city_labor_water_allocation_cursor() == 1);

    /* Full rollback, including the hidden cursor, reproduces every city/building byte. */
    restore_data(&before);
    city_labor_restore_water_allocation_cursor(before.cursor);
    city_labor_allocate_workers();
    CHECK(data_equal(&allocated) && city_labor_water_allocation_cursor() == allocated.cursor);
    restore_data(&before);
    city_labor_restore_water_allocation_cursor(before.cursor);
    city_labor_allocate_workers();
    CHECK(data_equal(&allocated) && city_labor_water_allocation_cursor() == allocated.cursor);

    /* Clearing only the fixture's state does not reset the module cursor. */
    seed_water_scarcity();
    CHECK(data_equal(&before) && city_labor_water_allocation_cursor() == 3);
    city_labor_restore_water_allocation_cursor(1);
    city_labor_allocate_workers();
    CHECK(data_equal(&allocated) && city_labor_water_allocation_cursor() == allocated.cursor);

    seed_water_scarcity();
    city_data.labor.workers_available = 12;
    city_labor_restore_water_allocation_cursor(2);
    city_labor_allocate_workers();
    CHECK(workers_are(4, 4, 4) && city_labor_water_allocation_cursor() == 1);
    CHECK(city_data.labor.workers_employed == 12 && city_data.labor.workers_needed == 0);

    seed_water_scarcity();
    city_data.labor.workers_available = 0;
    city_labor_restore_water_allocation_cursor(3);
    city_labor_allocate_workers();
    CHECK(workers_are(0, 0, 0) && city_labor_water_allocation_cursor() == 1);
    CHECK(city_data.labor.workers_employed == 0 && city_data.labor.workers_needed == 12);
    puts("Water labor scarcity rotation, complete rollback, cursor guards and reset/full employment passed.");
    return 0;
}
