#include "building/building.h"
#include "game/resource.h"
#include "gymnasium/food_supply.h"

#include <stdio.h>
#include <string.h>

int main(void)
{
    building_clear_all();
    building *farm = building_create(BUILDING_WHEAT_FARM, 1, 1);
    farm->state = BUILDING_STATE_IN_USE;
    farm->data.industry.progress = 175;
    farm->loads_stored = 9; /* Not an output inventory for farms. */
    building *granary = building_create(BUILDING_GRANARY, 5, 1);
    granary->state = BUILDING_STATE_IN_USE;
    granary->data.granary.resource_stored[RESOURCE_NONE] = 1300;
    granary->data.granary.resource_stored[RESOURCE_WHEAT] = 500;
    granary->data.granary.resource_stored[RESOURCE_VEGETABLES] = 200;
    granary->data.granary.resource_stored[RESOURCE_FRUIT] = 300;
    granary->data.granary.resource_stored[RESOURCE_MEAT] = 100;
    granary->data.granary.resource_stored[RESOURCE_OLIVES] = 999;
    building *market = building_create(BUILDING_MARKET, 9, 1);
    market->state = BUILDING_STATE_IN_USE;
    market->data.market.inventory[INVENTORY_WHEAT] = 350;
    market->data.market.inventory[INVENTORY_VEGETABLES] = 120;
    market->data.market.inventory[INVENTORY_FRUIT] = 75;
    market->data.market.inventory[INVENTORY_MEAT] = 80;
    market->data.market.inventory[INVENTORY_WINE] = 999;
    market->figure_id2 = 77; /* Shared with labor seekers, not necessarily a buyer. */
    building *olive = building_create(BUILDING_OLIVE_FARM, 12, 1);
    olive->state = BUILDING_STATE_IN_USE;
    unsigned char before[sizeof(*farm)];
    memcpy(before, farm, sizeof(*farm));
    char output[4096];
    if (gymnasium_get_food_supply(output, sizeof(output)) ||
        !strstr(output, "\"progress_points\":175,\"progress_max\":200") ||
        !strstr(output, "\"food_units\":[500,200,300,100],\"free_space_units\":1300") ||
        !strstr(output, "\"food_units\":[350,120,75,80]") ||
        !strstr(output, "\"shared_figure_id\":77") || strstr(output, "buyer_id") ||
        strstr(output, "\"type\":103") || strstr(output, "999") ||
        memcmp(before, farm, sizeof(*farm))) {
        fprintf(stderr, "Food inventory mapping, crop filtering or read-only query failed\n");
        return 1;
    }
    char tiny[16];
    memset(tiny, 'X', sizeof(tiny));
    if (gymnasium_get_food_supply(tiny, 4) != -1 || tiny[4] != 'X' ||
        gymnasium_get_food_supply(NULL, 20) != -1) {
        fprintf(stderr, "Food query buffer guards failed\n");
        return 1;
    }
    puts("Asset-free food inventory mapping, production units and buffer guards passed.");
    return 0;
}
