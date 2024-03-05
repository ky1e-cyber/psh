import re
from modules.token import Token, TokenType
from typing import Tuple, Iterator, List, Set, Dict, TextIO

def lexer_lines(input_stream: TextIO) -> Iterator[List[Token]]:

    
    def match_word(segment: str) -> Tuple[Token, str]:
        pos: int = 0
        for char in segment:
            if ((re.match(re_whitespaces, char)) or 
             (char in token_chars_set) or (char in str_chars_set)):
                break
            pos += 1

        word = segment[:pos]

        if word.isdecimal():
            return (Token(TokenType.NUMBER, int(word)), 
                    segment[pos::])

        return (Token(TokenType.WORD, literal=segment[:pos]) 
                    if word not in keywords.keys() 
                    else Token(keywords[word]), 
                segment[pos::])

    def match_string(segment: str, term_char: str) -> Tuple[Token, str]:
        pos: int = segment.find(term_char)
        return ( (Token(TokenType.WORD, literal=segment[:pos]), segment[pos + 1:]) 
                    if pos != -1
                    else (Token(TokenType.UNEXP), "") )

    re_whitespaces = re.compile(r"[ \t]+")

    single_char_map: Dict[str, TokenType] = {
        '<' : TokenType.REDIN,
        '|' : TokenType.PIPE,
        ';' : TokenType.SEMICOLON,
        '=' : TokenType.BIND,
        '\n': TokenType.NEWLINE,
        '+' : TokenType.PLUS,
        '-' : TokenType.MINUS,
        '*' : TokenType.STAR,
        '/' : TokenType.SLASH,
        '{' : TokenType.LBRACKET,
        '}' : TokenType.RBRACKET,
        '(' : TokenType.LPAREN,
        ')' : TokenType.RPAREN,
        ',' : TokenType.COMMA
    }

    double_char_map: Dict[str, Tuple[str, TokenType, TokenType]] = {
        '>': ('>', TokenType.REDOUT, TokenType.DOUBLE_REDOUT)
    }

    keywords: Dict[str, TokenType] = {
        "let" : TokenType.LET,
        "fn"  : TokenType.FN,
        "eq"  : TokenType.EQ,
        "ne"  : TokenType.NE,
        "lt"  : TokenType.LT,
        "le"  : TokenType.LE,
        "gt"  : TokenType.GT,
        "ge"  : TokenType.GE,
        "not" : TokenType.NOT
    }

    token_chars_set: Set[str] =\
        set(single_char_map.keys()).union(set(double_char_map.keys()))

    str_chars_set: Set[str] = {"'", '"'}

    for line in input_stream:
        tokens_line: List[Token] = []

        while len(line) > 0:
            ws_match = re.match(re_whitespaces, line)
            if ws_match:
                line = line[ws_match.end()::]

            char = line[0]

            if char in single_char_map.keys():
                line = line[1::]
                tokens_line.append(Token(single_char_map[char]))

            elif char in double_char_map.keys():
                match_char, token_unmatch, token_match =\
                    double_char_map[char]
                line = line[1::]
                if len(line) >= 1 and line[0] == match_char:
                    tokens_line.append(Token(token_match))
                    line = line[1::]
                else:
                    tokens_line.append(Token(token_unmatch))

            elif char in str_chars_set:
                token, line = match_string(line[1::], char)
                tokens_line.append(token) 

            else:
                token, line = match_word(line)
                tokens_line.append(token) 
                
        yield tokens_line

    yield [Token(TokenType.EOS)]
