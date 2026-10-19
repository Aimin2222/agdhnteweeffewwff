import json
from zipfile import ZipFile
from tools import collect_diagnostics as collector


def configure(monkeypatch,tmp_path):
    monkeypatch.setattr(collector,'ROOT',tmp_path)
    monkeypatch.setattr(collector,'SRC',tmp_path/'diagnostics')
    monkeypatch.setattr(collector,'DST',tmp_path/'AutoCine_Diagnostics.zip')


def test_empty_logs_still_produce_useful_environment_archive(monkeypatch,tmp_path):
    configure(monkeypatch,tmp_path)
    assert collector.collect()
    with ZipFile(collector.DST) as archive:
        snapshot=json.loads(archive.read('diagnostics/collector_environment.json'))
        assert snapshot['python'] and 'pillow' in snapshot['packages']


def test_original_log_bytes_are_preserved(monkeypatch,tmp_path):
    configure(monkeypatch,tmp_path)
    collector.SRC.mkdir()
    original=b'mirror failed\r\n\x81\x82\xff\n'
    (collector.SRC/'runtime.log').write_bytes(original)
    assert collector.collect()
    with ZipFile(collector.DST) as archive:
        assert archive.read('diagnostics/runtime.log')==original
    assert (collector.SRC/'runtime.log').read_bytes()==original
