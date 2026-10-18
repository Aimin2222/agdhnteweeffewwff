"""Run every collected test in module-isolated processes with native diagnostics.

Keeps Tcl interpreters from unrelated UI modules out of each other's lifetime.
No GC suppression, forced collection, skipped tests or assertion replacement.
Native exit still fails the run and is recorded alongside missing outcomes.
"""
import argparse
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--child', choices=('collect', 'run'))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--module')
    parser.add_argument('--report-dir', type=Path)
    parser.add_argument('--test-file', action='append')
    args = parser.parse_args()
    root = args.root.resolve()
    if args.child:
        sys.path.insert(0, str(root))
        import legacy_app  # Same initialization as the existing full-suite runner.
        import faulthandler
        import pytest
        faulthandler.enable(all_threads=True)
        if args.child == 'collect':
            class Collection:
                def pytest_collection_finish(self, session):
                    args.output.write_text(json.dumps([item.nodeid for item in session.items]), encoding='utf-8')
            return int(pytest.main([*(args.test_file or ['tests']), '--collect-only', '-q', '-p', 'no:faulthandler'],
                                   plugins=[Collection()]))
        return int(pytest.main([args.module, '-q', '-p', 'no:faulthandler',
                               '--junitxml=' + str(args.output)]))
    script = Path(__file__).resolve()
    report_dir = (args.report_dir or root / 'diagnostics' / 'local_dev' /
                  datetime.now().strftime('modules_%Y%m%d_%H%M%S_%f')).resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    merged = ET.Element('testsuites')
    failed = False
    with tempfile.TemporaryDirectory(prefix='autocine-module-tests-') as scratch:
        scratch = Path(scratch)
        collection = scratch / 'collection.json'
        prefix = [sys.executable, str(script), '--root', str(root)]
        selection = [arg for name in (args.test_file or []) for arg in ('--test-file', name)]
        collected = subprocess.run(prefix + ['--child', 'collect', '--output', str(collection), *selection], cwd=root)
        if collected.returncode or not collection.exists():
            print('Collection failed; regression run is incomplete.', flush=True)
            return collected.returncode or 1
        nodeids = json.loads(collection.read_text(encoding='utf-8'))
        if not nodeids:
            raise RuntimeError('Zero tests collected')
        modules = sorted({node.split('::', 1)[0] for node in nodeids})
        # Windows Tcl can also fail across repeated roots within one module.
        # Keep every collected case, but give GUI cases their own interpreter.
        groups = []
        for module in modules:
            gui = sys.platform == 'win32' and 'tkinter' in (root / module).read_text(encoding='utf-8')
            groups.extend([node for node in nodeids if node.split('::', 1)[0] == module]
                          if gui else [module])
        outcomes = []
        completed = 0
        for index, module in enumerate(groups):
            output = scratch / f'module{index:03d}.xml'
            print(f'[{index+1}/{len(groups)}] {module}', flush=True)
            result = subprocess.run(prefix + ['--child', 'run', '--module', module,
                                              '--output', str(output)], cwd=root)
            expected = 1 if '::' in module else sum(node.split('::', 1)[0] == module for node in nodeids)
            suites = list(ET.parse(output).getroot()) if output.exists() else []
            actual = sum(int(s.attrib['tests']) for s in suites)
            completed += actual
            if result.returncode or actual != expected:
                failed = True
            for suite in suites:
                merged.append(suite)
            if not output.exists():
                suite = ET.SubElement(merged, 'testsuite', name=module, tests='1', errors='1', failures='0', skipped='0')
                test = ET.SubElement(suite, 'testcase', name='native_or_incomplete_process')
                ET.SubElement(test, 'error').text = f'Process exit {result.returncode}; {expected} expected test outcomes missing.'
            outcomes.append({'module': module, 'expected_tests': expected, 'reported_tests': actual,
                             'returncode': result.returncode})
        ET.ElementTree(merged).write(report_dir / 'regressions.xml', encoding='utf-8', xml_declaration=True)
        summary = {'collected_tests': len(nodeids), 'reported_tests': completed,
                   'all_collected_tests_completed': completed == len(nodeids),
                   'modules': outcomes, 'gc_enabled': True, 'test_exclusions': [],
                   'windows_gui_case_isolation': sys.platform == 'win32',
                   'native_tk_lifetime_issue_fixed_in_application': False}
        (report_dir / 'regression_modules.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
        print(json.dumps({k: v for k, v in summary.items() if k != 'modules'}), flush=True)
        return 1 if failed or completed != len(nodeids) else 0


if __name__ == '__main__':
    raise SystemExit(main())
