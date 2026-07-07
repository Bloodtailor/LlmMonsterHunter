# Inventory Routes - Thin HTTP Layer Only
# Routes only handle: HTTP parsing -> Service call -> HTTP response formatting

from flask import Blueprint, jsonify, request

from backend.services import inventory_service

inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')


@inventory_bp.route('', methods=['GET'])
def get_inventory():
    """Paged inventory listing - thin HTTP wrapper"""

    result = inventory_service.get_inventory(
        kind=request.args.get('kind', 'items'),
        limit=request.args.get('limit', type=int),
        offset=request.args.get('offset', 0, type=int),
    )

    return jsonify(result), 200 if result['success'] else 400


@inventory_bp.route('/counts', methods=['GET'])
def get_counts():
    """Item and CoCaTok counts - thin HTTP wrapper"""
    result = inventory_service.get_inventory_counts()
    return jsonify(result), 200 if result['success'] else 400
