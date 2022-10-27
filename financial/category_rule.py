import financial.db as db

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, Session, relationship


class CategoryRule(db.Base):
    __tablename__ = "category_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule = Column(String)
    category_id = Column(String, ForeignKey("categories.id"))

    category = relationship("Category")

    def save(self):
        session = Session(db.get_engine())
        session.add(self)
        session.commit()
