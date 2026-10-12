"""Tracked-code audit must work in standalone and nested repos without reading private files."""
import subprocess
import pytest
from tools.check_text_encoding import audit


@pytest.mark.parametrize('nested',[False,True])
def test_git_audit_only_reads_tracked_code_and_resolves_git_root(tmp_path,nested):
    repo=tmp_path/'repo';repo.mkdir()
    subprocess.run(['git','init','-q',str(repo)],check=True)
    app=repo/'LoL_AutoCine' if nested else repo;app.mkdir(exist_ok=True)
    code=app/'source.py';code.write_text('print("日本語")\n',encoding='utf-8')
    (repo/'.gitignore').write_text('private.txt\n')
    (app/'private.txt').write_bytes(b'PRIVATE\x82\xa0')
    subprocess.run(['git','-C',str(repo),'add',str(code),'.gitignore'],check=True)
    assert audit(app)==[]
    code.write_bytes(b'\x82\xa0')
    problems=audit(app)
    assert len(problems)==1 and 'source.py' in problems[0] and 'UTF-8' in problems[0]
    assert not any('private.txt' in p for p in problems)
