from flaskr.extensions import db


class PaymentType(db.Model):
    __tablename__ = 'payment_types'

    id = db.Column(db.Integer, primary_key=True)
    payment_type = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    # Establish a one-to-many relationship with Order
    orders = db.relationship('Order', back_populates='payment_type')
    

    def as_dict(self):

        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in []}

    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            
            if key in ['payment_type']:
                setattr(self, key, value)
    
    