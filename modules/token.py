from dataclasses import dataclass
from enum import Enum, auto

from typing import Any

class TokenType(Enum):
    UNEXP = auto()

    NUMBER = auto()
    WORD = auto()

    LET = auto()
    BIND = auto()
    FN = auto()
    COMMA = auto()

    ## Redirections
    REDIN = auto()
    REDOUT = auto()
    DOUBLE_REDOUT = auto()

    ## Pipe
    PIPE = auto()

    ## End of cmd
    SEMICOLON = auto()
    NEWLINE = auto()

    LBRACKET = auto()
    RBRACKET = auto()

    LPAREN = auto()
    RPAREN = auto()
    
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()

    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()
    NOT = auto()

    # EOS
    EOS = auto()

@dataclass(frozen=True)
class Token:
    token_type: TokenType
    literal: Any = None

