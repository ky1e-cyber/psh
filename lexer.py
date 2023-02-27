import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import Tuple, Set, Dict, List, Optional, Iterator, TextIO


class TokenType(Enum):
    UNEXP = auto()

    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    MINUS = auto()
    PLUS = auto()
    SLASH = auto()
    STAR = auto()
    PIPE = auto()
    REDIN = auto()
    REDOUT = auto()
    EQUAL = auto()
    DOLLAR = auto()

    DOUBLE_REDOUT = auto()
    DOUBLE_AND = auto()
    DOUBLE_PIPE = auto()

    IDENTIFIER = auto()
    NUMBER = auto()

    IF = auto()
    ELSE = auto()
    TRUE = auto()
    FALSE = auto()
    RETURN = auto()
    DEF = auto()

    SEPARATOR = auto()
    SEMICOLON = auto()
    NEWLINE = auto()
    EOS = auto()


@dataclass(frozen=True)
class Token:
    token_type: TokenType
    literal: Optional[str] = None


def lexer_lines(input_stream: TextIO) -> Iterator[List[Token]]:

    def _match_identifier(segment: str) -> Tuple[Token, str]:
        def _match_quoted(term_char: str) -> Tuple[str, int]:
            term_pos = segment[pos + 1::].find(term_char)
            return (
                (segment[pos + 1:term_pos]
                    if term_pos != -1 else ""),
                term_pos
            )

        literal = ""
        pos = 0

        while pos < len(segment):
            if ((re.match(re_whitespaces, segment[pos]))
                    or (segment[pos] in _terminators_set)) or (segment[pos] in _not_in_identifier_set):
                break
            elif segment[pos] in _str_chars_set:
                quoted, term = _match_quoted(segment[pos])
                if term == -1:
                    return Token(TokenType.UNEXP), ""
                literal += quoted
                pos = term + 1
                continue
            literal += segment[pos]
            pos += 1


        return Token(TokenType.IDENTIFIER, literal=literal), segment[pos::]

    re_whitespaces = re.compile(r"[ \t]+")

    _double_char_map = {
        '>': ('>', TokenType.REDOUT, TokenType.DOUBLE_REDOUT),
        '&': ('&', TokenType.UNEXP, TokenType.DOUBLE_AND),
        '|': ('|', TokenType.PIPE, TokenType.DOUBLE_PIPE)
    }
    _single_char_map = {
        '<': TokenType.REDIN,
        '$': TokenType.DOLLAR,
        '(': TokenType.LEFT_PAREN,
        ')': TokenType.RIGHT_PAREN,
        '{': TokenType.LEFT_BRACE,
        '}': TokenType.RIGHT_BRACE,
        ',': TokenType.COMMA,
        '-': TokenType.MINUS,
        '+': TokenType.PLUS,
        '/': TokenType.SLASH,
        '*': TokenType.STAR,
        '=': TokenType.EQUAL,
        ';': TokenType.SEPARATOR,
        '\n': TokenType.SEPARATOR
    }

    _keywords_map = {
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "True": TokenType.TRUE,
        "False": TokenType.FALSE,
        "return": TokenType.RETURN,
        "def": TokenType.DEF
    }

    _not_in_identifier_set = (
        set(_single_char_map.keys())
        .union(set(_double_char_map.keys()))
        .difference({'-', '+', ',', '/', '*'})
    )
    _terminators_set = {"\n", ";"}
    _token_chars_set = (
        set(_single_char_map.keys())
        .union(set(_double_char_map.keys()))
    )
    _str_chars_set = {"'", '"'}

    for line in input_stream:
        tokens_line: List[Token] = []

        while len(line) > 0:
            whitespace_match = re.match(re_whitespaces, line)
            if whitespace_match:
                line = line[whitespace_match.end()::]

            char = line[0]

            if char in _single_char_map.keys():
                line = line[1::]
                tokens_line.append(Token(_single_char_map[char]))

            elif char in _double_char_map.keys():
                match_char, token_unmatch, token_match = \
                    _double_char_map[char]
                line = line[1::]
                if len(line) >= 1 and line[0] == match_char:
                    tokens_line.append(Token(token_match))
                    line = line[1::]
                else:
                    tokens_line.append(Token(token_unmatch))

            else:
                token, line = _match_identifier(line)
                tokens_line.append(token)
        tokens_line.append(Token(TokenType.EOS))
        yield tokens_line
