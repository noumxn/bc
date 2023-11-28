import re
from constants import (
    single_len_symbols,
    boolean_symbols,
    double_len_symbols,
    op_equals_symbols,
    bool_equals_symbols,
    assign_symbols,
    keywords,
    disj_symbols,
    conj_symbols,
    power_symbols,
    neg_symbols,
    incr_or_decr_symbols,
    relational_symbols,
)


class VariableNameChecker(object):
    def __init__(self, name):
        self.name = name

    def validate(self):
        if self.not_matched_with_regex() or self.all_underscore() or self.not_keyword():
            raise SyntaxError('parse error')

    def not_matched_with_regex(self):
        return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.name) is None

    def all_underscore(self):
        return all([i == '_' for i in self.name])

    def not_keyword(self):
        return self.name in keywords
