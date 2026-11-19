"""Two-stage retrieval retains model-selected alternatives and exact native evidence."""
import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent/'examples'))
import ollama_planner as adapter
import ollama_planner_lookup as lookup


class LookupTests(unittest.TestCase):
    def context(self):
        base = dict(ticks=1600, status='completed', population=100, culture=0, prosperity=0,
                    food_stocks=0, desirability_blocked_houses=10, health=50)
        return dict(decision_id=5, objective='Win in minimum ticks', forecast_policy={'minimum_ticks': 1600},
                    state={'population_total': 90}, elapsed_ticks=4000, remaining_ticks=8800,
                    minimum_decision_interval=800, housing={'test': 1}, finance={'test': 2},
                    candidates=[dict(id='wait', ticks=800, forecast=base),
                                dict(id='housing', ticks=25, net_treasury_outlay=200,
                                     forecast={**base, 'population': 130, 'desirability_blocked_houses': 15}),
                                dict(id='food', ticks=72, forecast={**base, 'food_stocks': 100})],
                    recent_outcomes=[dict(candidate_id='housing', ticks=800, status='completed',
                        delta={k: 0 for k in ('population', 'residents_with_food', 'health', 'culture',
                                             'granary_food_units', 'market_food_units', 'house_food_units', 'treasury')})])

    def query(self):
        return dict(decision_id=5, candidate_ids=['food', 'housing'])

    def answer(self):
        return dict(decision_id=5, candidate_id='food', comparisons=[
            dict(candidate_id='food', macro_ticks=72, forecast_ticks=1600, population=100, culture=0,
                 prosperity=0, food_stocks=100, blocked_houses=10, blocked_vs_wait=0),
            dict(candidate_id='housing', macro_ticks=25, forecast_ticks=1600, population=130, culture=0,
                 prosperity=0, food_stocks=0, blocked_houses=15, blocked_vs_wait=5)])

    def test_query_preserves_full_compact_context_options_and_all_ids(self):
        context = self.context()
        before = copy.deepcopy(context)
        for fmt in ('rows', 'objects', 'overrides'):
            options = dict(forecast_format=fmt, temperature=.7, top_p=.8, top_k=20, min_p=0., context_tokens=8192)
            base = adapter.request_body(context, 'model', 256, **options)
            body = lookup.lookup_request_body(context, 'model', 256, **options)
            self.assertEqual(body['prompt'], base['prompt'])
            self.assertEqual(body['options'], base['options'])
            schema = body['format']
            self.assertEqual(set(schema['properties']), {'decision_id', 'candidate_ids'})
            self.assertFalse(schema['additionalProperties'])
            ids = schema['properties']['candidate_ids']
            self.assertEqual((ids['minItems'], ids['maxItems']), (2, 2))
            self.assertEqual(ids['items'], dict(type='string', enum=['wait', 'housing', 'food']))
            self.assertEqual(schema['properties']['decision_id']['enum'], [5])
            self.assertNotIn('under eight words', body['system'])
            self.assertIn('not a final', body['system'])
        self.assertEqual(context, before)

    def test_queries_preserve_model_order_and_allow_every_legal_candidate(self):
        self.assertEqual(lookup.validate_lookup(self.context(), self.query()), ['food', 'housing'])
        for ids in (['wait', 'food'], ['housing', 'wait']):
            self.assertEqual(lookup.validate_lookup(self.context(), dict(decision_id=5, candidate_ids=ids)), ids)

    def test_invalid_query_schema_identity_count_types_and_membership(self):
        bad = [None, [], dict(decision_id=True, candidate_ids=['food', 'housing']),
               dict(decision_id=6, candidate_ids=['food', 'housing']),
               dict(decision_id=5, candidate_ids=['food']), dict(decision_id=5, candidate_ids=[]),
               dict(decision_id=5, candidate_ids=['food', 'food']),
               dict(decision_id=5, candidate_ids=['food', 'unknown']),
               dict(decision_id=5, candidate_ids=['food', True]),
               dict(decision_id=5, candidate_ids='food'),
               dict(decision_id=5, candidate_ids=['food', 'housing', 'wait']),
               {**self.query(), 'reason': 'extra'}]
        for value in bad:
            with self.subTest(value=value), self.assertRaises(ValueError):
                lookup.validate_lookup(self.context(), value)

    def test_materialized_forecasts_and_comparisons_have_native_values_and_provenance(self):
        context = self.context()
        before = copy.deepcopy(context)
        result = lookup.materialize_lookup(context, self.query())
        self.assertEqual(result['decision_id'], 5)
        self.assertEqual(result['candidate_ids'], ['food', 'housing'])
        self.assertEqual(result['context_sha256'], lookup.context_fingerprint(context))
        for row in result['alternatives']:
            native = next(c for c in context['candidates'] if c['id'] == row['candidate_id'])
            self.assertEqual(row['macro_execution_ticks'], native['ticks'])
            self.assertEqual(row['net_treasury_outlay'], native.get('net_treasury_outlay'))
            self.assertEqual(len(row['forecast']), 20)
            for key, value in row['forecast'].items():
                self.assertIs(type(value), type(native['forecast'].get(key)))
                self.assertEqual(value, native['forecast'].get(key))
        self.assertEqual(result['alternatives'][0]['comparison_facts'], self.answer()['comparisons'][0])
        self.assertEqual(result['alternatives'][1]['comparison_facts'], self.answer()['comparisons'][1])
        self.assertEqual(result['wait_forecast']['desirability_blocked_houses'], 10)
        self.assertEqual(context, before)
        result['alternatives'][0]['forecast']['population'] = -1
        self.assertEqual(context, before)

    def test_fingerprint_is_order_independent_but_detects_different_raw_state(self):
        context = self.context()
        reordered = dict(reversed(list(context.items())))
        self.assertEqual(lookup.context_fingerprint(context), lookup.context_fingerprint(reordered))
        reordered['state'] = {'population_total': 91}
        self.assertNotEqual(lookup.context_fingerprint(context), lookup.context_fingerprint(reordered))

    def test_second_stage_keeps_common_context_and_only_model_requested_schema_ids(self):
        context = self.context()
        data = lookup.materialize_lookup(context, self.query())
        body = lookup.lookup_choice_request_body(context, data, 'm', 256, forecast_format='overrides')
        base = adapter.request_body(context, 'm', 256, forecast_format='overrides')
        p, original = json.loads(body['prompt']), json.loads(base['prompt'])
        removed = {'candidate_columns', 'candidates', 'forecast_columns', 'forecast_baseline', 'forecast_semantics'}
        self.assertEqual({k: v for k, v in p.items() if k != 'lookup'},
                         {k: v for k, v in original.items() if k not in removed})
        self.assertEqual(p['lookup'], data)
        props = body['format']['properties']
        self.assertEqual(props['candidate_id']['enum'], ['food', 'housing'])
        self.assertEqual(props['comparisons']['items']['properties']['candidate_id']['enum'], ['food', 'housing'])
        self.assertEqual(body['options'], base['options'])
        for key, value in props['comparisons']['items']['properties'].items():
            if key != 'candidate_id':
                self.assertEqual(value, dict(type=['integer', 'null']))

    def test_final_choice_is_legacy_protocol_and_rechecked_against_original_context(self):
        context = self.context()
        data = lookup.materialize_lookup(context, self.query())
        choice = lookup.verified_lookup_choice(context, data, self.answer())
        self.assertEqual(choice, adapter.verified_comparison_choice(context, self.answer()))
        value = self.answer()
        value['comparisons'][0]['food_stocks'] = 0
        with self.assertRaisesRegex(ValueError, 'food_stocks'):
            lookup.verified_lookup_choice(context, data, value)

    def test_final_choice_rejects_an_unqueried_but_otherwise_valid_comparison(self):
        context = self.context()
        data = lookup.materialize_lookup(context, self.query())
        answer = self.answer()
        answer['comparisons'][1] = adapter.comparison_reference(context)['wait']
        with self.assertRaises(ValueError):
            lookup.verified_lookup_choice(context, data, answer)

    def test_tampered_or_stale_lookup_rejected_before_request_or_choice(self):
        context = self.context()
        data = lookup.materialize_lookup(context, self.query())
        variants = []
        for mutate in (lambda d: d.update(context_sha256='bad'),
                       lambda d: d['alternatives'][0]['forecast'].update(population=-1),
                       lambda d: d['alternatives'][0]['comparison_facts'].update(blocked_vs_wait=5),
                       lambda d: d['wait_forecast'].update(culture=False),
                       lambda d: d.update(extra=1)):
            item = copy.deepcopy(data)
            mutate(item)
            variants.append(item)
        for item in variants:
            with self.assertRaises(ValueError):
                lookup.lookup_choice_request_body(context, item, 'm', 256)
            with self.assertRaises(ValueError):
                lookup.verified_lookup_choice(context, item, self.answer())
        context['state']['population_total'] += 1
        with self.assertRaises(ValueError):
            lookup.verified_lookup_choice(context, data, self.answer())

    def test_unknown_fields_not_silently_imputed_and_single_wait_supported(self):
        context = self.context()
        context['candidates'] = [dict(id='wait', ticks=800, forecast={})]
        query = dict(decision_id=5, candidate_ids=['wait'])
        data = lookup.materialize_lookup(context, query)
        self.assertEqual(len(data['wait_forecast']), 20)
        self.assertTrue(all(v is None for v in data['wait_forecast'].values()))
        self.assertIsNone(data['alternatives'][0]['net_treasury_outlay'])
        self.assertIsNone(data['alternatives'][0]['comparison_facts']['blocked_vs_wait'])
        body = lookup.lookup_choice_request_body(context, data, 'm', 256)
        self.assertEqual(body['format']['properties']['comparisons']['minItems'], 1)
        value = dict(decision_id=5, candidate_id='wait', comparisons=[data['alternatives'][0]['comparison_facts']])
        self.assertEqual(lookup.verified_lookup_choice(context, data, value)['candidate_id'], 'wait')

    def test_selection_request_keeps_lookup_and_options_but_has_only_two_output_keys(self):
        context = self.context()
        data = lookup.materialize_lookup(context, self.query())
        before = copy.deepcopy((context, data))
        for fmt in ('rows', 'objects', 'overrides'):
            options = dict(forecast_format=fmt, context_tokens=8192, temperature=.7, top_p=.8, top_k=20, min_p=0.)
            old = lookup.lookup_choice_request_body(context, data, 'm', 256, **options)
            new = lookup.lookup_selection_request_body(context, data, 'm', 256, **options)
            self.assertEqual({k: v for k, v in new.items() if k not in ('system', 'format')},
                             {k: v for k, v in old.items() if k not in ('system', 'format')})
            self.assertEqual(set(new['format']['properties']), {'decision_id', 'candidate_id'})
            self.assertEqual(new['format']['required'], ['decision_id', 'candidate_id'])
            self.assertFalse(new['format']['additionalProperties'])
            self.assertEqual(new['format']['properties']['decision_id']['enum'], [5])
            self.assertEqual(new['format']['properties']['candidate_id']['enum'], ['food', 'housing'])
            self.assertIn('adapter-owned', new['system'])
            self.assertNotIn('Return comparisons quoting', new['system'])
        self.assertEqual((context, data), before)

    def test_selection_evidence_is_explicitly_adapter_owned_and_derived_from_native_context(self):
        context = self.context()
        data = lookup.materialize_lookup(context, self.query())
        before = copy.deepcopy((context, data))
        for selected in data['candidate_ids']:
            value = dict(decision_id=5, candidate_id=selected)
            choice = lookup.adapter_owned_lookup_choice(context, data, value)
            self.assertEqual(set(choice), {'decision_id', 'candidate_id', 'reason'})
            self.assertEqual(choice['candidate_id'], selected)
            self.assertEqual(choice['decision_id'], 5)
            evidence = json.loads(choice['reason'])
            self.assertEqual(evidence, dict(evidence_origin='adapter', context_sha256=lookup.context_fingerprint(context),
                                            requested_ids=['food', 'housing'], native_comparisons=self.answer()['comparisons']))
            self.assertNotIn('verified_comparisons', evidence)
            self.assertLessEqual(len(choice['reason']), 2000)
        self.assertEqual((context, data), before)

    def test_selection_rejects_extra_quotes_rationales_wrong_identity_and_unqueried_ids(self):
        context = self.context()
        data = lookup.materialize_lookup(context, self.query())
        good = dict(decision_id=5, candidate_id='food')
        for value in (None, [], {}, {'decision_id': 5}, {**good, 'decision_id': True},
                      {**good, 'decision_id': 6}, {**good, 'candidate_id': True},
                      {**good, 'candidate_id': 'wait'}, {**good, 'candidate_id': 'unknown'},
                      {**good, 'reason': 'a claim'}, {**good, 'comparisons': self.answer()['comparisons']}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                lookup.adapter_owned_lookup_choice(context, data, value)

    def test_selection_rejects_stale_or_tampered_provenance_in_both_helpers(self):
        context = self.context()
        original = lookup.materialize_lookup(context, self.query())
        value = dict(decision_id=5, candidate_id='food')
        for mutate in (lambda d: d.update(context_sha256='wrong'),
                       lambda d: d['alternatives'][0]['comparison_facts'].update(food_stocks=False),
                       lambda d: d['alternatives'][0]['forecast'].update(population=-1),
                       lambda d: d['wait_forecast'].update(culture=False)):
            data = copy.deepcopy(original)
            mutate(data)
            with self.assertRaises(ValueError):
                lookup.lookup_selection_request_body(context, data, 'm', 256)
            with self.assertRaises(ValueError):
                lookup.adapter_owned_lookup_choice(context, data, value)
        context['state']['population_total'] += 1
        with self.assertRaises(ValueError):
            lookup.adapter_owned_lookup_choice(context, original, value)

    def test_selection_single_wait_keeps_unknown_native_facts_null(self):
        context = self.context()
        context['candidates'] = [dict(id='wait', ticks=800, forecast={})]
        data = lookup.materialize_lookup(context, dict(decision_id=5, candidate_ids=['wait']))
        body = lookup.lookup_selection_request_body(context, data, 'm', 256)
        self.assertEqual(body['format']['properties']['candidate_id']['enum'], ['wait'])
        choice = lookup.adapter_owned_lookup_choice(context, data, dict(decision_id=5, candidate_id='wait'))
        facts = json.loads(choice['reason'])['native_comparisons'][0]
        self.assertIsNone(facts['population'])
        self.assertIsNone(facts['blocked_vs_wait'])
        self.assertEqual(facts['macro_ticks'], 800)

    def test_selection_refuses_oversized_native_evidence_instead_of_truncating(self):
        context = self.context()
        long_id = 'long_' + 'x'*1900
        context['candidates'][1]['id'] = long_id
        data = lookup.materialize_lookup(context, dict(decision_id=5, candidate_ids=[long_id, 'food']))
        with self.assertRaisesRegex(ValueError, 'reason limit'):
            lookup.adapter_owned_lookup_choice(context, data, dict(decision_id=5, candidate_id='food'))

    def test_full_domain_retains_every_compact_field_candidate_order_and_forecast_value(self):
        context = self.context()
        data = lookup.materialize_lookup(context, self.query())
        before = copy.deepcopy((context, data))
        for fmt in ('rows', 'objects', 'overrides'):
            options = dict(forecast_format=fmt, context_tokens=8192, temperature=.7, top_p=.8, top_k=20, min_p=0.)
            base = adapter.request_body(context, 'm', 256, **options)
            body = lookup.full_domain_lookup_selection_request_body(context, data, 'm', 256, **options)
            packed = json.loads(body['prompt'])
            self.assertEqual({k: v for k, v in packed.items() if k != 'lookup'}, json.loads(base['prompt']))
            self.assertEqual(packed['lookup'], data)
            self.assertEqual(body['options'], base['options'])
            schema = body['format']
            self.assertEqual(set(schema['properties']), {'decision_id', 'candidate_id'})
            self.assertEqual(schema['required'], ['decision_id', 'candidate_id'])
            self.assertFalse(schema['additionalProperties'])
            self.assertEqual(schema['properties']['candidate_id']['enum'], ['wait', 'housing', 'food'])
            self.assertEqual(schema['properties']['decision_id']['enum'], [5])
            self.assertIn('any current legal', body['system'])
        self.assertEqual((context, data), before)

    def test_full_domain_accepts_unqueried_selection_without_fabricating_query_or_model_facts(self):
        context = self.context()
        data = lookup.materialize_lookup(context, self.query())
        value = dict(decision_id=5, candidate_id='wait')
        before = copy.deepcopy((context, data, value))
        choice = lookup.adapter_owned_full_domain_choice(context, data, value)
        self.assertEqual(choice['candidate_id'], 'wait')
        self.assertEqual(set(choice), {'decision_id', 'candidate_id', 'reason'})
        evidence = json.loads(choice['reason'])
        expected_wait = dict(candidate_id='wait', macro_ticks=800, forecast_ticks=1600, population=100,
            culture=0, prosperity=0, food_stocks=0, blocked_houses=10, blocked_vs_wait=0)
        self.assertEqual(evidence, dict(evidence_origin='adapter', selection_domain='all_current_candidates',
            context_sha256=lookup.context_fingerprint(context), requested_ids=['food', 'housing'],
            selected_id='wait', native_comparisons=self.answer()['comparisons']+[expected_wait]))
        self.assertEqual((context, data, value), before)
        with self.assertRaises(ValueError):
            lookup.adapter_owned_lookup_choice(context, data, value)

    def test_full_domain_deduplicates_queried_selection_and_rejects_invalid_model_responses(self):
        context = self.context()
        data = lookup.materialize_lookup(context, self.query())
        good = dict(decision_id=5, candidate_id='food')
        evidence = json.loads(lookup.adapter_owned_full_domain_choice(context, data, good)['reason'])
        self.assertEqual(evidence['native_comparisons'], self.answer()['comparisons'])
        for bad in (None, [], {}, {**good, 'decision_id': True}, {**good, 'decision_id': 6},
                    {**good, 'candidate_id': True}, {**good, 'candidate_id': 'unknown'},
                    {**good, 'reason': 'claim'}, {**good, 'comparisons': []}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                lookup.adapter_owned_full_domain_choice(context, data, bad)

    def test_full_domain_revalidates_tampered_and_stale_lookup(self):
        context = self.context()
        original = lookup.materialize_lookup(context, self.query())
        value = dict(decision_id=5, candidate_id='wait')
        for mutate in (lambda d: d.update(context_sha256='bad'),
                       lambda d: d['alternatives'][0]['forecast'].update(population=-1),
                       lambda d: d['wait_forecast'].update(culture=False)):
            data = copy.deepcopy(original)
            mutate(data)
            with self.assertRaises(ValueError):
                lookup.full_domain_lookup_selection_request_body(context, data, 'm', 256)
            with self.assertRaises(ValueError):
                lookup.adapter_owned_full_domain_choice(context, data, value)
        context['state']['population_total'] += 1
        with self.assertRaises(ValueError):
            lookup.adapter_owned_full_domain_choice(context, original, value)

    def test_full_domain_preserves_unknowns_single_wait_and_reason_limit(self):
        context = self.context()
        context['candidates'] = [dict(id='wait', ticks=800, forecast={})]
        data = lookup.materialize_lookup(context, dict(decision_id=5, candidate_ids=['wait']))
        body = lookup.full_domain_lookup_selection_request_body(context, data, 'm', 256)
        self.assertEqual(body['format']['properties']['candidate_id']['enum'], ['wait'])
        choice = lookup.adapter_owned_full_domain_choice(context, data, dict(decision_id=5, candidate_id='wait'))
        self.assertIsNone(json.loads(choice['reason'])['native_comparisons'][0]['population'])
        context = self.context()
        context['candidates'].append(dict(id='x'*1900, ticks=1, forecast={}))
        data = lookup.materialize_lookup(context, self.query())
        with self.assertRaisesRegex(ValueError, 'reason limit'):
            lookup.adapter_owned_full_domain_choice(context, data, dict(decision_id=5, candidate_id='x'*1900))


if __name__ == '__main__':
    unittest.main()
