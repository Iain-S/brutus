"""Optional forecast evidence checks preserve choices without trusting rationales."""
import copy
import importlib.util
from io import StringIO
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('evidence_adapter', Path(__file__).parent/'examples/ollama_planner.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class VerifiedComparisonsTests(unittest.TestCase):
    def context(self):
        base = dict(ticks=1600, population=100, culture=0, prosperity=0,
                    food_stocks=0, desirability_blocked_houses=10)
        return {'decision_id': 5, 'forecast_policy': {'minimum_ticks': 1600},
                'state': {'population_total': 90}, 'objective': 'Win in minimum ticks',
                'candidates': [dict(id='wait', ticks=800, forecast=base),
                               dict(id='housing', ticks=25, forecast={**base, 'population': 130,
                                                                    'desirability_blocked_houses': 15}),
                               dict(id='food', ticks=72, forecast={**base, 'food_stocks': 100})]}

    def answer(self):
        return {'comparisons': [
            dict(candidate_id='housing', macro_ticks=25, forecast_ticks=1600, population=130, culture=0,
                 prosperity=0, food_stocks=0, blocked_houses=15, blocked_vs_wait=5),
            dict(candidate_id='food', macro_ticks=72, forecast_ticks=1600, population=100, culture=0,
                 prosperity=0, food_stocks=100, blocked_houses=10, blocked_vs_wait=0)],
            'decision_id': 5, 'candidate_id': 'housing'}

    def test_request_schema_keeps_all_candidates_options_and_input(self):
        context = self.context()
        before = copy.deepcopy(context)
        for fmt in ('rows', 'objects', 'overrides'):
            options = dict(forecast_format=fmt, context_tokens=8192, temperature=.7, top_p=.8, top_k=20, min_p=0.)
            baseline = adapter.request_body(context, 'model', 256, **options)
            body = adapter.request_body(context, 'model', 256, verify_comparisons=True, **options)
            self.assertEqual(body['prompt'], baseline['prompt'])
            self.assertEqual(body['options'], baseline['options'])
            schema = body['format']
            self.assertEqual(list(schema['properties']), ['comparisons', 'decision_id', 'candidate_id'])
            self.assertEqual(schema['required'], list(schema['properties']))
            self.assertFalse(schema['additionalProperties'])
            self.assertEqual(schema['properties']['candidate_id'], baseline['format']['properties']['candidate_id'])
            comparison = schema['properties']['comparisons']
            self.assertEqual((comparison['minItems'], comparison['maxItems']), (2, 2))
            self.assertFalse(comparison['items']['additionalProperties'])
            props = comparison['items']['properties']
            self.assertEqual(props['candidate_id']['enum'], ['wait', 'housing', 'food'])
            for key, value in props.items():
                if key != 'candidate_id':
                    self.assertEqual(value, {'type': ['integer', 'null']})
            self.assertNotIn('under eight words', body['system'])
            self.assertNotIn('under 100 words', body['system'])
            self.assertIn('blocked_vs_wait', body['system'])
        self.assertEqual(context, before)

    def test_disabled_profile_leaves_legacy_requests_unchanged(self):
        for fmt in ('rows', 'objects', 'overrides'):
            for reason in (False, True):
                options = dict(forecast_format=fmt, reason_first=reason)
                self.assertEqual(json.dumps(adapter.request_body(self.context(), 'm', 256, **options)),
                                 json.dumps(adapter.request_body(self.context(), 'm', 256,
                                                               verify_comparisons=False, **options)))

    def test_valid_evidence_translates_to_old_protocol_without_model_reason(self):
        context, value = self.context(), self.answer()
        before = copy.deepcopy((context, value))
        choice = adapter.verified_comparison_choice(context, value)
        self.assertEqual(set(choice), {'decision_id', 'candidate_id', 'reason'})
        self.assertEqual(choice['decision_id'], 5)
        self.assertEqual(choice['candidate_id'], 'housing')
        self.assertEqual(json.loads(choice['reason']), {'verified_comparisons': value['comparisons']})
        self.assertLessEqual(len(choice['reason']), 2000)
        self.assertEqual((context, value), before)

    def test_model_can_compare_and_choose_any_legal_ids_in_any_order(self):
        context = self.context()
        ref = adapter.comparison_reference(context)
        for selected in ref:
            other = next(k for k in ref if k != selected)
            value = dict(decision_id=5, candidate_id=selected,
                         comparisons=[ref[other], ref[selected]])
            self.assertEqual(adapter.verified_comparison_choice(context, value)['candidate_id'], selected)

    def test_unknowns_remain_null_and_single_wait_is_supported(self):
        context = self.context()
        context['candidates'] = [context['candidates'][0]]
        context['candidates'][0]['forecast'] = {}
        row = dict(candidate_id='wait', macro_ticks=800, forecast_ticks=None, population=None, culture=None,
                   prosperity=None, food_stocks=None, blocked_houses=None, blocked_vs_wait=None)
        value = dict(comparisons=[row], decision_id=5, candidate_id='wait')
        body = adapter.request_body(context, 'm', 256, verify_comparisons=True)
        self.assertEqual(body['format']['properties']['comparisons']['minItems'], 1)
        self.assertEqual(adapter.verified_comparison_choice(context, value)['candidate_id'], 'wait')
        bad = copy.deepcopy(value)
        bad['comparisons'][0]['population'] = 0
        with self.assertRaises(ValueError):
            adapter.verified_comparison_choice(context, bad)

    def test_every_quoted_fact_mismatch_is_rejected_not_corrected(self):
        for key in self.answer()['comparisons'][0]:
            if key == 'candidate_id':
                continue
            value = self.answer()
            value['comparisons'][0][key] += 1
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, key):
                adapter.verified_comparison_choice(self.context(), value)

    def test_invalid_values_types_keys_counts_and_ids_are_rejected(self):
        mutations = [lambda v: v.update(decision_id=True), lambda v: v.update(decision_id=6),
                     lambda v: v.update(candidate_id='absent'), lambda v: v.update(candidate_id='wait'),
                     lambda v: v.update(reason='Unverified'), lambda v: v.pop('comparisons'),
                     lambda v: v.update(comparisons=[]), lambda v: v.update(comparisons=v['comparisons'][:1]),
                     lambda v: v['comparisons'].append(copy.deepcopy(v['comparisons'][0])),
                     lambda v: v['comparisons'].__setitem__(1, copy.deepcopy(v['comparisons'][0])),
                     lambda v: v['comparisons'][0].update(candidate_id='absent'),
                     lambda v: v['comparisons'][0].pop('population'),
                     lambda v: v['comparisons'][0].update(extra=1)]
        for scalar in (True, 130.0, '130', None):
            mutations.append(lambda v, scalar=scalar: v['comparisons'][0].update(population=scalar))
        for mutate in mutations:
            value = self.answer()
            mutate(value)
            with self.subTest(value=value), self.assertRaises(ValueError):
                adapter.verified_comparison_choice(self.context(), value)
        for value in (None, [], 'bad', 1):
            with self.assertRaises(ValueError):
                adapter.verified_comparison_choice(self.context(), value)

    def test_bad_reference_or_conflicting_profile_fails_before_inference(self):
        mutations = [lambda c: c.pop('forecast_policy'), lambda c: c['candidates'].pop(0),
                     lambda c: c['candidates'].append(copy.deepcopy(c['candidates'][0])),
                     lambda c: c['candidates'][0].pop('forecast'),
                     lambda c: c['candidates'][0]['forecast'].update(population=True),
                     lambda c: c['candidates'][1].update(ticks=25.0)]
        for mutate in mutations:
            context = self.context()
            mutate(context)
            with self.assertRaises(ValueError):
                adapter.request_body(context, 'm', 256, verify_comparisons=True)
        with self.assertRaises(ValueError):
            adapter.request_body(self.context(), 'm', 256, verify_comparisons=True, reason_first=True)

    def cli(self, value=None, *, tokens=100, raw=None, error=None, result_changes=None, omit_response=False):
        result = dict(done=True, done_reason='stop', prompt_eval_count=tokens, eval_count=160,
                      response=json.dumps(value if value is not None else self.answer()) if raw is None else raw)
        result.update(result_changes or {})
        if omit_response:
            result.pop('response')
        argv = ['adapter', '--model', 'test', '--verify-comparisons', '--forecast-format', 'overrides',
                '--max-tokens', '256', '--context-tokens', '8192']
        with patch.object(sys, 'argv', argv), patch.object(sys, 'stdin', StringIO(json.dumps(self.context()))), \
                patch.object(sys, 'stdout', StringIO()) as output, patch.object(sys, 'stderr', StringIO()) as audit, \
                patch.object(adapter.urllib.request, 'urlopen', return_value=StringIO(json.dumps(result))) as network:
            if error:
                with self.assertRaises(error):
                    adapter.main()
                self.assertEqual(output.getvalue(), '')
            else:
                adapter.main()
            self.assertEqual(network.call_count, 1)
            metadata = json.loads(audit.getvalue())
            self.assertTrue(metadata['verify_comparisons'])
            return output.getvalue(), metadata

    def test_cli_translates_and_audits_verified_comparisons(self):
        output, audit = self.cli()
        self.assertEqual(json.loads(output), adapter.verified_comparison_choice(self.context(), self.answer()))
        self.assertEqual(audit['comparison_validation'], 'accepted')
        self.assertEqual(audit['comparisons'], self.answer()['comparisons'])

    def test_cli_rejects_wrong_facts_without_stdout_and_audits_error(self):
        value = self.answer()
        value['comparisons'][0]['blocked_vs_wait'] = -5
        _, audit = self.cli(value, error=ValueError)
        self.assertEqual(audit['comparison_validation'], 'rejected')
        self.assertIn('blocked_vs_wait', audit['validation_error'])

    def test_cli_still_rejects_context_headroom_without_comparison_acceptance(self):
        _, audit = self.cli(tokens=8192, error=RuntimeError)
        self.assertEqual(audit['comparison_validation'], 'not_run')

    def test_cli_rejects_duplicate_json_keys(self):
        raw = json.dumps(self.answer()).replace('"decision_id": 5', '"decision_id": 5, "decision_id": 5')
        _, audit = self.cli(raw=raw, error=ValueError)
        self.assertEqual(audit['comparison_validation'], 'rejected')

    def test_cli_audits_malformed_or_missing_api_response(self):
        for response in (None, {}, [], 17):
            with self.subTest(response=response):
                _, audit = self.cli(result_changes={'response': response}, error=ValueError)
                self.assertEqual(audit['comparison_validation'], 'rejected')
                self.assertIn('JSON string', audit['validation_error'])
        _, audit = self.cli(omit_response=True, error=ValueError)
        self.assertIn('JSON string', audit['validation_error'])

    def test_cli_conflicting_flags_fail_without_network(self):
        with patch.object(sys, 'argv', ['a', '--model', 'm', '--verify-comparisons', '--reason-first']), \
                patch.object(sys, 'stderr', StringIO()), patch.object(adapter.urllib.request, 'urlopen') as network:
            with self.assertRaises(SystemExit):
                adapter.main()
            network.assert_not_called()


if __name__ == '__main__':
    unittest.main()
