"""
Tests for the pipeline orchestration layer.

The full end-to-end integration run is exercised by CI via
`python -m src.pipeline`, so these tests focus on the structure
and behaviour of `run_pipeline()` itself.
"""

import polars as pl
import pytest

from src.pipeline import PipelineRun, StepResult

# ---------------------------------------------------------------------
# PipelineRun / StepResult containers
# ---------------------------------------------------------------------


def test_pipeline_run_starts_empty():
    run = PipelineRun()
    assert run.steps == []
    assert run.total_duration_s == 0


def test_pipeline_run_records_steps():
    run = PipelineRun()
    run.record("step_a", 1.5, rows=10, path="/tmp/a")
    run.record("step_b", 2.5, rows=20, path="/tmp/b")

    assert len(run.steps) == 2
    assert run.total_duration_s == pytest.approx(4.0)
    assert run.steps[0].name == "step_a"
    assert run.steps[0].rows == 10
    assert run.steps[1].duration_s == 2.5


def test_step_result_defaults():
    step = StepResult(name="x", duration_s=0.1)
    assert step.rows is None
    assert step.path is None


# ---------------------------------------------------------------------
# run_pipeline — structural, no filesystem side effects asserted
# ---------------------------------------------------------------------


def test_run_pipeline_is_callable():
    """The entry point exists and is importable."""
    from src.pipeline import run_pipeline

    assert callable(run_pipeline)


@pytest.mark.integration
def test_run_pipeline_returns_pipeline_run(sandbox_data_dirs, sandbox_duckdb):
    """
    Full run — only executes when `-m integration` is passed.
    Redirects data dirs and DuckDB to temp locations so nothing
    leaks into the real project.
    """
    from src.pipeline import run_pipeline

    run = run_pipeline(seed=42)

    assert isinstance(run, PipelineRun)
    assert len(run.steps) > 0

    step_names = {s.name for s in run.steps}
    assert "customers" in step_names
    assert "warehouses" in step_names
    assert "orders" in step_names
    assert "routes" in step_names
