from typing import Any
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


class token():
    typ: str
    val: str

    def __init__(self, typ, val):
        """
        >>> token('sym', '(')
        token('sym', '(')
        """
        self.typ = typ
        self.val = val

    def __repr__(self):
        return f'token({self.typ!r}, {self.val!r})'


class Lexer(object):
    def __init__(self, s: str) -> None:
        self.tokens = []
        self.i = 0
        self.s = s

    def execute(self) -> list[token]:
        while self.i < len(self.s):
            if self.s[self.i].isspace():
                self.evaluate_space()
            elif self.s[self.i].isalpha():
                self.evaluate_alpha()
            elif self.s[self.i].isdigit():
                self.evaluate_digit()
            elif self.s[self.i:self.i+2] in boolean_symbols:
                self.evaluate_boolean_symbol()
            elif self.s[self.i] == '!':
                self.evaluate_symbol()
            elif self.s[self.i:self.i+2] in double_len_symbols:
                self.evaluate_double_symbol()
            elif self.s[self.i] in single_len_symbols:
                self.evaluate_symbol()
            else:
                raise SyntaxError(f'unexpected character {self.s[self.i]}')

        return [token for token in self.tokens if token.typ != 'space']

    def evaluate_space(self):
        """
        >>> lexer = Lexer('3 + 4')
        >>> lexer.execute()
        [token('fl', '3'), token('sym', '+'), token('fl', '4')]
        >>> lexer.tokens
        [token('fl', '3'), token('space', ' '), token('sym', '+'), token('space', ' '), token('fl', '4')]
        """
        self.tokens.append(token('space', " "))
        self.i += 1

    def evaluate_alpha(self):
        end = self.i + 1
        while end < len(self.s) and (self.s[end].isalnum() or self.s[end] == '_'):
            end += 1
        assert end >= len(self.s) or not (
            self.s[end].isalnum() or self.s[end] == '_')

        word = self.s[self.i:end]

        if word in keywords:
            self.tokens.append(token('kw', word))
        else:
            self.tokens.append(token('var', word))

        self.i = end

    def evaluate_digit(self):
        end = self.i + 1
        while end < len(self.s) and (self.s[end] == '.' or self.s[end].isdigit()):
            end += 1
        assert end >= len(self.s) or not (
            self.s[end] == '.' or self.s[end].isdigit())

        self.tokens.append(token('fl', self.s[self.i:end]))

        self.i = end

    def evaluate_boolean_symbol(self):
        self.tokens.append(token('sym', self.s[self.i:self.i+2]))
        self.i += 2

    def evaluate_symbol(self):
        self.tokens.append(token('sym', self.s[self.i]))
        self.i += 1

    def evaluate_double_symbol(self):
        if (self.s[self.i:self.i+2] == '++' or self.s[self.i:self.i+2] == '--'):
            symbol = self.s[self.i:self.i+2]
            if self.tokens and self.tokens[-1].typ == 'var':
                # If the previous token is a variable, this is a post-sym operator
                self.tokens.append(token('sym', symbol))
                self.i += 2
            elif not self.tokens or self.tokens[-1].typ == 'space' or self.tokens[-1].val not in ["-", "+", '--', '++']:
                # If the previous token is a space, we can safely assume the next token is a variable
                self.tokens.append(token('sym', symbol))
                self.i += 2
            else:
                # Otherwise, we raise error?
                raise SyntaxError(
                    f'unexpected symbol {self.s[self.i:self.i+2]}'
                )
            return
        self.tokens.append(token('sym', self.s[self.i:self.i+2]))
        self.i += 2
