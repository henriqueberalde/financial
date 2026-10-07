from dataclasses import dataclass

from fastapi import APIRouter, HTTPException, status

from financial.api.dependencies import LedgerDep, MonthDep, SessionDep
from financial.models.category import Category
from financial.models.transaction import Transaction
from financial.services import categorization
from financial.services.analytics import categorization_quality

router = APIRouter(tags=["categories"])


@dataclass(frozen=True)
class CategoryItem:
    id: int
    name: str
    sector: str | None


@dataclass(frozen=True)
class CategoryChoice:
    category_id: int


@dataclass(frozen=True)
class NewRule:
    category_id: int
    rule: str


@dataclass(frozen=True)
class RuleResult:
    # Transactions skipped because rules of more than one category match
    conflicts: list[str]


@router.get("/categories")
def read_categories(session: SessionDep) -> list[CategoryItem]:
    categories = session.query(Category).order_by(Category.sector,
                                                  Category.name)

    return [CategoryItem(c.id, c.name, c.sector) for c in categories]


@router.put("/transactions/{transaction_id}/category",
            status_code=status.HTTP_204_NO_CONTENT)
def update_transaction_category(session: SessionDep,
                                transaction_id: int,
                                choice: CategoryChoice) -> None:
    """Pin a category to the transaction, over the category rules."""
    _ensure_exists(session, Transaction, transaction_id)
    _ensure_exists(session, Category, choice.category_id)

    categorization.set_user_category(session, transaction_id,
                                     choice.category_id)


@router.post("/category-rules", status_code=status.HTTP_201_CREATED)
def create_category_rule(session: SessionDep, new_rule: NewRule
                         ) -> RuleResult:
    """Create a regex rule and recategorize every transaction."""
    _ensure_exists(session, Category, new_rule.category_id)

    try:
        return RuleResult(categorization.add_rule(
            session, new_rule.category_id, new_rule.rule))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.get("/categorization-quality")
def read_categorization_quality(
        session: SessionDep,
        frame: LedgerDep,
        month: MonthDep) -> categorization_quality.CategorizationQuality:
    return categorization_quality.categorization_quality(session, frame,
                                                         month)


def _ensure_exists(session: SessionDep, model: type, id: int) -> None:
    if session.get(model, id) is None:
        raise HTTPException(status_code=404,
                            detail=f"{model.__name__} {id} not found")
