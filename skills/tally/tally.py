#!/usr/bin/env python3
"""Per-feature token & cost tally, reconstructed from session transcripts.

Read-only: scans the current project's Claude Code transcripts, attributes each
session to a (feature, step), sums the four token types per step, prices them,
and prints a finished table. Transcript contents never leave this script.
"""

import argparse
import glob
import json
import os
import re
import subprocess

TOKEN_TYPES = ("input", "output", "cache_w", "cache_r")
_USAGE_KEYS = {
    "input": "input_tokens",
    "output": "output_tokens",
    "cache_w": "cache_creation_input_tokens",
    "cache_r": "cache_read_input_tokens",
}
_WRITE_TOOLS = {"Write", "Edit", "NotebookEdit"}
_ARTIFACTS = {"spec.md", "plan.md", "tasks.md", "review.md"}
_SPECS_RE = re.compile(r"specs/([^/]+)/([^/\s]+)")
_VERIFICATION_RE = re.compile(r"(?mi)^#{1,6}\s*Verification\b")
PIPELINE_STEPS = ("spec", "plan", "build", "test", "review", "ship")

# USD per 1,000,000 tokens, per model, per token type. Cache-write uses the
# 5-minute ephemeral rate (1.25x input); cache-read is 0.1x input.
AS_OF = "2026-07-05"
PRICES = {
    "claude-opus-4-8": {"input": 5.00, "output": 25.00, "cache_w": 6.25, "cache_r": 0.50},
    "claude-sonnet-5": {"input": 3.00, "output": 15.00, "cache_w": 3.75, "cache_r": 0.30},
    "claude-haiku-4-5": {"input": 1.00, "output": 5.00, "cache_w": 1.25, "cache_r": 0.10},
    "claude-fable-5": {"input": 10.00, "output": 50.00, "cache_w": 12.50, "cache_r": 1.00},
}


def transcript_dir():
    """~/.claude/projects/<encoded-cwd>/ where <encoded-cwd> is cwd with / -> -."""
    encoded = os.getcwd().replace("/", "-")
    return os.path.join(os.path.expanduser("~/.claude/projects"), encoded)


def iter_sessions():
    """Yield (path, [parsed-json-lines]) for each *.jsonl transcript, skipping
    malformed lines safely."""
    for path in sorted(glob.glob(os.path.join(transcript_dir(), "*.jsonl"))):
        records = []
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        yield path, records


def _tool_uses(records):
    """Yield tool_use blocks (dicts) across all assistant messages in a session."""
    for rec in records:
        msg = rec.get("message")
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                yield block


def extract_session(records):
    """Reduce a session's records to the signals attribution needs.

    Returns a dict:
      skill_counts      {attributionSkill: count of records}
      refs              list of (slug, artifact_or_none, kind) where kind in {read, write}
      wrote_artifacts   set of (slug, artifact) written/edited
      checkbox_flip     set of slugs whose tasks.md had a [ ] -> [x] flip
      wrote_verification set of slugs whose artifact gained a "## Verification" section
      usage_by_model    {model: {input, output, cache_w, cache_r}}
    """
    skill_counts = {}
    refs = []
    wrote_artifacts = set()
    checkbox_flip = set()
    wrote_verification = set()
    usage_by_model = {}

    for rec in records:
        skill = rec.get("attributionSkill")
        if skill:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1

        msg = rec.get("message")
        if not isinstance(msg, dict):
            continue

        usage = msg.get("usage")
        model = msg.get("model")
        if isinstance(usage, dict) and model:
            bucket = usage_by_model.setdefault(model, {t: 0 for t in TOKEN_TYPES})
            for t, key in _USAGE_KEYS.items():
                bucket[t] += usage.get(key) or 0

    for block in _tool_uses(records):
        name = block.get("name")
        tool_input = block.get("input")
        if not isinstance(tool_input, dict):
            continue
        file_path = tool_input.get("file_path") or ""
        m = _SPECS_RE.search(file_path)
        if not m:
            continue
        slug, filename = m.group(1), m.group(2)
        artifact = filename if filename in _ARTIFACTS else None

        if name == "Read":
            refs.append((slug, artifact, "read"))
            continue
        if name in _WRITE_TOOLS:
            refs.append((slug, artifact, "write"))
            if artifact:
                wrote_artifacts.add((slug, artifact))
            blob = " ".join(
                str(tool_input.get(k) or "")
                for k in ("content", "new_string", "old_string")
            )
            if artifact == "tasks.md":
                old = str(tool_input.get("old_string") or "")
                new = str(tool_input.get("new_string") or "")
                if "[ ]" in old and "[x]" in new:
                    checkbox_flip.add(slug)
            if _VERIFICATION_RE.search(blob):
                wrote_verification.add(slug)

    return {
        "skill_counts": skill_counts,
        "refs": refs,
        "wrote_artifacts": wrote_artifacts,
        "checkbox_flip": checkbox_flip,
        "wrote_verification": wrote_verification,
        "usage_by_model": usage_by_model,
    }


def resolve_feature(data):
    """Dominant slug for a session: writes weigh more than reads. None if no refs."""
    scores = {}
    for slug, _artifact, kind in data["refs"]:
        scores[slug] = scores.get(slug, 0) + (2 if kind == "write" else 1)
    if not scores:
        return None
    return max(scores, key=lambda s: (scores[s], s))


def resolve_step(data, feature):
    """Step for a session: a pipeline-step attributionSkill wins; else the
    artifact-written fallback chain for `feature`. None if nothing resolves."""
    step_skills = {s: c for s, c in data["skill_counts"].items() if s in PIPELINE_STEPS}
    if step_skills:
        return max(step_skills, key=lambda s: (step_skills[s], PIPELINE_STEPS.index(s)))

    wrote = {a for slug, a in data["wrote_artifacts"] if slug == feature}
    if ("review.md") in wrote:
        return "review"
    if feature in data["wrote_verification"]:
        return "test"
    if feature in data["checkbox_flip"]:
        return "build"
    if "plan.md" in wrote or "tasks.md" in wrote:
        return "plan"
    if "spec.md" in wrote:
        return "spec"
    return None


def specs_dir():
    """The shared specs directory: <git-common-dir>/specs. That location is
    identical from the main tree and every linked/background-isolated worktree
    (they share one .git), and living inside .git means it is never committed.
    Falls back to <cwd>/specs outside a git repo."""
    try:
        common = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        common = ""
    return os.path.join(common, "specs") if common else os.path.join(os.getcwd(), "specs")


def spec_features():
    """Feature slugs that have a specs/<slug>/ directory in the current project."""
    base = specs_dir()
    if not os.path.isdir(base):
        return []
    return sorted(
        name for name in os.listdir(base)
        if os.path.isdir(os.path.join(base, name))
    )


def collect(sessions):
    """Attribute every session, keeping those that resolve to a (feature, step).
    Returns a list of {feature, step, usage_by_model} dicts."""
    resolved = []
    for _path, records in sessions:
        data = extract_session(records)
        feature = resolve_feature(data)
        if not feature:
            continue
        step = resolve_step(data, feature)
        if not step:
            continue
        resolved.append(
            {"feature": feature, "step": step, "usage_by_model": data["usage_by_model"]}
        )
    return resolved


def humanize(n):
    """Token count as a 'k' string, dropping a trailing '.0' (e.g. 17885 -> 17.9k)."""
    s = f"{n / 1000:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    return s + "k"


def features_present(resolved):
    """Sorted set of feature slugs that have at least one attributed session."""
    return sorted({r["feature"] for r in resolved})


def price_usage(usage_by_model):
    """Sum tokens across models and price them. Returns (totals, usd, unpriced):
    totals is summed tokens per type across all models; usd is the dollar cost of
    priced models only; unpriced maps each unknown model to its total token count."""
    totals = {t: 0 for t in TOKEN_TYPES}
    usd = 0.0
    unpriced = {}
    for model, bucket in usage_by_model.items():
        for t in TOKEN_TYPES:
            totals[t] += bucket[t]
        price = PRICES.get(model)
        if price:
            for t in TOKEN_TYPES:
                usd += bucket[t] / 1_000_000 * price[t]
        else:
            unpriced[model] = unpriced.get(model, 0) + sum(bucket.values())
    return totals, usd, unpriced


def _merge_usage(dst, src):
    for model, bucket in src.items():
        acc = dst.setdefault(model, {t: 0 for t in TOKEN_TYPES})
        for t in TOKEN_TYPES:
            acc[t] += bucket[t]


def build_detail(feature, resolved):
    """Render the finished per-step + total table for one feature."""
    mine = [r for r in resolved if r["feature"] == feature]

    # step -> {sessions, usage_by_model}
    by_step = {}
    for r in mine:
        entry = by_step.setdefault(r["step"], {"sessions": 0, "usage": {}})
        entry["sessions"] += 1
        _merge_usage(entry["usage"], r["usage_by_model"])

    header_cols = ["step", "sessions", "input", "output", "cache-w", "cache-r", "USD"]
    rows = []
    grand_usage = {}
    grand_sessions = 0
    unpriced_total = {}

    for step in PIPELINE_STEPS:
        if step not in by_step:
            continue
        entry = by_step[step]
        totals, usd, unpriced = price_usage(entry["usage"])
        rows.append([
            step,
            str(entry["sessions"]),
            humanize(totals["input"]),
            humanize(totals["output"]),
            humanize(totals["cache_w"]),
            humanize(totals["cache_r"]),
            f"${usd:.2f}",
        ])
        grand_sessions += entry["sessions"]
        _merge_usage(grand_usage, entry["usage"])
        for m, tok in unpriced.items():
            unpriced_total[m] = unpriced_total.get(m, 0) + tok

    g_totals, g_usd, _ = price_usage(grand_usage)
    total_row = [
        "total",
        str(grand_sessions),
        humanize(g_totals["input"]),
        humanize(g_totals["output"]),
        humanize(g_totals["cache_w"]),
        humanize(g_totals["cache_r"]),
        f"${g_usd:.2f}",
    ]

    widths = [len(c) for c in header_cols]
    for row in rows + [total_row]:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt(row):
        cells = [row[0].ljust(widths[0])]
        cells += [row[i].rjust(widths[i]) for i in range(1, len(row))]
        return "  " + "  ".join(cells)

    width = len(fmt(header_cols))
    lines = [
        f"specs/{feature}/ — token & cost tally   (prices as of {AS_OF})",
        "",
        fmt(header_cols),
        fmt(rows[0]) if rows else "  (no attributed usage)",
    ]
    for row in rows[1:]:
        lines.append(fmt(row))
    lines.append("  " + "─" * (width - 2))
    lines.append(fmt(total_row))

    if unpriced_total:
        lines.append("")
        for m, tok in sorted(unpriced_total.items()):
            lines.append(f"  ⚠ {m}: {humanize(tok)} tokens counted but unpriced (not in price table)")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Per-feature token & cost tally.")
    parser.add_argument("slug", nargs="?", help="feature slug under specs/ to detail")
    parser.add_argument("--debug", action="store_true", help="dump per-session extraction")
    args = parser.parse_args()

    sessions = list(iter_sessions())

    if args.debug:
        for path, records in sessions:
            data = extract_session(records)
            feature = resolve_feature(data)
            step = resolve_step(data, feature) if feature else None
            print(f"\n{os.path.basename(path)}")
            print(f"  skill_counts: {data['skill_counts']}")
            print(f"  feature: {feature}   step: {step}")
            print(f"  wrote_artifacts: {sorted(data['wrote_artifacts'])}")
            print(f"  usage_by_model: {json.dumps(data['usage_by_model'])}")
        return

    resolved = collect(sessions)

    if args.slug:
        print(build_detail(args.slug, resolved))
        return

    features = spec_features()
    if not features:
        print("No features in flight. Run /spec to start one.")
        return
    if len(features) == 1:
        print(build_detail(features[0], resolved))
        return

    for feature in features:
        mine = [r for r in resolved if r["feature"] == feature]
        _, usd, _ = price_usage(_flatten_usage(mine))
        print(f"  {feature:<20}  {len(mine):>2} sessions  ${usd:,.2f}")
    print("TALLY_MULTIPLE")


def _flatten_usage(resolved):
    merged = {}
    for r in resolved:
        _merge_usage(merged, r["usage_by_model"])
    return merged


if __name__ == "__main__":
    main()
