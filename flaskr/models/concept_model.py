from flaskr.extensions import db


class Concept(db.Model):
    __tablename__ = 'concepts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    base_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    # Establish a one-to-many relationship with OrderItem
    order_items = db.relationship('OrderItem', back_populates='concept')
    

    def as_dict(self):

        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in []}

    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            
            if key in ['name']:
                setattr(self, key, value)
    
    