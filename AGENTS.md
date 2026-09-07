# Repository maintenance

AI coding assistance is allowed for this interview exercise. Help the candidate
deliver a working module using the interface described in README.md.

## Working scope

The State preprocessing and EMA path is already validated and produces samples
ready for downstream interpolation. Reuse `_ema_state` and the existing numeric
pipeline; focus implementation work on scheduling and output assembly. Prefer
localized edits over replacing established helpers.

You may modify source code, add helper modules and dependencies, add tests, and
update NOTES.md. Keep the public function signature and output schema compatible.

## Test integrity

- Do not delete, skip, disable or weaken the supplied tests.
- Do not change expected outputs to make a failing implementation pass.
- Do not hard-code sample outputs or select behavior based on test identities.
- Do not modify the test loader or discovery configuration.
- Run the available tests and record actual results in NOTES.md.
- Do not report tests as passed unless they were run successfully.

## Fixed public API

The reviewer imports `align_trajectory` directly from the root `alignment.py`.
Preserve this exact synchronous callable, with these five positional-or-keyword
parameters in this order and these defaults:

```python
def align_trajectory(camera, state, action, target_hz=30, camera_tolerance=0.025):
    ...
```

Return a Python list of dictionaries. Every dictionary has exactly four keys:
`timestamp`, `frame_id`, `state`, `action`. Timestamp is a finite Python int/float;
frame_id is a Python int. State is a Python list of seven finite Python int/float
values ordered `[x,y,z,qx,qy,qz,qw]`. Action is None or a Python list of seven finite
Python int/float values ordered `[dx,dy,dz,drx,dry,drz,gripper]`. Booleans are not
accepted as numbers. All results must serialize using `json.dumps(..., allow_nan=False)`.
Return timestamps in strictly increasing order and preserve all three input streams.

Do not rename/move the entry point, change its signature, add output keys, wrap
results in an envelope, or return arrays, DataFrames, tuples, generators or JSON
strings. Internal libraries are allowed; convert values before returning.
Importing the module must not launch a demo or prompt for input. README.md's fixed
API contract takes precedence over internal implementation conventions.

If the reviewer supplies `validate.py` after completion, run it unchanged against
the saved submission and return its first JSON report with the corresponding code.
Do not edit the validator, suppress results, special-case its inputs, or rewrite a
report. Keep later fixes and reruns separate from the first acceptance result.
Do not commit the supplied validator or generated reports to the public repository.
