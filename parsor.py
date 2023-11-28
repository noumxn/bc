from typing import Any
from lexer import token, Lexer
from variable_name_checker import VariableNameChecker
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


class ast:
    typ: str
    children: tuple[Any, ...]
    post_op: Any

    def __init__(self, typ: str, *children: Any):
        self.typ = typ
        self.children = children
        self.post_op = None

    def __repr__(self):
        return f'ast({self.typ!r}, {", ".join([repr(c) for c in self.children])})'

    def add_post_op(self, post_op: Any):
        self.post_op = post_op


class Parsor(object):
    def __init__(self, s) -> None:
        self.s = s
        self.ts = []

    def execute(self):
        self.ts = Lexer(self.s).execute()

        a, i = self.bool_and_or(0)

        if i != len(self.ts):
            raise SyntaxError(f"expected EOF, found {self.ts[i:]!r}")

        return a

    def bool_and_or(self, i: int) -> tuple[ast, int]:
        """
        >>> Parsor('x && y').execute()
        ast('&&', ast('var', 'x'), ast('var', 'y'))
        >>> Parsor('!x').execute()
        ast('!', ast('var', 'x'))
        """
        if i >= len(self.ts):
            raise SyntaxError('expected boolean, found EOF')

        lhs, i = self.boolean_neg(i)

        while i < len(self.ts) and self.ts[i].typ == 'sym' and self.ts[i].val in boolean_symbols:
            val = self.ts[i].val
            rhs, i = self.boolean_neg(i+1)
            lhs = ast(val, lhs, rhs)

        return lhs, i

    def boolean_neg(self, i: int) -> tuple[ast, int]:
        """
        >>> Parsor('!x').execute()
        ast('!', ast('var', 'x'))
        """
        if i >= len(self.ts):
            raise SyntaxError('expected boolean, found EOF')

        if self.ts[i].typ == 'sym' and self.ts[i].val == '!':
            a, i = self.boolean_neg(i+1)
            return ast('!', a), i
        else:
            return self.relational(i)

    def relational(self, i: int) -> tuple[ast, int]:
        """
        >>> Parsor('x < y').execute()
        ast('<', ast('var', 'x'), ast('var', 'y'))
        """
        if i >= len(self.ts):
            raise SyntaxError('expected relational, found EOF')

        lhs, i = self.plus_or_minus(i)

        while i < len(self.ts) and self.ts[i].typ == 'sym' and self.ts[i].val in relational_symbols:
            val = self.ts[i].val
            rhs, i = self.plus_or_minus(i+1)
            lhs = ast(val, lhs, rhs)

        return lhs, i

    def plus_or_minus(self, i: int) -> tuple[ast, int]:
        if i >= len(self.ts):
            raise SyntaxError('expected plus_or_minus, found EOF')

        lhs, i = self.mul_or_div(i)

        while i < len(self.ts) and self.ts[i].typ == 'sym' and self.ts[i].val in disj_symbols:
            val = self.ts[i].val
            rhs, i = self.mul_or_div(i+1)
            lhs = ast(val, lhs, rhs)

        return lhs, i

    def mul_or_div(self, i: int) -> tuple[ast, int]:
        if i >= len(self.ts):
            raise SyntaxError('expected mul_or_div, found EOF')

        lhs, i = self.power(i)

        while i < len(self.ts) and self.ts[i].typ == 'sym' and self.ts[i].val in conj_symbols:
            val = self.ts[i].val
            rhs, i = self.power(i+1)
            lhs = ast(val, lhs, rhs)

        return lhs, i

    # Right associative power conjunction

    def power(self, i: int) -> tuple[ast, int]:
        """
        >>> Parsor('2 ^ 3').execute()
        ast('^', ast('fl', 2.0), ast('fl', 3.0))
        """
        if i >= len(self.ts):
            raise SyntaxError('expected power conjunction, found EOF')

        lhs, i = self.neg(i)

        if (i < len(self.ts) and self.ts[i].typ == 'sym' and self.ts[i].val == '^'):
            rhs, i = self.power(i+1)
            lhs = ast('^', lhs, rhs)

        return lhs, i

    def neg(self, i: int) -> tuple[ast, int]:
        """
        >>> Parsor('-1').execute()
        ast('-', ast('fl', 1.0))
        """

        if i >= len(self.ts):
            raise SyntaxError('expected negation, found EOF')

        if self.ts[i].typ == 'sym' and self.ts[i].val in neg_symbols:
            val = self.ts[i].val
            a, i = self.neg(i+1)
            return ast(val, a), i
        else:
            return self.incr_and_decr(i)

    def incr_and_decr(self, i: int) -> tuple[ast, int]:
        # pre and post incr and decr implemented
        # They are non-associative

        if i >= len(self.ts):
            raise SyntaxError('expected incr/decr, found EOF')

        if self.ts[i].typ == 'sym' and self.ts[i].val in incr_or_decr_symbols:
            val = self.ts[i].val
            if self.ts[i+1].typ != 'var':
                raise SyntaxError(
                    f'expected variable, found {self.ts[i+1].typ}'
                )
            a, i = self.atom(i+1)
            return ast(val, a), i

        if self.ts[i].typ == 'var' and i+1 < len(self.ts) and self.ts[i+1].typ == 'sym' and self.ts[i+1].val in incr_or_decr_symbols:
            op = self.ts[i+1].val
            var = self.ts[i].val
            ast_node = ast('var', var)
            ast_node.add_post_op(ast(op, ast('var', var)))
            return ast_node, i+2

        return self.atom(i)

    def atom(self, i: int) -> tuple[ast, int]:
        if i >= len(self.ts):
            raise SyntaxError('expected negation, found EOF')

        t = self.ts[i]

        if t.typ == 'var':
            VariableNameChecker(t.val).validate()
            return ast('var', t.val), i+1
        elif t.typ == 'fl':
            return ast('fl', float(t.val)), i+1
        elif t.typ == 'sym' and t.val == '(':
            a, i = self.bool_and_or(i + 1)

            if i >= len(self.ts):
                raise SyntaxError(f'expected right paren, got EOF')

            if not (self.ts[i].typ == 'sym' and self.ts[i].val == ')'):
                raise SyntaxError(f'expected right paren, got "{self.ts[i]}"')

            return a, i + 1

        raise SyntaxError(f'expected atom, got "{self.ts[i]}"')
