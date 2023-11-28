import sys
from statement_evaluator import StatementEvaluator
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


if __name__ == '__main__':
    statements = []
    for line in sys.stdin:
        if line:
            statements.append(line.strip())
    StatementEvaluator(statements).execute()
