from financial.models.category import Category
from financial.models.category_rule import CategoryRule
from financial.models.category_rule_conflict_error import CategoryRuleConflictError  # nopep8


def test_message_lists_each_conflicting_category_once():
    gas = Category(name="Gas")
    water = Category(name="Water")
    rules = [
        CategoryRule(category=gas, rule="posto"),
        CategoryRule(category=gas, rule="auto posto"),
        CategoryRule(category=water, rule="agua"),
    ]

    error = CategoryRuleConflictError("AUTO POSTO CARAGUATATUBA", rules)

    assert error.message == "More than one category match. Description: 'AUTO POSTO CARAGUATATUBA', Matches: ['Gas', 'Water']"  # nopep8
    assert str(error) == error.message
    assert error.conflicted_category_rules == rules
