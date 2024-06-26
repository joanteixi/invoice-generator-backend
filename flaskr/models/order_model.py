from flaskr.extensions import db


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String)
    total_base = db.Column(db.Float)
    created_by = db.Column(db.String)
    public_url = db.Column(db.String)
    month = db.Column(db.Integer)
    year = db.Column(db.Integer)
    
    
    # Establish a one-to-many relationship with PaymentType
    payment_type_id = db.Column(db.Integer, db.ForeignKey('payment_types.id'))
    payment_type = db.relationship('PaymentType', back_populates='orders')
    
    # Establish a one-to-many relationship with OrderItem
    order_items = db.relationship('OrderItem', back_populates='order')
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in []}

    def as_dict_min(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name in ['public_id', 'name', 'type']}

    def update(self, **kwargs):
        for key, value in kwargs.items():

            if key in ['customer_name', 'payment_type_id', 'total_base']:
                setattr(self, key, value)
    
    