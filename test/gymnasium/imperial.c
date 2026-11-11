#include "city/data_private.h"
#include "city/emperor.h"
#include "gymnasium/action.h"
#include "gymnasium/imperial.h"

#include <stdio.h>
#include <string.h>

#define CHECK(condition) do { if (!(condition)) { \
    fprintf(stderr, "Imperial check failed at line %d: %s\n", __LINE__, #condition); return 1; \
} } while (0)

int main(void)
{
    memset(&city_data, 0, sizeof(city_data));
    city_data.finance.treasury = 5000;
    city_data.ratings.favor = 50;
    city_data.emperor.personal_savings = 800;
    city_data.emperor.player_rank = 3;
    city_emperor_set_salary_rank(3);
    static unsigned char before[sizeof(city_data)];
    memcpy(before, &city_data, sizeof(city_data));
    char output[2048];
    CHECK(gymnasium_get_imperial_state(output, sizeof(output)) == 0);
    CHECK(strstr(output, "\"personal_savings\":800"));
    CHECK(strstr(output, "\"cost\":120,\"affordable\":true"));
    CHECK(strstr(output, "\"cost\":250,\"affordable\":true"));
    CHECK(strstr(output, "\"cost\":500,\"affordable\":true"));
    CHECK(memcmp(before, &city_data, sizeof(city_data)) == 0);
    CHECK(city_emperor_gift_cost(-1) == -1 && city_emperor_gift_cost(3) == -1);
    char tiny[16];
    memset(tiny, 'X', sizeof(tiny));
    CHECK(gymnasium_get_imperial_state(tiny, 4) == -1 && tiny[4] == 'X');
    CHECK(gymnasium_get_imperial_state(NULL, 20) == -1);
    CHECK(gymnasium_get_imperial_state(output, 0) == -1);
    CHECK(ACTION_BUILD_LOW_BRIDGE == 55 && ACTION_SEND_MODEST_GIFT == 56 && ACTION_COUNT == 59);

    gymnasium_action_t gift = { .type = ACTION_SEND_LAVISH_GIFT, .x = -1, .y = -1 };
    gymnasium_action_result_t result;
    CHECK(gymnasium_validate_action(&gift, &result));
    CHECK(memcmp(before, &city_data, sizeof(city_data)) == 0);
    CHECK(gymnasium_execute_action(&gift, &result) == 0);
    CHECK(city_data.emperor.personal_savings == 300 && city_data.ratings.favor == 60);
    CHECK(city_data.finance.treasury == 5000 && city_data.emperor.gift_overdose_penalty == 1);
    CHECK(gymnasium_execute_action(&gift, &result) == 0);
    CHECK(city_data.emperor.personal_savings == 50 && city_data.ratings.favor == 65);
    memcpy(before, &city_data, sizeof(city_data));
    CHECK(!gymnasium_validate_action(&gift, &result) && result.reason == ACTION_ERROR_NO_MONEY);
    CHECK(gymnasium_execute_action(&gift, &result) != 0);
    CHECK(memcmp(before, &city_data, sizeof(city_data)) == 0);
    CHECK(gymnasium_get_imperial_state(output, sizeof(output)) == 0);
    CHECK(strstr(output, "\"cost\":125,\"affordable\":false"));
    gift.type = ACTION_SEND_MODEST_GIFT;
    CHECK(gymnasium_execute_action(&gift, &result) == 0);
    CHECK(city_data.emperor.personal_savings == 24 && city_data.ratings.favor == 65);
    gift.type = ACTION_SEND_GENEROUS_GIFT;
    CHECK(!gymnasium_validate_action(&gift, &result));
    city_data.emperor.personal_savings = 800;
    city_data.emperor.gift_overdose_penalty = 0;
    city_data.ratings.favor = 50;
    CHECK(gymnasium_execute_action(&gift, &result) == 0);
    CHECK(city_data.emperor.personal_savings == 550 && city_data.ratings.favor == 55);
    CHECK(city_data.finance.treasury == 5000);
    const int minimum_savings[] = {22, 66, 199};
    for (int size = 0; size < 3; size++) {
        gift.type = ACTION_SEND_MODEST_GIFT + size;
        city_data.emperor.personal_savings = minimum_savings[size] - 1;
        CHECK(!gymnasium_validate_action(&gift, &result));
        city_data.emperor.personal_savings++;
        CHECK(city_emperor_gift_cost(size) == city_data.emperor.personal_savings);
        CHECK(gymnasium_execute_action(&gift, &result) == 0);
        CHECK(city_data.emperor.personal_savings == 0);
    }
    city_data.emperor.personal_savings = 10000;
    city_data.emperor.gift_overdose_penalty = 0;
    city_data.ratings.favor = 50;
    const int gains[] = {10, 5, 3, 1, 0};
    for (int i = 0; i < 5; i++) {
        int savings = city_data.emperor.personal_savings;
        int cost = city_emperor_gift_cost(GIFT_LAVISH);
        int favor = city_data.ratings.favor;
        CHECK(gymnasium_execute_action(&gift, &result) == 0);
        CHECK(city_data.emperor.personal_savings == savings - cost);
        CHECK(city_data.ratings.favor == favor + gains[i]);
    }
    puts("Imperial query, fresh costs, personal payments, gift penalties and action guards passed.");
    return 0;
}
