# actionable-review-clusterer

## Pain point
Review comments often arrive as a noisy pile. Engineers waste time guessing which comments are bugs, tests, security, docs, or pure style nitpicks.

## Why now
AI review comments and faster code review workflows are trending hard; the biggest gap is not generating comments, but converting them into a concrete execution plan.

## Install
```bash
python -m venv .venv
. .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
pip install -e .
```

## Run
```bash
python -m reviewcluster examples/comments.json
cat examples/comments.json | python -m reviewcluster --json
```

## Example
Input:
```json
[{"file":"app.py","line":12,"body":"Add a test for the retry path"}]
```
Output:
```text
# Actionable review map
Total comments: 1
...
```

## Priorities and owner hints
The clusterer now orders review buckets by delivery risk and includes suggested file owners:

- `P0`: security findings
- `P1`: likely bugs
- `P2`: tests and performance
- `P3`: docs, style, and follow-up work

Markdown output includes a `Suggested owners by file` section. JSON output includes `bucket_order`, `owners_by_file`, and per-bucket `priority` metadata so another automation can turn review comments into an execution queue.

## Roadmap
- Add richer keyword heuristics and semantic clustering.
- Export GitHub review thread IDs and owner assignments.
- Emit markdown suitable for PR comments.

## License
MIT