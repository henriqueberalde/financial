import financial.entities.db as db

from sqlalchemy import Column, Integer, String


class Category(db.Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    sector = Column(String)
