# Pydantic AI ToolOutput Spike

The user requests a small ToolOutput experiment before any migration. Use an
ignored temporary environment under `runs/`, created from the canonical training
interpreter with system packages visible. Install only the OpenAI extra of
Pydantic AI slim there; record exact versions, interpreter and package checks.
Do not change training dependencies, historical helpers or the live planner.

## Predeclared Experiment

Use decision 3 from the existing immutable order archive. Retain all three native
alternatives and their original order/facts. Preserve the old system/prompt text;
Pydantic AI's tool definition and chat transport are new protocol components.
This is a protocol feasibility spike, not a clean single-variable comparison
with the old generate endpoint or proof of improved selection quality.

Expose one output tool with exactly decision_id=3 and candidate_id in
compound/single/wait, forbid extra fields and coercion. Independently check raw
tool arguments with the existing selection validator; never parse thinking as
the answer. No executable game tools are registered.

Maximum two inference attempts: instruct control (256 output tokens, think=False),
then thinking candidate (1536 tokens, think=True) only if the control passes.
Both use 8192 context, seed 20261122, temperature .7, top_p .8, top_k 20, min_p 0.
Use a killable worker with a 170-second total deadline per attempt, output and
provider retries disabled, and request_limit=1. Capture actual outbound HTTP
requests and raw responses before provider parsing, including partial failure.
Stop after any failed condition; no retry, budget increase or output salvage.

Record installed model identity/defaults before and after; copy/revalidate the
pinned source archive and retain executed spike source and package versions.
Accept only a complete successful raw response, one correctly named output tool,
valid exact arguments and a matching Pydantic AI result. Preserve raw reasoning
as unverified output. Check actual outgoing settings: a setting silently ignored
by the compatibility endpoint must be reported as a limitation, not presumed
effective. Native generation telemetry may differ on the chat endpoint.

The throwaway runner and raw evidence remain in ignored `runs/`; tracked results
and this plan retain their paths. Do a transport dry run with synthetic replies
to verify no extra calls, wrong-channel rejection and strict argument validation
before inference. Independently audit the actual requests/results afterward.

## Ledger

- [x] Install isolated dependencies, inspect actual installed interfaces.
- [x] Prepare throwaway runner and verify captured outbound request/validation
  with mock HTTP only. No native environment and no model calls in dry runs.
- [ ] Execute at most two real attempts; preserve all failures and raw evidence.
- [ ] Record independently checked result and integration recommendation;
  commit/push documentation only, preserving unrelated staged files.

Official references:
[ToolOutput](https://pydantic.dev/docs/ai/core-concepts/output/),
[Ollama provider](https://pydantic.dev/docs/ai/models/ollama/).

Installed Pydantic AI slim 2.71.0, Pydantic 2.14.4, OpenAI SDK 3.57.0 and httpx2
2.16.2 in the temporary environment. Its `pip check` passes. Four synthetic HTTP
cases accept valid tool arguments and reject thinking-only output, invented IDs
and extra fields, with exactly one simulated request each and no retries.
Dry-run archive:
`runs/planner-input-probes/2026-11-23/20261123T082751.187117Z_pydantic-dry_ba4124f7/`.
Runner: `runs/pydantic_tooloutput_spike.py`; a copy/hash is retained per archive.

Compatibility ruling before inference: installed Ollama 0.16.2's
[request conversion](https://github.com/ollama/ollama/blob/v0.16.2/openai/openai.go)
does not accept `num_ctx`, `top_k`, `min_p` or boolean `think` on the compatibility
endpoint. Use unique temporary local aliases of the existing models with only
num_ctx=8192, top_k=20 and min_p=0 overridden, verifying unchanged weight blob,
template and all other defaults. Remove only those new aliases afterward.
Request reasoning_effort=none for instruct and medium for thinking through the
supported compatibility field; this is not a boolean-think ablation. Tool choice
is requested by the client, but this old server's request struct does not enforce
it. Record actual returned tool calls rather than presume constrained generation.
