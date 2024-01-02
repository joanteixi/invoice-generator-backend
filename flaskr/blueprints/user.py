from flask import Blueprint

import uuid
from datetime import datetime, timezone

from flask_jwt_extended import jwt_required
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt, get_jwt_identity
from flask_jwt_extended import create_access_token,  create_refresh_token
from flask import current_app

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from functools import wraps

from flask import request, jsonify
from flask_cors import CORS
from flaskr.extensions import db

from flaskr.models.user_model import *
from flaskr.models.order_model import *
from flaskr.models.order_items_model import *

from flaskr.extensions import jwt

bp = Blueprint('user', __name__, url_prefix='/api/user')
CORS(bp)
# test route


@bp.route('/test', methods=['GET'])
def test():
    return jsonify({
        "message": "Test endpoint",
        "status":"Successfully completed"
        }), 200


# decorators
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["is_admin"]:
                return fn(*args, **kwargs)
            else:
                return jsonify({
                    "message": "Admins only!",
                    "status": "Failed"
                    }), 403

        return decorator

    return wrapper


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None


# crud endpoints
@bp.route("", methods=["POST"], endpoint='create_user')
def create_user():
    """Create new User
    ---
    tags:
    - Users

    parameters:
        - name: email
          in: body
          type: string
          required: true
          description: The email of the user

        - name: password
          in: body
          type: string
          required: true
          description: The password of the 

        - name: username
          in: body
          type: string
          required: true
          description: The Username of the user

        - name: is_admin
          in: body
          type: boolean
          required: false
          description: Define is user is admin or not        
    """
    data = request.get_json()

    if not data["username"] or not data["email"] or not data["password"]:
        return jsonify(status="error", message="Missing information!"), 400

    if User.query.filter_by(email=data["email"]).one_or_none():
        return jsonify(status="error", message="User already exists!"), 400

    hashed_password = generate_password_hash(data["password"])
    user = User(public_id=str(uuid.uuid4(
    )), username=data["username"], email=data["email"], password=hashed_password, is_admin=int(data["is_admin"]))

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message":{"user": user.username},
        "status": "Successfully completed"
        }), 200


@bp.route("sign-in-with-token", methods=["POST"], endpoint='sign-in-with-token')
@jwt_required()
def login_with_token():
    user = User.query.filter_by(public_id=get_jwt_identity()).one_or_none()
    access_token = create_access_token(identity=user.public_id, additional_claims={
                                       "is_admin": user.is_admin})
    refresh_token = create_refresh_token(identity=user.public_id, additional_claims={
                                         "is_admin": user.is_admin})
    

    return jsonify(status="success", message="User successfully logged in", access_token=access_token, refresh_token=refresh_token, user=user.as_dict()), 200

@bp.route("", methods=["GET"], endpoint='get_user')
@jwt_required()
def get_user():
    """Get active user info
    ---
    tags:
    - Users

    responses:
        200:
            description: User object
            schema:
                $ref: '#/definitions/User'        

    """
    user = User.query.filter_by(public_id=get_jwt_identity()).one_or_none()
    if not user:
        return jsonify({
            "message":{"user": user.username,
                    "email": user.email,
                    "is_admin": user.is_admin},
            "status": "Failed"
        }), 400
    
    return jsonify({
        "message": {"user": user.username,
                    "email": user.email,
                    "is_admin": user.is_admin},
        "status": "Successfully completed"}), 400
    

@bp.route("login", methods=["POST"], endpoint='login_user')
def login_user():
    """Create access token
    ---
    tags:
    - Users

    parameters:
        - name: email
          in: body
          type: string
          required: true
          description: The email of the user

        - name: password
          in: body
          type: string
          required: true
          description: The password of the user

    """

    data = request.get_json()
    if 'password' not in data.keys() or 'email' not in data.keys():
        return jsonify({
            "message": """User not verified""",
            "status": "Failed"
        }), 400

    
    user = User.query.filter_by(email=data['email']).one_or_none()

    if not user:
        return jsonify({
            "message": """User not found""",
            "status": "Failed"
        }), 400
    
    if not check_password_hash(user.password, data['password']):
        return jsonify({
            "message": """Invalid password""",
            "status": "Failed"
        }), 400
    
    access_token = create_access_token(identity=user.public_id, additional_claims={
                                       "is_admin": user.is_admin})

    return jsonify(status="success", message="User successfully logged in", access_token=access_token, user=user.as_dict()), 200
    


@bp.route("logout", methods=["DELETE"], endpoint='expire_token')
@jwt_required()
def expire_token():
    """Inactivate access token"""

    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)

    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()

    return jsonify({
        "message":"User logged out",
        "status": "Successfully completed"
        }), 200


@bp.route("refresh", methods=["POST"], endpoint='refresh_token')
@jwt_required(refresh=True)
def refresh_token():

    identity = get_jwt_identity()
    claims = get_jwt()

    access_token = create_access_token(identity=identity, additional_claims={
                                       "is_admin": claims["is_admin"]})

    return jsonify({
        "message":"User session refreshed",
        "status": "Successfully completed"
        }), 200


@bp.route("<public_id>", methods=["PUT"], endpoint='update_user')
@admin_required()
def update_user(public_id):
    """Modify users information in database.
    ---
    tags:
        - User
        parameters:
            - name: public_id
              in: path
              type: string
              required: true
              description: unic user identifier

           - name: email
             in: body
             type: string
             required: false
             description: The email of the user

           - name: password
             in: body
             type: string
             required: false
             description: The password of the 
 
           - name: username
             in: body
             type: string
             required: false
             description: The Username of the user

           - name: is_admin
             in: body
             type: boolean
             required: false
             description: Define is user is admin or not   
    """
    data = request.get_json()

    user = User.query.filter_by(public_id=public_id).one_or_none()
    if not user:
        return jsonify({
            "message": """User not found""",
            "status": "Failed"
        }), 400
    
    if 'username' in data.keys():
        user.username = data["username"]

    if 'email' in data.keys():

        if data.get('email') != user.email and User.query.filter_by(email=data["email"]).one_or_none():
            return jsonify({
                "message": """Email already exists""",
                "status": "Failed"
                }), 400
        
        user.email = data["email"]

    if 'password' in data.keys():
        user.password = generate_password_hash(
            data["password"], method="sha256")

    if 'is_admin' in data.keys():
        user.is_admin = int(data["is_admin"])

    db.session.commit()

    return jsonify({
        "message": f""" User updated
                name: {user.username},
                email: {user.email},
                 is admin: {user.is_admin}""",
        "status": "Successfully completed"}), 400


@bp.route("<public_id>", methods=["DELETE"], endpoint='delete_user')
@admin_required()
def delete_user(public_id):
    """Delete User
    ---
    tags:
    - Users

    parameters:
        - name: id
          in: path
          type: string
          required: true
          description: The public id of user


    """

    user = User.query.filter_by(public_id=public_id).one_or_none()
    if not user:
        return jsonify({
            "message": """User not found""",
            "status": "Failed"
        }), 400
    
    db.session.delete(user)
    db.session.commit()

    return jsonify({
            "message": """User deleted""",
            "status": "Successfully completed"
        }), 200