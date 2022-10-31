import pandas
import re
from financial.entities.category_rule_conflict_error import CategoryRuleConflictError  # nopep8

from pandas import DataFrame as PandasDataFrame
from financial.entities.user import User
from financial.entities.category_rule import CategoryRule
from financial.entities.normalization_error import NormalizationError


class DataFrame:
    def __init__(self,
                 data_frame: PandasDataFrame,
                 category_rules: list[CategoryRule]):

        self.data_frame = data_frame
        self.category_rules = category_rules

    def normalize_date(self) -> None:
        self.data_frame['date'] = pandas.to_datetime(self.data_frame['date'],
                                                     format='%d/%m/%Y')

    def add_fixed_columns(self, user: User, bank: str) -> None:
        self.data_frame.insert(0, "user_id", user.id)
        self.data_frame.insert(1, "user_account", user.account)
        self.data_frame.insert(2, "bank", bank)

    def set_category_by_rules(self):
        errors: list[str] = []
        self.data_frame['category_id'] = self.data_frame[
            'description'
        ].apply(lambda d: self.__try_set_category(d, errors))

        if (len(errors) > 0):
            raise NormalizationError(errors)

    def __try_set_category(self, d: str, errors: list[str]) -> str | None:
        try:
            return self.__set_category(d)
        except CategoryRuleConflictError as e:
            errors.append(e.message)

    def __set_category(self, description: str) -> str | None:
        matched_rules: list[CategoryRule] = []

        for rule in self.category_rules:
            if re.search(str(rule.rule),
                         description,
                         re.IGNORECASE) is not None:
                matched_rules.append(rule)

        distinct_matched_categories = CategoryRule.distinct_categories(
            matched_rules
        )

        if len(distinct_matched_categories) == 0:
            return None

        if len(distinct_matched_categories) == 1:
            return str(matched_rules[0].category.id)

        raise CategoryRuleConflictError(description, matched_rules)
