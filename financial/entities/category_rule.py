import financial.entities.db as db
from typing import Any

from financial.entities.category import Category
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class CategoryRule(db.Base):
    __tablename__ = "category_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule = Column(String)
    category_id = Column(String, ForeignKey("categories.id"))

    category = relationship("Category")

    @staticmethod
    def distinct_categories(rules: list["CategoryRule"]):  # type: ignore
        distinct_categories: list[str] = []

        for rule in rules:
            if rule.category.name not in distinct_categories:
                distinct_categories.append(rule.category.name)

        return distinct_categories
