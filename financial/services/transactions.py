from typing import Any, Iterable

from sqlalchemy.orm import Session

from financial.models.transaction import Transaction


def set_context(session: Session,
                ids: Iterable[Any] | str,
                context: str) -> None:
    """Set the context of the transactions with the given ids, given as an
    iterable or as a space-separated string."""
    ids_param = str(ids).split(" ") if isinstance(ids, str) else ids

    try:
        session.query(Transaction).filter(
            Transaction.id.in_(ids_param)
        ).update({
            Transaction.context: context
        })
        session.commit()
    except Exception as e:
        print(f"Error while saving data to db.{e}")
        session.rollback()
