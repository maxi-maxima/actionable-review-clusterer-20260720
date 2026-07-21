from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Sequence

KEYWORDS = {
    "tests": ["test", "coverage", "regression", "assert"],
    "security": ["secret", "token", "auth", "cookie", "csrf", "xss", "injection"],
    "performance": ["slow", "perf", "latency", "memory", "cpu", "cache"],
    "docs": ["readme", "docs", "comment", "typo", "wording"],
    "bug": ["bug", "fail", "error", "crash", "null", "race", "broken"],
    "style": ["naming", "style", "lint", "format", "whitespace"],
}

PRIORITY = {
    "security": 0,
    "bug": 1,
    "tests": 2,
    "performance": 3,
    "docs": 4,
    "style": 5,
    "follow-up": 6,
}

PRIORITY_LABELS = {
    "security": "P0",
    "bug": "P1",
    "tests": "P2",
    "performance": "P2",
    "docs": "P3",
    "style": "P3",
    "follow-up": "P3",
}


@dataclass(frozen=True)
class ReviewComment:
    file: str
    line: int | None
    body: str


def _coerce_line(value: object) -> int | None:
    if value in (None, ""):
        return None
    try:
        line = int(value)
    except (TypeError, ValueError):
        return None
    return line if line > 0 else None


def load_comments(raw: str) -> list[ReviewComment]:
    payload = json.loads(raw)
    if not isinstance(payload, list):
        raise ValueError("input must be a JSON array")
    comments: list[ReviewComment] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("each comment must be an object")
        body = str(item.get("body", "")).strip()
        if not body:
            continue
        comments.append(
            ReviewComment(
                file=str(item.get("file", "<unknown>")),
                line=_coerce_line(item.get("line")),
                body=body,
            )
        )
    return comments


def _bucket_for(text: str) -> str:
    lowered = text.lower()
    for bucket, words in KEYWORDS.items():
        if any(word in lowered for word in words):
            return bucket
    return "follow-up"


def _ordered_bucket_names(buckets: dict[str, list[ReviewComment]]) -> list[str]:
    return sorted(buckets, key=lambda bucket: (PRIORITY.get(bucket, 99), bucket))


def cluster_comments(comments: Sequence[ReviewComment]) -> dict[str, list[ReviewComment]]:
    grouped: dict[str, list[ReviewComment]] = defaultdict(list)
    for comment in comments:
        grouped[_bucket_for(comment.body)].append(comment)
    return dict(grouped)


def owner_suggestions(comments: Sequence[ReviewComment]) -> dict[str, str]:
    """Suggest an owner bucket per file using the dominant comment theme."""
    by_file: dict[str, Counter[str]] = defaultdict(Counter)
    for comment in comments:
        by_file[comment.file][_bucket_for(comment.body)] += 1
    return {
        file: counts.most_common(1)[0][0]
        for file, counts in sorted(by_file.items())
    }


def summarize_comments(comments: Sequence[ReviewComment]) -> str:
    buckets = cluster_comments(comments)
    lines = ["# Actionable review map", f"Total comments: {len(comments)}", ""]
    for bucket in _ordered_bucket_names(buckets):
        items = buckets[bucket]
        lines.append(f"## {bucket.title()} ({len(items)}) — {PRIORITY_LABELS.get(bucket, 'P3')}")
        for item in items:
            location = f"{item.file}:{item.line}" if item.line is not None else item.file
            lines.append(f"- {location} — {item.body}")
        lines.append("")
    owners = owner_suggestions(comments)
    if owners:
        lines.append("## Suggested owners by file")
        for file, bucket in owners.items():
            lines.append(f"- {file}: {bucket}")
        lines.append("")
    lines.append("## Suggested next step")
    lines.append("Start with the highest priority bucket, assign one owner per affected file, add or update tests, then record the verification command next to the resolved review thread.")
    return "\n".join(lines).rstrip() + "\n"


def to_json_summary(comments: Sequence[ReviewComment]) -> dict[str, object]:
    buckets = cluster_comments(comments)
    return {
        "total_comments": len(comments),
        "bucket_order": _ordered_bucket_names(buckets),
        "owners_by_file": owner_suggestions(comments),
        "buckets": {
            bucket: {
                "priority": PRIORITY_LABELS.get(bucket, "P3"),
                "comments": [comment.__dict__ for comment in items],
            }
            for bucket, items in sorted(buckets.items(), key=lambda item: (PRIORITY.get(item[0], 99), item[0]))
        },
    }
