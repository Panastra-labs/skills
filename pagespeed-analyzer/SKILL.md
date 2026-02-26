---
name: pagespeed-analyzer
description: Run and troubleshoot Google PageSpeed Insights audits using the workspace analyzer at websites/pagespeed_analyzer.py. Use when asked to audit a URL, compare mobile and desktop performance, extract Lighthouse issues and pinpoint evidence, validate API key/setup, or recommend website performance fixes based on PSI output.
---

# PageSpeed Analyzer

## Overview

Use this skill to run repeatable PageSpeed Insights audits through the workspace script at `websites/pagespeed_analyzer.py`, validate setup before execution, and turn PSI output into prioritized fixes.

## Core Workflow

1. Validate setup first.
2. Run the analyzer in `analysis` mode for actionable findings.
3. Use `summary` mode for quick checks and `full` mode only when raw payloads are required.
4. Prioritize fixes from weak categories, failing audits, and pinpoint URL-level evidence.
5. Re-run after changes and compare mobile and desktop deltas.

## Setup And Sanity Check

Run:

```bash
python scripts/check_setup.py
```

The checker verifies:

- `websites/pagespeed_analyzer.py` exists
- Python dependency `requests` is importable
- A usable API key is present in environment or root `.env`

## Run Audits

Use wrapper script:

```bash
python scripts/run_pagespeed.py https://example.com --strategy both --mode analysis --output-format human
```

Direct script invocation (equivalent):

```bash
python ../websites/pagespeed_analyzer.py https://example.com --strategy both --mode analysis --output-format human
```

## Recommended Defaults

- Use `--strategy both` unless user explicitly requests one strategy.
- Use `--mode analysis` for optimization tasks.
- Use `--output-format human` for quick review.
- Use `--output-format json` for automation or downstream parsing.
- Keep retries enabled (`--max-retries 3` or higher for unstable networks).

## Troubleshoot Fast

- HTTP `429`: treat as quota/rate limit; retry later or rotate to a valid key.
- HTTP `5xx` or network errors: rely on backoff flags and retry.
- Missing key errors: add one of `PAGE_SPEED_INSIGHTS_API_KEY`, `PAGESPEED_API_KEY`, or `GOOGLE_API_KEY` to root `.env`.
- Empty/missing audit fields: surface `runtimeError` and continue with available categories and metrics.

## Interpreting Results

- Read `weakCategories` first.
- Then read `issuesByCategory` to find failing audits that affect category scores.
- Use `pinpoint` sections (`renderBlocking`, `unusedJavaScript`, `imageDelivery`, `longTasks`, `scriptTreemap`) to identify exact URLs and byte/time hotspots.
- Prioritize by largest user impact: render-blocking resources, JS waste, heavy images, long tasks, and high transfer payloads.

## References

- [references/command-recipes.md](references/command-recipes.md)
