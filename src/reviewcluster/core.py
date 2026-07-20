from __future__ import annotations

import json
from collections import defaultdict
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

@dataclass(frozen=True)
class ReviewComment:
    file: str
    line: int | None
    body: str


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
                line=item.get("line"),
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


def cluster_comments(comments: Sequence[ReviewComment]) -> dict[str, list[ReviewComment]]:
    grouped: dict[str, list[ReviewComment]] = defaultdict(list)
    for comment in comments:
        grouped[_bucket_for(comment.body)].append(comment)
    return dict(grouped)


def summarize_comments(comments: Sequence[ReviewComment]) -> str:
    buckets = cluster_comments(comments)
    lines = ["# Actionable review map", f"Total comments: {len(comments)}", ""]
    for bucket in sorted(buckets, key=lambda k: (k == "follow-up", k)):
        items = buckets[bucket]
        lines.append(f"## {bucket.title()} ({len(items)})")
        for item in items:
            location = f"{item.file}:{item.line}" if item.line is not None else item.file
            lines.append(f"- {location} — {item.body}")
        lines.append("")
    lines.append("## Suggested next step")
    lines.append("Turn each bucket into one owner, one test, one code change, and one verification command.")
    return "\n".join(lines).rstrip() + "\n"


def to_json_summary(comments: Sequence[ReviewComment]) -> dict[str, object]:
    buckets = cluster_comments(comments)
    return {
        "total_comments": len(comments),
        "buckets": {bucket: [comment.__dict__ for comment in items] for bucket, items in sorted(buckets.items())},
    }
