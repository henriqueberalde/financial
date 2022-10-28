from os import stat
import financial.entities.db as db

from typing import Any

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, relationship


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

    @staticmethod
    def get_all() -> list[CategoryRule]:   # type: ignore
        return db.get_session().query(CategoryRule).all()

    @staticmethod
    def distinct_categories(rules: list[CategoryRule]):  # type: ignore
        distinct_categories: list[str] = []

        for rule in rules:
            if rule.category.name not in distinct_categories:
                distinct_categories.append(rule.category.name)

        return distinct_categories
