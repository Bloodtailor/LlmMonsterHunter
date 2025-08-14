
import io
import sys
import traceback
import importlib.util
from flask import jsonify
from pathlib import Path

class TeeStdout:
    """A stream that writes to both sys.stdout and a string buffer"""
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout
        self.buffer = io.StringIO()
    
    def write(self, data):
        self.original_stdout.write(data)  # write to terminal
        self.buffer.write(data)           # write to memory

    def flush(self):
        self.original_stdout.flush()
        self.buffer.flush()

    def getvalue(self):
        return self.buffer.getvalue()


def run_test_file(test_name):
    """Run a test file and capture its output while still printing to console"""
    test_file_path = f"backend/tests/{test_name}.py"

    if not Path(test_file_path).exists():
        return jsonify({
            'success': False,
            'error': f'Test file not found: {test_file_path}',
            'output': ''
        }), 404

    try:
        # Duplicate stdout
        old_stdout = sys.stdout
        tee = TeeStdout(old_stdout)
        sys.stdout = tee

        try:
            spec = importlib.util.spec_from_file_location(test_name, test_file_path)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
        finally:
            sys.stdout = old_stdout

        return jsonify({
            'success': True,
            'test_name': test_name,
            'output': tee.getvalue(),
            'message': f'Test {test_name} completed successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc(),
            'output': tee.getvalue() if 'tee' in locals() else ''
        }), 500


def get_test_files():
    """Return a list of test file names (without .py extension) from backend/tests"""
    tests_dir = Path("backend/tests")
    test_files = []

    if tests_dir.exists():
        for file in tests_dir.glob("*.py"):
            if not file.name.startswith("__"):
                test_files.append(file.stem)

    return jsonify(test_files)
