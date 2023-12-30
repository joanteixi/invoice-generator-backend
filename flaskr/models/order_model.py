from flaskr.extensions import db


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String)

    # Establish a one-to-many relationship with OrderItem
    order_items = db.relationship('OrderItem', back_populates='order')
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    def as_dict(self):

        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in []}

    def as_dict_min(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name in ['public_id', 'name', 'type']}

    def update(self, **kwargs):
        for key, value in kwargs.items():
            
            if key in ['customer_name']:
                setattr(self, key, value)
    
    