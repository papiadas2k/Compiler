import sys
import re
import os.path
from os import path

INTEGER = 'INTEGER'
PLUS = 'PLUS'
MINUS = 'MINUS'
MUL = 'MUL'
LPAREN = '('
RPAREN = ')'
EOF = 'EOF'

class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def next_char(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.next_char()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.next_char()
        return int(result)

    def next_token(self):
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return SyntaxToken(INTEGER, self.integer())

            if self.current_char == '+':
                self.next_char()
                return SyntaxToken(PLUS, '+')

            if self.current_char == '-':
                self.next_char()
                return SyntaxToken(MINUS, '-')

            if self.current_char == '*':
                self.next_char()
                return SyntaxToken(MUL, '*')

            if self.current_char == '(':
                self.next_char()
                return SyntaxToken(LPAREN, '(')

            if self.current_char == ')':
                self.next_char()
                return SyntaxToken(RPAREN, ')')

            print("Syntax Error: ", self.current_char)
            sys.exit(1)

        return SyntaxToken(EOF, None)

class SyntaxToken(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

class Operator:
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Num:
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.next_token()
        else:
            print("Invalid token: "+self.current_token.type)
            sys.exit(0);

    def factor(self):
        token = self.current_token
        if token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node

    def term(self):
        node = self.factor()
        while self.current_token.type == MUL:
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            node = Operator(left=node, op=token, right=self.factor())
        return node

    def expr(self):
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)

            node = Operator(left=node, op=token, right=self.term())

        return node

    def parse(self):
        return self.expr()

class Interpreter:
    def __init__(self, parser):
        self.parser = parser

    def visit_Operator(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)

    def visit_Num(self, node):
        return node.value

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)

    def visit(self, node):
        if type(node).__name__ == "Num":
            return self.visit_Num(node)
        elif type(node).__name__ == "Operator":
            return self.visit_Operator(node)
        else:
            print("Error 3")
            sys.exit()

variables = {}

def divide_exp(exp):
    global variables
    values = {}
    vars = re.findall('[_a-z]\w*', exp)

    if re.match('[0][0-9]', exp.strip()) is not None:
        print("Invalid")
        sys.exit(0)

    for i in range(len(vars)):
        if vars[i] not in variables:
            print("Invalid" )
            sys.exit(0)
        values[vars[i]] = variables[vars[i]]

    for i in vars:
        exp = exp.replace(i, str(variables[i]))

    if re.match('[a-z]|[A-Z]|_', exp) is not None:
        sys.exit(0)
    return exp


def evaluate(text):
    lexer = Lexer(text)

    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    result = interpreter.interpret()
    return result

def get_minus_plus(lis):
    ret = []
    for i in range(len(lis)):
        lis[i] = lis[i][0]
        if '-' in lis[i]:
            ret.append('-')
        else:
            ret.append('+')
    return ret


def evaluate_expression(line):
    global variables
    exp = divide_exp(line.strip())
    exp = exp.replace(';', '')
    plus_minus = re.findall(r'(((\++)|(-+))+)', exp)

    plus_minus_2 = get_minus_plus(plus_minus)
    for i in range(len(plus_minus)):
        exp = exp.replace(plus_minus[i], plus_minus_2[i])

    mul = 1
    exp = exp.strip()
    if exp[0] == '+':
        exp = exp[1:]

    if exp[0] == '-':
        exp = exp[1:]
        mul = -1

    return evaluate(exp) * mul

def process_user_input(inputs):
    for i in range(len(inputs)):
       inputs[i] = inputs[i].strip().split("=");

    for i in inputs:
        if len(i) >= 2:
            variables[i[0].strip()] = evaluate_expression(i[1].strip())
        else:
            print("Invalid expression: " + i[0])
            sys.exit(0);


    print("User Input: {}".format(user_input))
    print("Output: {}".format(user_input))
    for i in sorted(variables):
        print("{}  = {}".format(i, variables[i]))

user_input = input("Please enter input: ")
user_input_data = user_input.split(';')
user_input_data.remove("")
process_user_input(user_input_data);
