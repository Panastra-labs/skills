# Command Recipes

## Full Analysis (recommended)

```bash
python scripts/run_pagespeed.py https://example.com --strategy both --mode analysis --output-format human --analyzer-path ../websites/pagespeed_analyzer.py
```

## JSON Output For Automation

```bash
python scripts/run_pagespeed.py https://example.com --strategy both --mode analysis --output-format json --analyzer-path ../websites/pagespeed_analyzer.py
```

## Save Raw Payloads

```bash
python scripts/run_pagespeed.py https://example.com --strategy both --mode analysis --save-raw --analyzer-path ../websites/pagespeed_analyzer.py
```

## Only Mobile

```bash
python scripts/run_pagespeed.py https://example.com --strategy mobile --mode analysis --analyzer-path ../websites/pagespeed_analyzer.py
```

## Retry/Backoff Tuning

```bash
python scripts/run_pagespeed.py https://example.com --strategy both --mode analysis --max-retries 5 --retry-backoff-base-seconds 1 --retry-backoff-max-seconds 16 --analyzer-path ../websites/pagespeed_analyzer.py
```

## Localized Results

```bash
python scripts/run_pagespeed.py https://example.com --strategy desktop --mode summary --locale en-US --analyzer-path ../websites/pagespeed_analyzer.py
```
