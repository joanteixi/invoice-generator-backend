from flask import Blueprint, request, jsonify
from flaskr.extensions import db
from flask_cors import CORS
from flaskr.models.order_model import Order
from flaskr.models.order_items_model import OrderItem
from flaskr.models.concept_model import Concept
from flaskr.models.user_model import User
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
from whatsapp import whatsapp

bp = Blueprint('document', __name__, url_prefix='/api/orders')
CORS(bp)

# Create an order
@bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    data = request.get_json()
    order_items = data.get('order_items')

    #if data contains some id, it's not a new order
    if data.get('id'):
        order = Order.query.get(data.get('id'))
        
        # update order with new values
        order.update(**data)
        
        # delete all order items for this order
        for item in order.order_items:
            db.session.delete(item) 
        
    else:
        order = Order(
            customer_name = data.get('customer_name'), 
            payment_type_id = data.get('payment_type_id'), 
            total_base = data.get('total_base'),
            created_by = get_jwt_identity(),
            public_url = str(uuid.uuid4())
        )
    
    db.session.add(order)
    
    for item in order_items:
        order_item = OrderItem(
        quantity=item.get('quantity'),
        price=item.get('price'),
        order_id=order.id,
        concept_id=item.get('concept'),
        total_item=item.get('total_item')
        )
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
        
        # Get the user name that created the order
        created_by_user = User.query.filter_by(public_id=order.created_by).first()
        order_data['created_by'] = created_by_user.username
        
        result.append(order_data)
    
    return jsonify(result)

# Read a specific order
@bp.route('<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)

    if order:
        order_data = order.as_dict()
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        order_data['order_items'] = []
        
        for item in order_items:
            item_array = item.as_dict()
            concept_id = item.concept_id
            concept = Concept.query.get(concept_id)
            item_array['concept'] = concept.name
            order_data['order_items'].append(item_array)
            

        return jsonify(order_data)
            
    return jsonify({'message': 'Order not found'})

@bp.route('<int:order_id>', methods=['PUT'])
def update_order(order_id):
    order = Order.query.get(order_id)
    if order:
        data = request.get_json()
        order.update(**data)
        db.session.commit()
        return jsonify({'message': 'Order updated successfully'})
    return jsonify({'message': 'Order not found'})

# Delete an order
@bp.route('<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Order.query.get(order_id)
    if order:
        db.session.delete(order)
        # delete all order items for this order
        for item in order.order_items:
            db.session.delete(item)
            
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
@bp.route('<int:order_id>/item/<int:item_id>', methods=['DELETE'])
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


# show invoice by public_url
@bp.route('/shared_order/<string:public_url>', methods=['GET'])
def get_shared_invoice(public_url):
    order = Order.query.filter_by(public_url=public_url).first()
    if order:
        order_data = order.as_dict()
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        order_data['order_items'] = [item.as_dict() for item in order_items]
        
        # Get the user name that created the order
        created_by_user = User.query.filter_by(public_id=order.created_by).first()
        order_data['created_by'] = created_by_user.username
        
        return jsonify(order_data)
    
    return jsonify({'message': 'Order not found'})


# send whatsapp shared-url
@bp.route('<int:order_id>/send_whatsapp', methods=['POST'])
async def send_whatsapp(order_id):
    order = Order.query.filter_by(id=order_id).first()
    await whatsapp.send_message('+34679201018', f'https://tiquets.puceduca.cat/accounting/shared_version/{order.public_url}')
    
    
    return jsonify({'message': 'Sended Message'})


