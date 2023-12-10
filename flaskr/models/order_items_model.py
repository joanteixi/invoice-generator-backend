from flaskr.extensions import db

class OrderItem(db.Model):
  __tablename__ = 'order_items'

  id = db.Column(db.Integer, primary_key=True)
  product_name = db.Column(db.String)
  quantity = db.Column(db.Integer)
  price = db.Column(db.Float)

  # Establish a many-to-one relationship with Order
  order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
  order = db.relationship('Order', back_populates='order_items')

  def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}
  