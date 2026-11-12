#include "imperial.h"

#include "city/data_private.h"
#include "city/emperor.h"
#include "city/ratings.h"

#include <stdio.h>

int gymnasium_get_imperial_state(char *output, int capacity)
{
    if (!output || capacity <= 0) {
        return -1;
    }
    int savings = city_emperor_personal_savings();
    int modest = city_emperor_gift_cost(GIFT_MODEST);
    int generous = city_emperor_gift_cost(GIFT_GENEROUS);
    int lavish = city_emperor_gift_cost(GIFT_LAVISH);
    int written = snprintf(output, capacity,
        "{\"schema_version\":1,\"payment_source\":\"personal_savings\",\"favor\":%d,"
        "\"personal_savings\":%d,\"player_rank\":%d,\"salary_rank\":%d,\"salary_amount\":%d,"
        "\"months_since_gift\":%d,\"gift_overdose_penalty\":%d,\"gifts\":["
        "{\"size\":0,\"name\":\"modest\",\"cost\":%d,\"affordable\":%s},"
        "{\"size\":1,\"name\":\"generous\",\"cost\":%d,\"affordable\":%s},"
        "{\"size\":2,\"name\":\"lavish\",\"cost\":%d,\"affordable\":%s}]}",
        city_rating_favor(), savings, city_emperor_rank(), city_emperor_salary_rank(), city_emperor_salary_amount(),
        city_emperor_months_since_gift(), city_data.emperor.gift_overdose_penalty,
        modest, modest <= savings ? "true" : "false", generous, generous <= savings ? "true" : "false",
        lavish, lavish <= savings ? "true" : "false");
    return written < 0 || written >= capacity ? -1 : 0;
}
