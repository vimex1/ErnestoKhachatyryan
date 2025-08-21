from app.backend.db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    comment = Column(String, nullable=True)
    comment_date = Column(Date)
    grade = Column(Integer)
    is_active = Column(Boolean, default=True)