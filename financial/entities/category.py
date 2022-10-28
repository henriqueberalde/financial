import financial.entities.db as db

from sqlalchemy import Column, Integer, String


class Category(db.Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    def save(self):
        session = db.get_session()
        session.add(self)
        session.commit()

    def fetch_by_name(self):
        Category(name=self.name)
        session = db.get_session()
        self = session.query(Category).filter_by(name=self.name)
