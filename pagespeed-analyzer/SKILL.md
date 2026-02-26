---
name: pagespeed-analyzer
description: Run and troubleshoot Google PageSpeed Insights audits with a local pagespeed_analyzer.py script. Use when asked to audit a URL, compare mobile and desktop performance, extract Lighthouse issues and pinpoint evidence, set up PageSpeed API credentials, or recommend website performance fixes from PSI output.
---

# PageSpeed Analyzer

## Overview

Use this skill to run repeatable PageSpeed Insights audits through a local `pagespeed_analyzer.py` script and turn PSI output into prioritized fixes.

## Prerequisites

1. Install Python dependencies:

```bash
pip install -r scripts/requirements.txt
```

2. Create a Google API key for PageSpeed Insights:

1. Open Google Cloud Console.
2. Create or select a project.
3. Go to `APIs & Services` -> `Library`.
4. Enable `PageSpeed Insights API`.
5. Go to `APIs & Services` -> `Credentials`.
6. Create an API key.

3. Export one of these environment variables (preferred first):

```bash
PAGE_SPEED_INSIGHTS_API_KEY=your_key_here
PAGESPEED_API_KEY=your_key_here
```

Do not rely on Gemini-specific keys for this skill.

## Core Workflow

1. Run the analyzer in `analysis` mode for actionable findings.
2. Start with both strategies unless the user asks for one.
3. Use `summary` mode for quick checks and `full` mode only when raw payloads are required.
4. Prioritize fixes from weak categories, failing audits, and pinpoint URL-level evidence.
5. Re-run after changes and compare mobile and desktop deltas.

## Run Audits

Use wrapper script:

```bash
python scripts/run_pagespeed.py https://example.com --strategy both --mode analysis --output-format human --analyzer-path ../websites/pagespeed_analyzer.py
```

If `websites/pagespeed_analyzer.py` exists in the workspace root, `--analyzer-path` can be omitted.

Direct invocation is also valid:

```bash
python ../websites/pagespeed_analyzer.py https://example.com --strategy both --mode analysis --output-format human --api-key-env PAGE_SPEED_INSIGHTS_API_KEY,PAGESPEED_API_KEY
```

## Recommended Defaults

- Use `--strategy both` unless user explicitly requests one strategy.
- Use `--mode analysis` for optimization tasks.
- Use `--output-format human` for quick review.
- Use `--output-format json` for automation or downstream parsing.
- Keep retries enabled (`--max-retries 3` or higher for unstable networks).
- Use `--api-key-env PAGE_SPEED_INSIGHTS_API_KEY,PAGESPEED_API_KEY` for public, unambiguous key selection.

## Troubleshoot Fast

- HTTP `429`: treat as quota/rate limit; retry later or rotate to a valid key.
- HTTP `5xx` or network errors: rely on backoff flags and retry.
- Missing key errors: set `PAGE_SPEED_INSIGHTS_API_KEY` or `PAGESPEED_API_KEY`.
- Empty/missing audit fields: surface `runtimeError` and continue with available categories and metrics.

## Interpreting Results

- Read `weakCategories` first.
- Then read `issuesByCategory` to find failing audits that affect category scores.
- Use `pinpoint` sections (`renderBlocking`, `unusedJavaScript`, `imageDelivery`, `longTasks`, `scriptTreemap`) to identify exact URLs and byte/time hotspots.
- Prioritize by largest user impact: render-blocking resources, JS waste, heavy images, long tasks, and high transfer payloads.

## References

- [references/command-recipes.md](references/command-recipes.md)
