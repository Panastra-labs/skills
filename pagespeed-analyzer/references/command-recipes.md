# Command Recipes

## Setup Check

```bash
python scripts/check_setup.py
```

## Full Analysis (recommended)

```bash
python scripts/run_pagespeed.py https://example.com --strategy both --mode analysis --output-format human
```

## JSON Output For Automation

```bash
python scripts/run_pagespeed.py https://example.com --strategy both --mode analysis --output-format json
```

## Save Raw Payloads

```bash
python scripts/run_pagespeed.py https://example.com --strategy both --mode analysis --save-raw
```

## Only Mobile

```bash
python scripts/run_pagespeed.py https://example.com --strategy mobile --mode analysis
```

## Retry/Backoff Tuning

```bash
python scripts/run_pagespeed.py https://example.com --strategy both --mode analysis --max-retries 5 --retry-backoff-base-seconds 1 --retry-backoff-max-seconds 16
```

## Localized Results

```bash
python scripts/run_pagespeed.py https://example.com --strategy desktop --mode summary --locale en-US
```
