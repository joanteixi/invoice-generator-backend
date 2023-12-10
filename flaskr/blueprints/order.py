from flask import Blueprint, request, jsonify
from flaskr.extensions import db
from flask_cors import CORS
from flaskr.models.order_model import Order
from flaskr.models.order_items_model import OrderItem

bp = Blueprint('document', __name__, url_prefix='/api/orders')
CORS(bp)

# Create an order
@bp.route('', methods=['POST'])
def create_order():
    data = request.get_json()
    customer_name = data.get('customer_name')
    order_items = data.get('order_items')

    order = Order(customer_name=customer_name)
    db.session.add(order)
    db.session.commit()

    for item in order_items:
        product_name = item.get('product_name')
        quantity = item.get('quantity')
        price = item.get('price')

        order_item = OrderItem(product_name=product_name, quantity=quantity, price=price, order_id=order.id)
        db.session.add(order_item)
    
    db.session.commit()
    
    return jsonify({'message': 'Order created successfully'})
    

# Read all orders
@bp.route('', methods=['GET'])
def get_all_orders():
    orders = Order.query.all()
    result = []
    
    for order in orders:
        order_data = order.as_dict()
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        order_data['order_items'] = [item.as_dict() for item in order_items]
        result.append(order_data)
    
    return jsonify(result)

# Read a specific order
@bp.route('<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if order:
        order_data = order.as_dict()
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        order_data['order_items'] = [item.as_dict() for item in order_items]
        
        return jsonify(order_data)
    
    return jsonify({'message': 'Order not found'})

# Update an order
@bp.route('/order/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    order = Order.query.get(order_id)
    if order:
        data = request.get_json()
        order.update(**data)
        db.session.commit()
        return jsonify({'message': 'Order updated successfully'})
    return jsonify({'message': 'Order not found'})

# Delete an order
@bp.route('/order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Order.query.get(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Order deleted successfully'})
    return jsonify({'message': 'Order not found'})

# Create an order item
@bp.route('/order/<int:order_id>/item', methods=['POST'])
def create_order_item(order_id):
    order = Order.query.get(order_id)
    if order:
        data = request.get_json()
        order_item = OrderItems(**data)
        order.order_items.append(order_item)
        db.session.commit()
        return jsonify({'message': 'Order item created successfully'})
    return jsonify({'message': 'Order not found'})

# Read all order items for a specific order
@bp.route('/order/<int:order_id>/item', methods=['GET'])
def get_all_order_items(order_id):
    order = Order.query.get(order_id)
    if order:
        result = []
        for order_item in order.order_items:
            result.append(order_item.to_dict())
        return jsonify(result)
    return jsonify({'message': 'Order not found'})

# Read a specific order item
@bp.route('/order/<int:order_id>/item/<int:item_id>', methods=['GET'])
def get_order_item(order_id, item_id):
    order = Order.query.get(order_id)
    if order:
        order_item = OrderItems.query.get(item_id)
        if order_item:
            return jsonify(order_item.to_dict())
        return jsonify({'message': 'Order item not found'})
    return jsonify({'message': 'Order not found'})

# Update an order item
@bp.route('/order/<int:order_id>/item/<int:item_id>', methods=['PUT'])
def update_order_item(order_id, item_id):
    order = Order.query.get(order_id)
    if order:
        order_item = OrderItems.query.get(item_id)
        if order_item:
            data = request.get_json()
            order_item.update(**data)
            db.session.commit()
            return jsonify({'message': 'Order item updated successfully'})
        return jsonify({'message': 'Order item not found'})
    return jsonify({'message': 'Order not found'})

# Delete an order item
@bp.route('/order/<int:order_id>/item/<int:item_id>', methods=['DELETE'])
def delete_order_item(order_id, item_id):
    order = Order.query.get(order_id)
    if order:
        order_item = OrderItems.query.get(item_id)
        if order_item:
            db.session.delete(order_item)
            db.session.commit()
            return jsonify({'message': 'Order item deleted successfully'})
        return jsonify({'message': 'Order item not found'})
    return jsonify({'message': 'Order not found'})

