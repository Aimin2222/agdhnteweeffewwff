"""Startup failures must survive missing engine packages and GUI selection errors."""
import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture
def launcher(tmp_path, monkeypatch):
    path = Path(__file__).resolve().parents[1] / 'tools/gpu_render_test.py'
    spec = importlib.util.spec_from_file_location('gpu_test_launcher', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    (tmp_path/'VERSION.txt').write_text('test')
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    return module


def records(module):
    return [json.loads(p.read_text()) for p in (module.ROOT/'diagnostics').glob('*.json')]


@pytest.mark.parametrize('error', [ModuleNotFoundError('missing engine dependency'), RuntimeError('file dialog failed')])
def test_early_failures_leave_traceback_and_nonzero_result(launcher, error):
    def run(stage):
        stage('loading_engine')
        raise error
    assert launcher.entrypoint(run) == 1
    data, = records(launcher)
    assert data['status'] == 'failed' and data['exit_code'] == 1
    log, = (launcher.ROOT/'diagnostics').glob('*.log')
    assert type(error).__name__ in log.read_text()
    assert str(error) in log.read_text()


def test_success_streams_progress_and_records_completion(launcher, capsys):
    def run(stage):
        stage('running_cases')
        print('01 passed')
        return 0
    assert launcher.entrypoint(run) == 0
    assert records(launcher)[0]['status'] == 'completed'
    assert '01 passed' in capsys.readouterr().out
    assert '01 passed' in next((launcher.ROOT/'diagnostics').glob('*.log')).read_text()


def test_cancel_has_a_distinct_status_without_engine_start(launcher):
    def run(stage):
        stage('cancelled')
        return 2
    assert launcher.entrypoint(run) == 2
    assert records(launcher)[0]['status'] == 'cancelled'


def test_argument_failure_is_saved(launcher):
    def run(stage):
        raise SystemExit(2)
    assert launcher.entrypoint(run) == 2
    assert records(launcher)[0]['status'] == 'failed'
