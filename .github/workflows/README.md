# CI Workflows

This directory contains GitHub Actions workflows that keep the
ShippingDataPipeline tested and linted on every push and pull request.

## Workflows

### `ci.yml` — Continuous Integration

Runs on every push to `main`/`master`, on every pull request against
those branches, and can be triggered manually from the Actions tab.

**Jobs:**

| Job | What it does | Duration |
|-----|--------------|----------|
| `lint` | Runs `ruff check` and `ruff format --check` | ~30s |
| `test` | Runs `pytest` across Python 3.11 / 3.12 / 3.13 with coverage | ~2min per version |
| `dbt` | Runs `python -m src.pipeline` → `dbt run` → `dbt test` on a fresh DuckDB | ~2min |
| `integration` | Runs the full-pipeline pytest suite (`-m integration`) | ~1min |
| `ci-status` | Gate job — fails if any dependency failed | <5s |

**Why this design?**

- **Lint runs first** — fast feedback if style is off
- **Test matrix runs 3.11 / 3.12 / 3.13** — ensures the package works across supported Pythons; 3.14 is intentionally excluded until the DuckDB/dbt ecosystem officially supports it
- **dbt depends on `test`** — no point running dbt if unit tests fail
- **dbt uses a temp DuckDB** — the workflow writes `~/.dbt/profiles.yml` pointing at `$GITHUB_WORKSPACE/warehouse/shipping.duckdb` so the pipeline's output is the dbt source
- **Integration runs separately** — full-pipeline tests are slower and only matter once unit tests pass
- **`ci-status` gate** — branch protection can require a single check "CI status" instead of four separate jobs

## Running CI Locally

Most CI checks have local equivalents via the `Makefile` at the
repository root:

```bash
make lint        # ruff check + ruff format --check
make test        # pytest tests/ -v
make test-cov    # pytest with coverage
make dbt         # dbt run + dbt test
make ci          # lint + test + dbt (the full CI surface)