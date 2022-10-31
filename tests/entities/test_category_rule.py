from financial.entities.category_rule import CategoryRule
from financial.entities.category import Category


def test_distinct_categories():
    rule_test_category1 = CategoryRule(
        category=Category(name="test_category1"),
        rule="")

    rule_test_category2 = CategoryRule(
        category=Category(name="test_category2"),
        rule="")

    expected = ["test_category1", "test_category2"]

    distinct_categories = CategoryRule.distinct_categories(
        [rule_test_category1, rule_test_category2])

    assert expected == distinct_categories


def test_distinct_categories_repeated_category_rules():
    rule_test_category1 = CategoryRule(
        category=Category(name="test_category1"),
        rule="")

    rule_test_category2 = CategoryRule(
        category=Category(name="test_category2"),
        rule="")

    expected = ["test_category1", "test_category2"]

    distinct_categories = CategoryRule.distinct_categories(
        [rule_test_category1, rule_test_category2, rule_test_category2])

    assert expected == distinct_categories
