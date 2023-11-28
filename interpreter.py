from parsor import ast, Parsor
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


class Interpreter(object):
    """
    >>> Interpreter(Parsor('x + y * z').execute(), {'y': 2, 'z': 3}).execute()
    6.0
    >>> Interpreter(Parsor('x / y * z').execute(), {'y': 2, 'z': 3}).execute()
    0.0
    >>> Interpreter(Parsor('x / y * z').execute(), {'z': 3, 'x': 6}).execute()
    Traceback (most recent call last):
    ...
    ZeroDivisionError: divide by zero
    >>> Interpreter(Parsor('(x + y) * z + 5').execute(), {'x': 6, 'y': 2, 'z': 3}).execute()
    29.0
    >>> Interpreter(Parsor('(x + y) * (z + 5)').execute(), {'x': 6, 'y': 2, 'z': 3}).execute()
    64.0
    >>> Interpreter(Parsor('(x + y) * (z - 5)').execute(), {'x': 6, 'y': 2, 'z': 3}).execute()
    -16.0
    """

    def __init__(self, a: ast, variables) -> None:
        self.a = a
        self.variables = variables

    def execute(self) -> bool:
        if self.a.typ in ['fl', 'bool']:
            return self.a.children[0]
        elif self.a.typ == 'var':
            return self.interp_var()
        elif self.a.typ == '=':
            return self.interp_assign()
        elif self.a.typ == '+':
            return self.interp_plus()
        elif self.a.typ == '-':
            return self.interp_minus()
        elif self.a.typ == '*':
            return self.interp_times()
        elif self.a.typ == '/':
            return self.interp_divide()
        elif self.a.typ == '%':
            return self.interp_mod()
        elif self.a.typ == '^':
            return self.interp_pow()
        elif self.a.typ == '==':
            return self.interp_eq()
        elif self.a.typ == '!=':
            return self.interp_neq()
        elif self.a.typ == '>':
            return self.interp_gt()
        elif self.a.typ == '<':
            return self.interp_lt()
        elif self.a.typ == '>=':
            return self.interp_gte()
        elif self.a.typ == '<=':
            return self.interp_lte()
        elif self.a.typ == '!':
            return self.interp_not()
        elif self.a.typ == '&&':
            return self.interp_and()
        elif self.a.typ == '||':
            return self.interp_or()
        elif self.a.typ in ['--', '++']:
            return self.interp_incr_or_decr()

        raise SyntaxError(f'unknown operation {self.a.typ}')

    def interp_var(self):
        if self.a.children[0] not in self.variables:
            self.variables[self.a.children[0]] = float(0)

        value = self.variables[self.a.children[0]]
        if self.a.post_op:
            Interpreter(self.a.post_op, self.variables).execute()
        return value

    def interp_plus(self):
        return Interpreter(self.a.children[0], self.variables).execute() + Interpreter(self.a.children[1], self.variables).execute()

    def interp_minus(self):
        if len(self.a.children) == 1:
            return -Interpreter(self.a.children[0], self.variables).execute()

        return Interpreter(self.a.children[0], self.variables).execute() - Interpreter(self.a.children[1], self.variables).execute()

    def interp_times(self):
        return Interpreter(self.a.children[0], self.variables).execute() * Interpreter(self.a.children[1], self.variables).execute()

    def interp_divide(self):
        right = Interpreter(self.a.children[1], self.variables).execute()
        if right in [0, None, 0.0]:
            raise ZeroDivisionError('divide by zero')
        return Interpreter(self.a.children[0], self.variables).execute() / right

    def interp_mod(self):
        right = Interpreter(self.a.children[1], self.variables).execute()
        if right in [0, None, 0.0]:
            raise ZeroDivisionError('divide by zero')
        left = Interpreter(self.a.children[0], self.variables).execute()

        return left - (right * int(left/right))
        # return left % right

    def interp_pow(self):
        return Interpreter(self.a.children[0], self.variables).execute() ** Interpreter(self.a.children[1], self.variables).execute()

    def interp_not(self):
        return self.bool_to_int(not Interpreter(self.a.children[0], self.variables).execute())

    def interp_and(self):
        return self.bool_to_int(Interpreter(self.a.children[0], self.variables).execute() and Interpreter(self.a.children[1], self.variables).execute())

    def interp_or(self):
        return self.bool_to_int(Interpreter(self.a.children[0], self.variables).execute() or Interpreter(self.a.children[1], self.variables).execute())

    def interp_incr_or_decr(self):
        if len(self.a.children) != 1:
            raise SyntaxError(f'expected 1 child, got {len(self.a.children)}')

        if self.a.children[0].typ != 'var':
            raise SyntaxError(
                f'expected variable, got {self.a.children[0].typ}'
            )

        variable = self.a.children[0].children[0]

        if variable not in self.variables:
            self.variables[variable] = float(0)

        if self.a.typ == '++':
            self.variables[variable] += 1
        elif self.a.typ == '--':
            self.variables[variable] -= 1
        else:
            raise SyntaxError(f'unknown operation {self.a.children[1]}')

        return self.variables[variable]

    def interp_eq(self):
        return self.bool_to_int(Interpreter(self.a.children[0], self.variables).execute() == Interpreter(self.a.children[1], self.variables).execute())

    def interp_neq(self):
        return self.bool_to_int(Interpreter(self.a.children[0], self.variables).execute() != Interpreter(self.a.children[1], self.variables).execute())

    def interp_gt(self):
        return self.bool_to_int(Interpreter(self.a.children[0], self.variables).execute() > Interpreter(self.a.children[1], self.variables).execute())

    def interp_lt(self):
        return self.bool_to_int(Interpreter(self.a.children[0], self.variables).execute() < Interpreter(self.a.children[1], self.variables).execute())

    def interp_gte(self):
        return self.bool_to_int(Interpreter(self.a.children[0], self.variables).execute() >= Interpreter(self.a.children[1], self.variables).execute())

    def interp_lte(self):
        return self.bool_to_int(Interpreter(self.a.children[0], self.variables).execute() <= Interpreter(self.a.children[1], self.variables).execute())

    def interp_assign(self):
        if len(self.a.children) != 2 or self.a.children[0].typ != 'var':
            raise SyntaxError('Invalid assignment syntax')

        variable = self.a.children[0].children[0]
        value = Interpreter(self.a.children[1], self.variables).execute()

        self.variables[variable] = value

        return value

    def bool_to_int(self, b):
        return 1 if b else 0
