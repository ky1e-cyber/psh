from dataclasses import dataclass
from enum import Enum, auto

class TokenType(Enum):
    UNEXP = auto()

    WORD = auto()
    EQUAL = auto()

    ## Redirections
    REDIN = auto()
    REDOUT = auto()
    DOUBLE_REDOUT = auto()

    ## Pipe
    PIPE = auto()

    ## End of cmd
    SEMICOLON = auto()
    NEWLINE = auto()

    # EOS
    EOS = auto()

@dataclass(frozen=True)
class Token:
    token_type: TokenType
    literal: str = ""

