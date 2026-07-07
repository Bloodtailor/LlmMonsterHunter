import importlib.util
import io
import sys
import traceback
from pathlib import Path

from flask import jsonify


class TeeStdout:
    """A stream that writes to both sys.stdout and a string buffer"""

    def __init__(self, original_stdout):
        self.original_stdout = original_stdout
        self.buffer = io.StringIO()

    def write(self, data):
        self.original_stdout.write(data)  # write to terminal
        self.buffer.write(data)  # write to memory

    def flush(self):
        self.original_stdout.flush()
        self.buffer.flush()

    def getvalue(self):
        return self.buffer.getvalue()


def run_test_file(test_name):
    """Run a test file and capture its output while still printing to console"""

    # Only names that exist in backend/tests may run - the name arrives
    # from the URL, so never let it form a path on its own
    if test_name not in list_test_names():
        return jsonify({'success': False, 'error': f'Unknown test: {test_name}', 'output': ''}), 404

    test_file_path = f"backend/tests/{test_name}.py"

    try:
        # Duplicate stdout
        old_stdout = sys.stdout
        tee = TeeStdout(old_stdout)
        sys.stdout = tee

        try:
            spec = importlib.util.spec_from_file_location(test_name, test_file_path)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)

            # Utility scripts run at import. Suites define main() - which
            # exec_module never triggers (__name__ is the file stem, not
            # '__main__') - so call it; it returns the failed-check count
            failed_checks = 0
            if hasattr(test_module, 'main'):
                failed_checks = int(test_module.main() or 0)
        finally:
            sys.stdout = old_stdout

        if failed_checks:
            return jsonify(
                {
                    'success': False,
                    'test_name': test_name,
                    'error': f'{failed_checks} check(s) failed',
                    'output': tee.getvalue(),
                }
            ), 200

        return jsonify(
            {
                'success': True,
                'test_name': test_name,
                'output': tee.getvalue(),
                'message': f'Test {test_name} completed successfully',
            }
        )

    except Exception as e:
        return jsonify(
            {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'output': tee.getvalue() if 'tee' in locals() else '',
            }
        ), 500


def list_test_names():
    """Names (without .py) of the runnable files in backend/tests"""
    tests_dir = Path("backend/tests")
    if not tests_dir.exists():
        return []
    return sorted(file.stem for file in tests_dir.glob("*.py") if not file.name.startswith("__"))


def get_test_files():
    """Return a list of test file names (without .py extension) from backend/tests"""
    return jsonify(list_test_names())
