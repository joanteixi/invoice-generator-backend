from flaskr.extensions import db

class User(db.Model):
    __table__name__ = 'users'
    
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(200), unique=True, nullable=False)
    username = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    avatar = db.Column(db.String(250))
    password = db.Column(db.String(500), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    create_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    update_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp()) 

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in ['password', 'id']}
    
class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)