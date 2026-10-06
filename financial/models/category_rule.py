import financial.database as db

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class CategoryRule(db.Base):
    __tablename__ = "category_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule = Column(String)
    category_id = Column(String, ForeignKey("categories.id"))

    category = relationship("Category")
