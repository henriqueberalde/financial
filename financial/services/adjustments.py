from sqlalchemy.orm import Session

from financial.models.adjustment import Adjustment
from financial.models.transaction import Transaction


def add_adjustment(session: Session,
                   reason: str,
                   transactions: list[int] | list[Transaction]) -> None:

    t_normalized = _normalize_and_validate(
        session,
        transactions
    )

    try:
        adjustment = Adjustment(reason=reason)

        for t in t_normalized:
            adjustment.transactions.append(t)

        session.add(adjustment)

        gains = adjustment.gains()
        spends = adjustment.spends()

        spends.sort(
            reverse=True,
            key=lambda t: t.value  # type: ignore
        )
        gains.sort(key=lambda t: t.value)  # type: ignore

        run = True
        current_spend_index = 0
        current_gain_index = 0
        while run:
            print("")
            s = spends[current_spend_index]
            g = gains[current_gain_index]

            print(f"si {current_spend_index} - gi {current_gain_index}")
            print(f"s {s.id} {s.value} - g {g.id} {g.value}")  # nopep8
            print("---")
            result = g.value + s.value

            g.value = result  # type: ignore
            s.value = result  # type: ignore

            if result > 0:
                s.value = 0  # type: ignore
            elif result < 0:
                g.value = 0  # type: ignore

            if s.value == 0:
                current_spend_index = spends.index(s) + 1
                if _is_last_index(s, spends):  # nopep8
                    run = False

            if g.value == 0:
                current_gain_index = gains.index(g) + 1
                if _is_last_index(g, gains):
                    run = False

            print(f"next si {current_spend_index} - next gi {current_gain_index}")  # nopep8
            print(f"s {s.id} {s.value} - g {g.id} {g.value}")  # nopep8
            print(f"run: {run}")
            print("")

        session.commit()
    except Exception as ex:
        session.rollback()
        raise ex


def _normalize_and_validate(session: Session,
                            transactions: list[Transaction] | list[int]) -> list[Transaction]:  # nopep8
    result: list[Transaction] = []

    if not _is_list_of_transactions(transactions):
        result = _to_transactions(
            session,
            transactions  # type: ignore
        )
    else:
        result = transactions  # type: ignore

    has_spend = False
    has_gain = False

    for t in result:
        if t.is_spend() and not has_spend:
            has_spend = True

        if t.is_gain() and not has_gain:
            has_gain = True

    if not has_spend or not has_gain:
        raise Exception(
            "Transactions must have at least one spend and one gain"
        )

    return result


def _is_last_index(obj: Transaction, list: list[Transaction]) -> bool:
    last_index = len(list) - 1
    return last_index == list.index(obj)


def _to_transactions(session: Session,
                     ids: list[int]) -> list[Transaction]:
    result: list[Transaction] = []
    for id in ids:
        result.append(session.get(Transaction, id))

    return result


def _is_list_of_transactions(list_param: list) -> bool:
    if len(list_param) == 0:
        return True

    if isinstance(list_param, list) and isinstance(list_param[0],
                                                   Transaction):
        return True

    return False
