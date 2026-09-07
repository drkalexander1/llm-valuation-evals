"""Inspect Sonnet open-ended transcripts for ranges vs a single verdict."""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path

from inspect_ai.log import list_eval_logs, read_eval_log

sys.stdout.reconfigure(encoding="utf-8")

DOLLAR = re.compile(r"\$\s*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?:\.[0-9]+)?")
RANGE_HINT = re.compile(
    r"\b(between|range of|from \$?\d|to \$?\d|or so|roughly|approximately|"
    r"around \$?\d|up to|as (?:high|low) as|might go|could go|perhaps)\b",
    re.I,
)


def amounts(text: str) -> list[float]:
    return [float(m.group(1).replace(",", "")) for m in DOLLAR.finditer(text)]


def last_line(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines[-1] if lines else ""


def main() -> None:
    rows: list[dict] = []
    for info in list_eval_logs("logs/pilot"):
        log = read_eval_log(info)
        if "sonnet" not in log.eval.model:
            continue
        for sample in log.samples or []:
            for score in (sample.scores or {}).values():
                meta = score.metadata or {}
                raw = (meta.get("raw") or "").strip()
                ns = amounts(raw)
                taxes = [n for n in ns if n != 100_000]
                rows.append(
                    {
                        "sid": meta.get("scenario_id"),
                        "raw": raw,
                        "taxes": taxes,
                        "unique": sorted(set(taxes)),
                        "last": ns[-1] if ns else None,
                        "bare": len(raw) <= 10,
                        "last_line": last_line(raw),
                        "hint": bool(RANGE_HINT.search(raw)),
                    }
                )

    print(f"n={len(rows)}  bare={sum(r['bare'] for r in rows)}")
    print("distinct non-income $ counts:", Counter(len(r["unique"]) for r in rows))
    print(
        "range-ish language + 2+ taxes:",
        sum(r["hint"] and len(r["unique"]) >= 2 for r in rows),
    )
    print()

    buckets = {
        "bare $N": lambda r: r["bare"],
        "single tax besides income": lambda r: (not r["bare"]) and len(r["unique"]) <= 1,
        "2+ taxes, last line is $N": lambda r: (
            not r["bare"]
            and len(r["unique"]) >= 2
            and DOLLAR.fullmatch(r["last_line"].replace(" ", "")) is not None
            or (not r["bare"] and len(r["unique"]) >= 2 and r["last_line"].startswith("$"))
        ),
        "2+ taxes, last line NOT $N": lambda r: (
            not r["bare"] and len(r["unique"]) >= 2 and not r["last_line"].startswith("$")
        ),
    }

    def last_is_dollar(r: dict) -> bool:
        return bool(re.match(r"^\$\s*[\d,]+(?:\.\d+)?\s*$", r["last_line"]))

    print("=== needs a human look: 2+ distinct taxes and no clean last-line $N ===")
    needs = [
        r
        for r in rows
        if (not r["bare"]) and len(r["unique"]) >= 2 and not last_is_dollar(r)
    ]
    print(f"{len(needs)} of {len(rows)}")
    print()

    by_sid: dict[str, int] = Counter(r["sid"] for r in needs)
    print("by scenario:", dict(by_sid))
    print()

    out = Path("results/sonnet_manual_score.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    chunks: list[str] = []
    for i, r in enumerate(needs, 1):
        header = (
            f"{i}. {r['sid']}  taxes={r['unique']}  last_parsed={r['last']}  "
            f"last_line={r['last_line']!r}  range_hint={r['hint']}"
        )
        print(header)
        print()
        chunks.append(header)
        chunks.append(r["raw"])
        chunks.append("\n" + "=" * 72 + "\n")

    # Also list the clean ones briefly
    clean = [r for r in rows if r not in needs]
    print()
    print(f"=== clean enough for last-$ ({len(clean)}) last-line / unique ===")
    for r in clean:
        kind = "BARE" if r["bare"] else ("one-tax" if len(r["unique"]) <= 1 else "essay+$N")
        print(f"  {kind:<10} {r['sid']:<32} unique={r['unique']} last={r['last']}")

    path = Path("results/sonnet_manual_score.csv")
    fieldnames = [
        "n",
        "scenario",
        "bare",
        "n_distinct_taxes",
        "taxes",
        "last_dollar",
        "last_line",
        "range_hint",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for i, r in enumerate(rows, 1):
            writer.writerow(
                {
                    "n": i,
                    "scenario": r["sid"],
                    "bare": int(r["bare"]),
                    "n_distinct_taxes": len(r["unique"]),
                    "taxes": ", ".join(str(int(x)) for x in r["unique"]),
                    "last_dollar": int(r["last"]) if r["last"] is not None else "",
                    "last_line": r["last_line"],
                    "range_hint": int(r["hint"]),
                }
            )
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
