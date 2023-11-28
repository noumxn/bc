from parsor import ast, Parsor
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


class StatementParser(object):
    def __init__(self, statement, block_comment):
        self.statement = statement
        self.index = 0
        self.block_comment = block_comment
        self.block_comment_ended = False

    def parse(self):
        # Remove commented code from statement
        self.sanitize_statement()

        if self.block_comment:
            return {'statement': self.statement, 'block_comment': True}

        if self.block_comment_ended:
            return {'statement': self.statement, 'block_comment': False}

        while self.index < len(self.statement):
            if self.index == 0 and self.statement.startswith('print'):
                if len(self.statement) > 5 and self.statement[5] != ' ':
                    self.index = 5
                    continue
                linestatement = self.statement[6:].strip()
                linestatement = linestatement.split(',')
                if not linestatement:
                    return self.print_eval_dict_builder('print', [])
                else:
                    printlist = [Parsor(i).execute() for i in linestatement]
                    return self.print_eval_dict_builder('print', printlist)

            if self.statement[self.index] == ' ':
                self.index += 1
                continue

            if self.statement[self.index:self.index + 2] in op_equals_symbols:
                return self.parse_op_equate()

            if self.statement[self.index:self.index + 3] in bool_equals_symbols:
                return self.parse_op_bool_equate()

            if self.statement[self.index] == '=':
                return self.parse_equate()

            self.index += 1

        self.statement = self.statement.strip()

        if self.statement:
            return self.print_eval_dict_builder('eval', Parsor(self.statement).execute())

    def sanitize_statement(self):
        if self.block_comment:
            comment_type = '*/'
            comment_idx = self.find_comment_type(self.statement, comment_type)

            if comment_idx is None:
                self.statement = ''
                return
        else:
            comment_type, comment_idx = self.find_any_comment(
                self.statement
            )

        if not comment_type:
            return True

        if comment_type == '#':
            self.statement = self.statement[:comment_idx]
            return True

        if comment_type == '/*':
            new_statement = self.statement[:comment_idx]
            end_comment_idx = self.find_comment_type(
                self.statement[comment_idx:], '*/'
            )
            if end_comment_idx:
                new_statement += self.statement[
                    comment_idx + end_comment_idx + 2:
                ]
                self.statement = new_statement
                self.block_comment = False
                self.block_comment_ended = True
                # Calling sanitize statement again to check for any other comments
                self.sanitize_statement()
            else:
                self.statement = new_statement
                self.block_comment = True
                self.block_comment_ended = False

        if comment_type == '*/':
            if not self.block_comment:
                raise SyntaxError('Unexpected */')

            new_statement = self.statement[comment_idx + 2:]
            self.statement = new_statement
            self.block_comment = False
            self.block_comment_ended = True
            # Calling sanitize statement again to check for any other comments
            self.sanitize_statement()

    def find_any_comment(self, statement):
        comment_idxs = [
            statement.index(i)
            for i in ('#', '/*', '*/')
            if i in statement
        ]
        idx = min(comment_idxs) if len(comment_idxs) > 0 else None

        if idx is None:
            return (None, statement)

        return ('#' if statement[idx] == '#' else statement[idx:idx+2], idx)

    def find_comment_type(self, statement, type):
        if not type or not statement:
            return None

        if type == '#':
            return statement.index('#') if '#' in statement else None

        if type == '/*':
            return statement.index('/*') if '/*' in statement else None

        if type == '*/':
            return statement.index('*/') if '*/' in statement else None

        return None

    def parse_equate(self):
        variable = self.statement[:self.index].strip()
        expression = self.statement[self.index+1:].strip()
        if not expression or not variable:
            raise SyntaxError('parse error')

        VariableNameChecker(variable).validate()

        return self.assign_dict_builder(
            variable,
            Parsor(expression).execute()
        )

    def parse_op_equate(self):
        if self.statement[self.index:self.index+2] not in op_equals_symbols:
            raise SyntaxError('parse error')
        return self.parse_op_equate_helper(2)

    def parse_op_bool_equate(self):
        if self.statement[self.index:self.index+3] not in bool_equals_symbols:
            raise SyntaxError('parse error')
        return self.parse_op_equate_helper(3)

    def parse_op_equate_helper(self, length):
        variable = self.statement[:self.index].strip()
        operation = self.statement[self.index:self.index+length]
        expression = self.statement[self.index+length:].strip()
        if not expression or not variable:
            raise SyntaxError('parse error')

        VariableNameChecker(variable).validate()

        return self.assign_dict_builder(
            variable,
            Parsor(
                f'{variable}{operation.replace("=", "")}{expression}'
            ).execute()
        )

    def assign_dict_builder(self, key, value):
        return {
            'type': 'assign',
            'variable': key,
            'value': value
        }

    def print_eval_dict_builder(self, typ, value):
        return {
            'type': typ,
            'value': value
        }
