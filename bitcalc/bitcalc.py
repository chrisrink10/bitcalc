#!/usr/bin/env python
#
#######################################################################
# bitcalc :: visual bitwise calculator
#
# A read-eval-print loop calculator for bitwise expressions.
#
# Author: Chris Rink <chrisrink10@gmail.com>
#######################################################################
import collections
import enum
import math


class TokenType(enum.Enum):
    """Enumeration of valid token values."""
    Integer = 0
    BitwiseAnd = 1
    BitwiseOr = 2
    BitwiseXOr = 3
    BitwiseNot = 4
    LeftShift = 5
    RightShift = 6
    LeftParen = 7
    RightParen = 8
    Plus = 9
    Minus = 10
    Times = 11
    Divide = 12
    Modulo = 13


class Token:
    """Represents an expression Token."""

    def __init__(self, value, type):
        self.value = value
        self.type = type

    def __int__(self):
        if self.type == TokenType.Integer:
            return int(self.value)
        raise TypeError("Operators cannot be converted to int.")

    def __str__(self):
        return self.value

    def __repr__(self):
        return "Token({v}, {t})".format(
            v=repr(self.value), t=self.type)


class Lexer:
    """Lexer for BitCalc expressions."""
    _INTEGERS = {
        '0': True, '1': True, '2': True, '3': True,
        '4': True, '5': True, '6': True, '7': True,
        '8': True, '9': True
    }
    _OPERATORS = {
        '&': TokenType.BitwiseAnd, '|': TokenType.BitwiseOr,
        '^': TokenType.BitwiseXOr, '~': TokenType.BitwiseNot,
        '+': TokenType.Plus, '-': TokenType.Minus,
        '*': TokenType.Times, '/': TokenType.Divide,
        '(': TokenType.LeftParen, ')': TokenType.RightParen,
        '%': TokenType.Modulo,
    }

    def __init__(self):
        self._expr = None
        self._index = 0
        self._tokens = []
        self._actions = {
            '0': self._lex_int,
            '1': self._lex_int,
            '2': self._lex_int,
            '3': self._lex_int,
            '4': self._lex_int,
            '5': self._lex_int,
            '6': self._lex_int,
            '7': self._lex_int,
            '8': self._lex_int,
            '9': self._lex_int,
            '<': self._lex_shifters,
            '>': self._lex_shifters,
            '&': self._lex_operators,
            '|': self._lex_operators,
            '^': self._lex_operators,
            '~': self._lex_operators,
            '+': self._lex_operators,
            '-': self._lex_int,
            '*': self._lex_operators,
            '%': self._lex_operators,
            '/': self._lex_operators,
            '(': self._lex_operators,
            ')': self._lex_operators,
            ' ': self._advance,
            '\t': self._advance,
        }

    def lex(self, expr):
        """Lex an expression into a series of tokens."""
        self._expr = expr
        self._index = 0
        self._tokens = []

        while self._index < len(self._expr):
            try:
                action = self._actions[self._current]
            except KeyError:
                raise ParserError(self._expr,
                                  "Encountered invalid token '{t}' at {i}".format(
                                      t=self._current, i=self._index))

            token = action()
            if token is not None:
                self._tokens.append(token)

        return self._tokens

    def _advance(self, c=1):
        """Advance the token pointer."""
        self._index += c

    @property
    def _current(self):
        """Get the current character."""
        return self._expr[self._index]

    @property
    def _next(self):
        if self._index + 1 < len(self._expr):
            return self._expr[self._index + 1]
        return None

    def _lex_int(self):
        """Lex an integer value from an expression."""
        t = []

        if self._current == '-':
            if self._next not in Lexer._INTEGERS:
                return self._lex_operators()
            while self._current == '-':
                t.append(self._current)
                self._advance()

        while self._index < len(
                self._expr) and self._current in Lexer._INTEGERS:
            t.append(self._current)
            self._advance()

        return Token("".join(t), TokenType.Integer)

    def _lex_shifters(self):
        """Lex the left and right shift operators."""
        if self._current == ">" and self._next == ">":
            self._advance(2)
            return Token(">>", TokenType.RightShift)
        elif self._current == "<" and self._next == "<":
            self._advance(2)
            return Token("<<", TokenType.LeftShift)
        else:
            raise ParserError(self._expr,
                              "Expected '{t}' at {i}".format(t=self._current,
                                                             i=self._index))

    def _lex_operators(self):
        """Lex the remaining operator values."""
        try:
            val = self._current
            type = Lexer._OPERATORS[self._current]
            self._advance()
            return Token(val, type)
        except KeyError:
            raise ParserError(self._expr,
                              "Encountered invalid token '{t}' at {i}".format(
                                  t=self._current, i=self._index))


class BinaryFormatter:
    """Convenience class for formatting binary values."""

    def __init__(self, vals):
        self._vals = vals
        self._digits = max([BinaryFormatter._binary_digits(x) for x in vals])
        self._negative = any([x < 0 for x in vals])

    @property
    def digits(self):
        return self._digits if not self._negative else self._digits + 1

    def format(self, num):
        """Format a value as consistent binary after being given the
        entire corpus of values."""
        if self._negative:
            if num > 0:
                digit_fmt = "0{0}".format(self._digits)
                return " {{:{}b}}".format(digit_fmt).format(num)
            else:
                digit_fmt = "0{0}".format(self._digits + 1)
                return "{{:{}b}}".format(digit_fmt).format(num)
        else:
            digit_fmt = "0{0}".format(self._digits)
            return "{{:{}b}}".format(digit_fmt).format(num)

    @staticmethod
    def single_format(num):
        digits = BinaryFormatter._binary_digits(num)
        digits = digits + 1 if num < 0 else digits
        digit_fmt = "0{0}".format(digits)
        return "{{:{}b}}".format(digit_fmt).format(num)

    @staticmethod
    def _binary_digits(num):
        """Return the number of binary digits to be displayed for the
        given number in increments of 8."""
        ln = math.log(abs(num), 2) if num != 0 else 1
        ndigits = math.ceil(ln)
        if int(ln) == ln:
            ndigits += 1

        should_pad = ((ndigits % 8) != 0)
        if should_pad:
            ndigits = (int(ndigits / 8) * 8) + 8

        return ndigits


class Expression:
    """Base Expression class for BitCalc expression syntax tree."""
    pass


class BinaryExpression(Expression):
    """Binary Expression tree object for BitCalc."""

    def __init__(self, first, op, second):
        super(Expression, self).__init__()
        self.first = int(first) if isinstance(first, Token) else first
        self.second = int(second) if isinstance(second, Token) else second
        self.op = str(op) if isinstance(op, Token) else op

    def __int__(self):
        return self._val(int(self.first), int(self.second))

    def __str__(self):
        output = []

        if isinstance(self.first, (UnaryExpression, BinaryExpression)):
            output.append(str(self.first))
            output.append("\n\n")

        if isinstance(self.second, (UnaryExpression, BinaryExpression)):
            output.append(str(self.second))
            output.append("\n\n")

        fmt = BinaryFormatter([int(self.first), int(self.second), int(self)])

        fb = fmt.format(int(self.first))
        if self.op not in ['<<', '>>']:
            sb = fmt.format(int(self.second))
        else:
            sb = str(int(self.second))
        rb = fmt.format(int(self))

        output.append(repr(self))
        output.append("\n")
        output.append(fb.rjust(fmt.digits + 4))
        output.append("\n")
        output.append(self.op.center(4))
        output.append(sb.rjust(fmt.digits))
        output.append("\n")
        output.append("".rjust(fmt.digits + 4, "-"))
        output.append("\n")
        output.append(rb.rjust(fmt.digits + 4))

        return "".join(output)

    def __repr__(self):
        return "({0} {1} {2})".format(
            repr(self.first), str(self.op), repr(self.second))

    def _val(self, e1, e2):
        return {
            '&': lambda: e1 & e2,
            '|': lambda: e1 | e2,
            '^': lambda: e1 ^ e2,
            '+': lambda: e1 + e2,
            '-': lambda: e1 - e2,
            '*': lambda: e1 * e2,
            '%': lambda: e1 % e2,
            '/': lambda: e1 / e2,
            '<<': lambda: e1 << e2,
            '>>': lambda: e1 >> e2,
        }[self.op]()


class UnaryExpression(Expression):
    """Unary Expression tree object for BitCalc."""

    def __init__(self, first, op):
        super(Expression, self).__init__()
        self.first = int(first) if isinstance(first, Token) else first
        self.op = str(op) if isinstance(op, Token) else op

    def __int__(self):
        return self._val(int(self.first))

    def __str__(self):
        output = []
        if isinstance(self.first, (UnaryExpression, BinaryExpression)):
            output.append(str(self.first))
            output.append("\n\n")

        fmt = BinaryFormatter([int(self.first), int(self)])

        fb = fmt.format(int(self.first))
        rb = fmt.format(int(self))

        output.append(repr(self))
        output.append("\n")
        output.append(self.op.center(4))
        output.append(fb)
        output.append("\n")
        output.append("".rjust(fmt.digits + 4, '-'))
        output.append("\n")
        output.append(rb.rjust(fmt.digits + 4))

        return "".join(output)

    def __repr__(self):
        return "{0}{1}".format(str(self.op), repr(self.first))

    def _val(self, e1):
        return {
            '-': lambda: -1 * e1,
            '+': lambda: e1,
            '~': lambda: ~e1,
        }[self.op]()


class NumericExpression(Expression):
    """Numeric Expression tree object for BitCalc."""

    def __init__(self, first):
        super(Expression, self).__init__()
        self.first = int(first) if isinstance(first, Token) else first

    def __int__(self):
        return self.first

    def __str__(self):
        return BinaryFormatter.single_format(int(self.first))

    def __repr__(self):
        return "{0}".format(str(self.first))


class Parser:
    """Parser for BitCalc expressions."""

    _PRECEDENCE = [
        {TokenType.BitwiseNot: "right"},
        {TokenType.Times: "left", TokenType.Divide: "left",
         TokenType.Modulo: "left"},
        {TokenType.LeftShift: "left", TokenType.RightShift: "left"},
        {TokenType.Plus: "left", TokenType.Minus: "left"},
        {TokenType.BitwiseAnd: "left"},
        {TokenType.BitwiseXOr: "left"},
        {TokenType.BitwiseOr: "left"},
    ]

    def __init__(self, genpostfix=False):
        self._genpostfix = genpostfix
        self._queue = collections.deque() if genpostfix else None
        self._lexer = Lexer()
        self._result = None
        self._tree = None

    @property
    def postfix(self):
        return str(self._queue) if self._genpostfix else None

    @property
    def result(self):
        return self._result

    @property
    def tree(self):
        return self._tree

    def parse(self, expr):
        """Parse a BitCalc expression."""
        tokens = self._lexer.lex(expr)
        self._queue = collections.deque() if self._genpostfix else None
        self._tree = self._parse_expr(expr, tokens)
        self._result = int(self.tree)

    def _parse_expr(self, expr, tokens):
        """Perform the Shunting Yard algorithm on expression tokens and
        return an expression AST tree."""
        tree = []
        stack = []

        for tok in tokens:
            if tok.type == TokenType.Integer:
                expr = NumericExpression(tok)
                tree.append(expr)
                self._add_to_queue(expr)
            elif tok.type == TokenType.LeftParen:
                stack.append(tok)
            elif tok.type == TokenType.RightParen:
                found = False
                while len(stack) > 0:
                    top = stack[-1]
                    if top.type != TokenType.LeftParen:
                        op = stack.pop()
                        Parser._reduce_expr(tree, op)
                        self._add_to_queue(op)
                    else:
                        found = True
                        stack.pop()
                        break
                if not found:
                    raise ParserError(expr, "Mismatched parentheses")
            else:
                try:
                    if len(stack) > 0 and Parser._should_pop_op(stack, tok):
                        old = stack.pop()
                        Parser._reduce_expr(tree, old)
                        self._add_to_queue(old)
                    stack.append(tok)
                except KeyError as e:
                    raise ParserError(expr, str(e))

        while len(stack) > 0:
            top = stack[-1]
            if top.type == TokenType.RightParen or top.type == TokenType.LeftParen:
                raise ParserError(expr, "Mismatched parentheses")
            Parser._reduce_expr(tree, top)
            self._add_to_queue(top)
            stack.pop()

        if len(tree) != 1:
            raise ParserError(expr, "An internal parser error has occurred.")

        return tree.pop()

    def _add_to_queue(self, tok):
        """Add the input token to the postfix queue if it is being generated."""
        if self._genpostfix:
            self._queue.append(tok)

    @staticmethod
    def _reduce_expr(tree, tok):
        """Reduce multiple operators in an operand tree stack to an
        Expression."""
        second = tree.pop()
        if len(tree) > 0 and not Parser._is_unary_op(tok):
            first = tree.pop()
            expr = BinaryExpression(first, tok, second)
        else:
            expr = UnaryExpression(second, tok)
        tree.append(expr)

    @staticmethod
    def _should_pop_op(stack, new):
        """Determine if the operator at the top of the stack should be used
        before pushing the new operator on the stack."""
        old = stack[-1]

        if old.type == TokenType.LeftParen:
            return False

        oldprec, oldassoc = Parser._op_precedence(old)
        newprec, newassoc = Parser._op_precedence(new)

        if newassoc == "left" and newprec >= oldprec:
            return True
        elif newassoc == "right" and newprec > oldprec:
            return True
        else:
            return False

    @staticmethod
    def _op_precedence(op):
        """Return the operator precedence and associativity."""
        for i, level in enumerate(Parser._PRECEDENCE):
            if op.type in level:
                return i, level[op.type]
        raise KeyError("Invalid operator '{o}' given.".format(o=op))

    @staticmethod
    def _is_unary_op(op):
        """Test if an operator is a unary operatory."""
        if op.type == TokenType.BitwiseNot:
            return True
        return False


class ParserError(Exception):
    """General exception for errors encountered parsing a BitCalc expression."""

    def __init__(self, expr, message):
        self.expr = expr
        self.message = message

    def __str__(self):
        return "Error parsing expression '{expr}': {msg}".format(
            expr=self.expr,
            msg=self.message
        )


def start_repl():
    """Start a BitCalc REPL."""
    print("BitCalc v0.1 - a visual calculator for bitwise expressions")
    print("Use Ctrl+C to quit.\n")
    parser = Parser()

    while True:
        try:
            expr = input(">>> ")
            if len(expr.strip()) == 0:
                continue

            parser.parse(expr)
            print("")
            print(str(parser.tree))
            print(parser.result)
            print("")
        except ParserError as e:
            print(e)
        except KeyboardInterrupt:
            print("")
            raise SystemExit(0)


if __name__ == "__main__":
    start_repl()
