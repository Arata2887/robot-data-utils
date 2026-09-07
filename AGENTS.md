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
