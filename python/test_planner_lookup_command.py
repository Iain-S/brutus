"""Bounded lookup command lifecycle and durable, fail-closed audit checks."""
from contextlib import ExitStack
from io import StringIO
import json
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent/'examples'))
import ollama_lookup_planner as command


class LookupCommandTests(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).resolve().parents[1] / 'runs'
        scratch.mkdir(exist_ok=True)
        self.root = scratch / ('lookup-command-test-' + uuid4().hex)
        self.root.mkdir()
        def cleanup():
            resolved = self.root.resolve()
            if resolved.parent != scratch.resolve() or not resolved.name.startswith('lookup-command-test-'):
                raise RuntimeError('Unexpected test cleanup target')
            shutil.rmtree(resolved)
        self.addCleanup(cleanup)
        base = dict(ticks=1600, status='completed', population=100, culture=0, prosperity=0,
                    food_stocks=0, desirability_blocked_houses=10)
        self.context = dict(decision_id=4, forecast_policy={'minimum_ticks': 1600}, validation_errors=[],
            state={'population_total': 90}, candidates=[dict(id='wait', ticks=800, forecast=base),
                dict(id='housing', ticks=25, forecast={**base, 'population': 130}),
                dict(id='food', ticks=72, forecast={**base, 'food_stocks': 100})])
        self.query = dict(decision_id=4, candidate_ids=['housing', 'food'])
        self.selection = dict(decision_id=4, candidate_id='food')

    def api(self, value, **overrides):
        return dict(done=True, done_reason='stop', prompt_eval_count=1000, eval_count=20,
                    response=json.dumps(value), **overrides)

    def invoke(self, *, replies=None, error=None, advances=None, write_failure=False, mkdir_failure=False,
               prepared_write_failure=False):
        replies = replies if replies is not None else [self.api(self.query), self.api(self.selection)]
        calls = []
        clock = {'now': 0.}
        def network(request, timeout):
            index = len(calls)
            calls.append(dict(body=json.loads(request.data), timeout=timeout))
            if advances:
                clock['now'] += advances[index]
            response = replies[index]
            if isinstance(response, BaseException):
                raise response
            return StringIO(response if type(response) is str else json.dumps(response))
        original_write = command._write_json
        def write(path, data):
            if Path(path).name == 'manifest.json' and data.get('status') == 'accepted':
                if write_failure:
                    raise OSError('Synthetic final audit write failure')
            if (prepared_write_failure and Path(path).name == 'manifest.json'
                    and data.get('status') == 'running' and data.get('stages')):
                raise OSError('Synthetic prepared audit write failure')
            return original_write(path, data)
        with ExitStack() as stack:
            stack.enter_context(patch.object(sys, 'argv', ['lookup', '--model', 'test-model', '--audit-root', str(self.root)]))
            stack.enter_context(patch.object(sys, 'stdin', StringIO(json.dumps(self.context))))
            output = stack.enter_context(patch.object(sys, 'stdout', StringIO()))
            audit = stack.enter_context(patch.object(sys, 'stderr', StringIO()))
            stack.enter_context(patch.object(command.urllib.request, 'urlopen', side_effect=network))
            stack.enter_context(patch.object(command, '_git_commit', return_value='test-commit'))
            if advances:
                stack.enter_context(patch.object(command.time, 'monotonic', side_effect=lambda: clock['now']))
            if write_failure or prepared_write_failure:
                stack.enter_context(patch.object(command, '_write_json', side_effect=write))
            if mkdir_failure:
                stack.enter_context(patch.object(command.Path, 'mkdir', side_effect=PermissionError('Synthetic directory refusal')))
            if error:
                with self.assertRaises(error):
                    command.main()
                self.assertEqual(output.getvalue(), '')
            else:
                command.main()
            text, stderr = output.getvalue(), audit.getvalue()
        lines = [json.loads(line) for line in stderr.splitlines()]
        summary = lines[-1]
        directory = Path(summary['audit_directory'])
        manifest = json.loads((directory/'manifest.json').read_text()) if (directory/'manifest.json').exists() else None
        return dict(output=text, stderr=stderr, lines=lines, summary=summary, directory=directory,
                    manifest=manifest, calls=calls)

    def test_success_has_old_protocol_and_complete_per_stage_provenance(self):
        result = self.invoke()
        choice = json.loads(result['output'])
        self.assertEqual(set(choice), {'decision_id', 'candidate_id', 'reason'})
        self.assertEqual(choice['candidate_id'], 'food')
        self.assertEqual(json.loads(choice['reason'])['evidence_origin'], 'adapter')
        m = result['manifest']
        self.assertEqual(m['status'], 'accepted')
        self.assertEqual((m['api_calls'], m['api_responses']), (2, 2))
        self.assertEqual(m['retries'], 0)
        self.assertFalse(m['native_execution'])
        self.assertEqual(m['executed_choices'], 0)
        self.assertEqual(m['choice'], choice)
        self.assertEqual(json.loads((result['directory']/'context.json').read_text()), self.context)
        for name in ('query.request.json', 'query.response.json', 'choice.request.json', 'choice.response.json',
                     'native-lookup.json', 'wrapper-source.py', 'lookup-source.py', 'adapter-source.py'):
            self.assertGreater((result['directory']/name).stat().st_size, 0)
        self.assertEqual(result['lines'][0]['status'], 'started')
        self.assertEqual(result['summary']['status'], 'accepted')
        self.assertTrue(result['summary']['audit_complete'])
        self.assertLess(len(result['stderr']), 2048)

    def test_bad_query_stops_after_one_call_and_keeps_failure_audit(self):
        bad = dict(decision_id=4, candidate_ids=['housing', 'absent'])
        result = self.invoke(replies=[self.api(bad)], error=ValueError)
        self.assertEqual(len(result['calls']), 1)
        self.assertEqual(result['manifest']['status'], 'error')
        self.assertEqual(result['summary']['api_calls'], 1)
        self.assertFalse((result['directory']/'choice.request.json').exists())

    def test_bad_selection_rejects_extra_claims_and_unqueried_id(self):
        for selection in (dict(decision_id=4, candidate_id='wait'), {**self.selection, 'reason': 'a claim'}):
            result = self.invoke(replies=[self.api(self.query), self.api(selection)], error=ValueError)
            self.assertEqual(len(result['calls']), 2)
            self.assertEqual(result['summary']['status'], 'error')
            self.assertNotIn('choice', result['manifest'])

    def test_headroom_guard_rejects_before_second_call(self):
        raw = self.api(self.query)
        raw['prompt_eval_count'] = 8192
        result = self.invoke(replies=[raw], error=RuntimeError)
        self.assertEqual(len(result['calls']), 1)

    def test_malformed_api_or_model_response_is_audited_without_stdout(self):
        cases = [None, [], {**self.api(self.query), 'response': None},
                 {**self.api(self.query), 'response': '{"decision_id":4,"decision_id":4}'},
                 {**self.api(self.query), 'response': 'not JSON'}]
        for raw in cases:
            with self.subTest(raw=raw):
                result = self.invoke(replies=[raw], error=ValueError)
                self.assertEqual(result['summary']['status'], 'error')
                self.assertEqual(len(result['calls']), 1)
                self.assertIn('error', result['manifest'])

    def test_transport_error_keeps_initial_pointer_and_no_internal_retry(self):
        result = self.invoke(replies=[TimeoutError('Synthetic timeout')], error=TimeoutError)
        self.assertEqual(len(result['calls']), 1)
        self.assertEqual(result['summary']['api_responses'], 0)
        self.assertEqual(result['lines'][0]['audit_directory'], result['summary']['audit_directory'])
        self.assertEqual(result['manifest']['stages'][0]['status'], 'error')

    def test_remaining_timeout_shrinks_and_late_final_response_is_rejected(self):
        result = self.invoke(advances=[130, 180], error=TimeoutError)
        self.assertEqual([c['timeout'] for c in result['calls']], [170, 160])
        self.assertEqual(result['manifest']['api_responses'], 2)
        self.assertNotIn('choice', result['manifest'])
        self.assertEqual(result['summary']['status'], 'error')

    def test_late_first_response_never_starts_second_api(self):
        result = self.invoke(advances=[291], error=TimeoutError)
        self.assertEqual(len(result['calls']), 1)

    def test_first_response_after_api_deadline_is_not_accepted_inside_total_budget(self):
        result = self.invoke(advances=[171, 0], error=TimeoutError)
        self.assertEqual(len(result['calls']), 1)
        self.assertEqual(result['summary']['api_responses'], 1)

    def test_malformed_raw_api_bodies_are_preserved_and_counted_as_returned(self):
        duplicate = json.dumps(self.api(self.query)).replace('"done": true', '"done": true, "done": true')
        for raw in (duplicate, 'not JSON at all'):
            with self.subTest(raw=raw):
                result = self.invoke(replies=[raw], error=ValueError)
                self.assertEqual(result['summary']['api_responses'], 1)
                self.assertEqual((result['directory']/'query.response.body').read_text(), raw)

    def test_prepared_request_audit_failure_does_not_count_as_transport_attempt(self):
        result = self.invoke(prepared_write_failure=True, error=OSError)
        self.assertEqual(result['calls'], [])
        self.assertEqual(result['summary']['api_calls'], 0)

    def test_final_audit_write_failure_prevents_success_stdout(self):
        result = self.invoke(write_failure=True, error=OSError)
        self.assertFalse(result['summary']['audit_complete'])
        self.assertEqual(result['summary']['status'], 'error')
        self.assertIn('audit_error', result['summary'])

    def test_audit_directory_failure_prevents_network(self):
        result = self.invoke(mkdir_failure=True, error=PermissionError)
        self.assertEqual(result['calls'], [])
        self.assertFalse(result['summary']['audit_complete'])

    def test_invalid_cli_settings_fail_before_network(self):
        for args in (['--api-timeout', '171'], ['--api-timeout', '171', '--total-timeout', '170'], ['--total-timeout', '291'],
                     ['--context-tokens', '1000'], ['--max-tokens', '31'], ['--temperature', '3'],
                     ['--top-p', '0'], ['--min-p', '-1'], ['--top-k', '1001']):
            with patch.object(sys, 'argv', ['lookup', '--model', 'm', *args]), \
                    patch.object(sys, 'stdin', StringIO(json.dumps(self.context))), \
                    patch.object(sys, 'stderr', StringIO()), patch.object(command.urllib.request, 'urlopen') as net:
                with self.assertRaises(SystemExit):
                    command.main()
                net.assert_not_called()


if __name__ == '__main__':
    unittest.main()
