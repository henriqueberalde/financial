from financial.entities.category_rule import CategoryRule


class CategoryRuleConflictError(Exception):
    def __init__(self,
                 t_description: str,
                 conflicted_rules: list[CategoryRule]):
        dist_c = CategoryRule.distinct_categories(
            conflicted_rules)

        self.message = f"More than one category match. Description: '{t_description}', Matches: {dist_c}"  # nopep8

        self.conflicted_category_rules = conflicted_rules
        super().__init__(self.message)
