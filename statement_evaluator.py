import re
from parsor import ast, Parsor
from statement_parser import StatementParser
from interpreter import Interpreter
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


class StatementEvaluator(object):
    def __init__(self, statements):
        self.statements = statements
        self.variables = {}
        self.parsed_statements = []
        self.parse_paused_statement = None
        self.printlist = []
        self.in_block_comment = False

    def execute(self):
        try:
            self.parse()
        except (SyntaxError, ValueError):
            print("parse error")
            return

        try:
            self.evaluate()
        except ZeroDivisionError:
            print(*(self.printlist + ["divide by zero"]))
            return

    def parse(self):
        for statement in self.statements:
            self.parse_statement(statement)

    def parse_statement(self, statement):
        statement = statement.strip()
        if not statement:
            return

        parsed_statement = StatementParser(
            statement, self.in_block_comment
        ).parse()
        if parsed_statement.get('block_comment', False):
            self.in_block_comment = True
            if not self.parse_paused_statement:
                self.parse_paused_statement = ''
            self.parse_paused_statement += parsed_statement['statement']
            return
        else:
            if self.in_block_comment:
                self.in_block_comment = False
                self.parse_paused_statement += parsed_statement['statement']
                # Start parsing again from the beginning
                self.parse_statement(self.parse_paused_statement)
                # Reset the paused statement
                self.parse_paused_statement = None
                return

        self.parsed_statements.append(parsed_statement)

    def evaluate(self):
        """
        Doctests for all operators

        """
        if not self.parsed_statements:
            return

        for statement in self.parsed_statements:
            if statement['type'] == 'print':
                self.printlist = []
                if not statement['value']:
                    print()
                    continue

                for item in statement['value']:
                    if isinstance(item, str):
                        self.printlist.append(item)
                    else:
                        val = Interpreter(item, self.variables)
                        result = val.execute()
                        self.printlist.append(result)
                print(*self.printlist, sep=' ')
                self.printlist = []
            elif statement['type'] == 'assign':
                self.variables[statement['variable']] = Interpreter(
                    statement['value'], self.variables
                ).execute()
            else:
                Interpreter(
                    statement['value'], self.variables
                ).execute()
