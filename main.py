from enum import Enum
from typing import Callable
import math


# Tokenize
equation = "{sqrt x}"
letters = set(list("abcdefghijklmnopqrstuvwxyz"))
numbers = set(list("0123456789."))

# Tokenizer
class TokenType(Enum):
  LPAREN = 1
  RPAREN = 2
  LCURLY = 3
  RCURLY = 4
  NUMBER = 5
  IDENT = 6
  OPERATOR = 7

class Token:
  type: TokenType
  value: str

  def __init__(self, type, value):
    self.type = type
    self.value = value
  
  def __repr__(self) -> str:
    return f"Token({self.type}, {self.value})"

def tokenize(code: str) -> list[Token]:
  tokens = []
  while len(code) > 0:
    char = code[0]
    if char == "(":
      tokens.append(Token(TokenType.LPAREN, "("))
      code = code[1:]
    elif char == ")":
      tokens.append(Token(TokenType.RPAREN, ")"))
      code = code[1:]
    elif char == "{":
      tokens.append(Token(TokenType.LCURLY, "{"))
      code = code[1:]
    elif char == "}":
      tokens.append(Token(TokenType.RCURLY, "}"))
      code = code[1:]
    elif char == "+":
      tokens.append(Token(TokenType.OPERATOR, "+"))
      code = code[1:]
    elif char == "-":
      tokens.append(Token(TokenType.OPERATOR, "-"))
      code = code[1:]
    elif char == "*":
      tokens.append(Token(TokenType.OPERATOR, "*"))
      code = code[1:]
    elif char == "/":
      tokens.append(Token(TokenType.OPERATOR, "/"))
      code = code[1:]
    elif char == "=":
      tokens.append(Token(TokenType.OPERATOR, "="))
      code = code[1:]
    elif char == "^":
      tokens.append(Token(TokenType.OPERATOR, "^"))
      code = code[1:]
    elif char == " ":
      code = code[1:]
    elif char in letters:
      ident, code = get_ident(code)
      tokens.append(Token(TokenType.IDENT, ident))
    elif char in numbers:
      (num, code) = get_num(code)
      tokens.append(Token(TokenType.NUMBER, num))
    else:
      raise SyntaxError("unknown character: " + char)

  return tokens

def get_ident(code: str) -> tuple[str, str]:
  out = ""
  while (code[0]) in letters:
    out += code[0]
    code = code[1:]
    if len(code) == 0:
      return (out, code)
  return (out, code)

def get_num(code: str) -> tuple[str, str]:
  out = ""
  while (code[0]) in numbers:
    out += code[0]
    code = code[1:]
    if len(code) == 0:
      return (out, code)
  return (out, code)

# Parse
class NodeType(Enum):
  NUMBER = 1
  VARIABLE = 2
  EXPR = 3
  CALL = 4

class Node:
  type: NodeType
  value: any

  def __init__(self, type, value):
    self.type = type
    self.value = value

  def __repr__(self) -> str:
    return f"Node({self.type}, {self.value})"

def parse(tokens: list[Token]) -> tuple[list[Token], Node]:
  tok = tokens[0]
  if tok.type == TokenType.IDENT:
    return tokens[1:], Node(NodeType.VARIABLE, tok.value)

  elif tok.type == TokenType.NUMBER:
    return tokens[1:], Node(NodeType.NUMBER, float(tok.value))

  elif tok.type == TokenType.LPAREN:
    (tokens, val) = parse(tokens[1:])
    tok = tokens[0]
    while tok.type != TokenType.RPAREN:
      op = tok.value
      (tokens, right) = parse(tokens[1:])
      val = Node(NodeType.EXPR, (op, val, right))
      tok = tokens[0]
    return tokens[1:], val

  elif tok.type == TokenType.LCURLY:
    tokens = tokens[1:]
    fn_name = tokens[0].value
    tokens = tokens[1:]
    params: list[Node] = []
    while tokens[0].type != TokenType.RCURLY:
      (tokens, param) = parse(tokens)
      params.append(param)
    tokens = tokens[1:]
    return (tokens, Node(NodeType.CALL, (fn_name, params)))

  raise SyntaxError("unexpected token: " + str(tok))

# Functions
functions: dict[str, Callable[[list[float]], float]] = {
  "sqrt": lambda inp: math.sqrt(inp[0])
}

# Evaluator
def eval_node(node: Node, variables: dict[str, float]) -> float:
  if node.type == NodeType.NUMBER:
    return node.value
  elif node.type == NodeType.VARIABLE:
    return variables[node.value]
  elif node.type == NodeType.EXPR:
    (op, left, right) = node.value
    left = eval_node(left, variables)
    right = eval_node(right, variables)
    if op == "+":
      return left + right
    elif op == "-":
      return left - right
    elif op == "*":
      return left * right
    elif op == "/":
      return left / right
    elif op == "^":
      return left ** right
    else:
      raise SyntaxError("unknown operator: " + op)
  elif node.type == NodeType.CALL:
    (fn_name, params) = node.value
    if fn_name in functions:
      return functions[fn_name]([eval_node(param, variables) for param in params])
    else:
      raise NameError("unknown function: " + fn_name)
  else:
    raise ValueError("unknown node: " + str(node))

# Parse
(_, ast) = parse(tokenize(equation))
print(eval_node(ast, {"x": 4}))