import os
import uuid
import logging
from datetime import timedelta
import urllib.parse
from dotenv import load_dotenv

from flask import Flask
from werkzeug.security import generate_password_hash
from flask_migrate import Migrate

from flaskr.extensions import db
from flaskr.models.order_model import *
from flaskr.models.concept_model import *
from flaskr.models.order_items_model import *
from flaskr.models.user_model import *
from flaskr.extensions import jwt

def create_app(testing=False):

    # create the app
    # instance_path='/path/to/instance/folder'
    app = Flask(__name__, instance_relative_config=True)

    app.config['TESTING'] = testing    
    
    # ensure the instance folder exists
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    if app.config['TESTING']:
        load_dotenv(dotenv_path=os.path.join(app.instance_path, '.test_env'))
        
    # configure the app
    if app.config['DEBUG']:
        load_dotenv(dotenv_path=os.path.join(app.instance_path, '.env'))

    app.config.from_pyfile(os.path.join(
        app.instance_path, '..', 'flaskr/config.py'), silent=True)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['sql'] = False

    if app.config['TESTING']:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.sqlite'
    else:
        driver = "{ODBC Driver 17 for SQL Server}"
        # driver = "{SQL Server}"
        server = f"{app.config['SQL_SERVER_NAME']}.database.windows.net"
        database = app.config['SQL_DATABASE_NAME']
        user = app.config['SQL_USER_NAME']
        password = app.config['SQL_PASSWORD']

        params = urllib.parse.quote_plus(
            f"DRIVER={driver};SERVER={server};DATABASE={database};UID={user};PWD={password}")

        app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params

    # configure extensions - ddbb
    migrate = Migrate(app, db)

    db.init_app(app)
    with app.app_context():
        db.create_all()
    
    #generate random string

        if not User.query.filter_by(email="admin@admin.com").one_or_none():
            admin_user = User(public_id=str(uuid.uuid4()), username="admin", email="admin@admin.com", password=generate_password_hash("bismartadmin"), is_admin=True)
            db.session.add(admin_user)
            db.session.commit()

    # configure extensions - jwt
    jwt.init_app(app)
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
        hours=int(app.config["JWT_ACCESS_TOKEN_EXPIRES"]))
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(
        days=int(app.config["JWT_REFRESH_TOKEN_EXPIRES"]))
   
    # import blueprints
    from flaskr.blueprints import user
    from flaskr.blueprints import order
    from flaskr.blueprints import concept

    app.register_blueprint(user.bp)
    app.register_blueprint(order.bp)
    app.register_blueprint(concept.bp)
   

    return app
