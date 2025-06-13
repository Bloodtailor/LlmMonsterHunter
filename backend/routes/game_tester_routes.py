from flask import Blueprint, jsonify, request
from backend.services.game_tester_service import run_test_file, get_test_files

game_tester_bp = Blueprint('game_tester', __name__, url_prefix='/api/game_tester')

@game_tester_bp.route('/run/<test_name>', methods=['POST'])
def run_test(test_name):
    """Run a test file and capture its output"""
    
    result = run_test_file(test_name)
    return result

@game_tester_bp.route('/tests')
def get_tests():
    """Gets the names of the available test files"""

    test_file_names = get_test_files()

    return test_file_names