import ast
from dataclasses import dataclass
from textwrap import indent
from modules.token import TokenType, Token

from typing import List, Tuple, Set, Optional, Iterator
from types import CodeType


@dataclass
class Command:
    name: str
    args: List[str]

@dataclass
class RedirectTable:
    inp: Optional[str]
    output: Optional[str]
    output_mode: str

@dataclass
class CommandArray:
    commands: List[Command]
    redirect_table: RedirectTable

class Parser:
    def __init__(self):
        self.current_token = Token(TokenType.UNEXP)

    def _parse(self, tokens_iter: Iterator[Token]) -> Iterator[CommandArray]:

        def match(types: Set[TokenType]) -> bool:
            return self.current_token.token_type in types

        def command_name() -> str:
            if match({TokenType.WORD}):
                name: str = self.current_token.literal
                self.current_token = next(tokens_iter)
                return name
            raise Exception("Syntax error")
            ## TODO RAISE SYNTAX ERROR smh

        def command() -> Command:
            cmd_name: str = command_name()
            cmd = Command(cmd_name, [])
            while match({TokenType.WORD}):
                cmd.args.append(self.current_token.literal)
                self.current_token = next(tokens_iter)
            return cmd

        def redirect() -> Tuple[TokenType, str]:
            red_type = self.current_token.token_type
            self.current_token = next(tokens_iter)
            if match({TokenType.WORD}):
                file_name = self.current_token.literal
                self.current_token = next(tokens_iter)
                return red_type, file_name
            raise Exception("Syntax error")
            ## TODO RAISE SYNTAX ERROR

        def command_arr() -> CommandArray:
            redirect_tokens_map = {
                TokenType.REDOUT: "w",
                TokenType.DOUBLE_REDOUT: "a"
            }

            cmd_arr = CommandArray([command()], RedirectTable(None, None, 'w'))

            while match({TokenType.PIPE}):
                self.current_token = next(tokens_iter)
                cmd_arr.commands.append(command())

            while match({TokenType.REDIN, TokenType.REDOUT, TokenType.DOUBLE_REDOUT}):
                red_token, file_name = redirect()
                if red_token == TokenType.REDIN:
                    cmd_arr.redirect_table.inp = file_name
                else:
                    cmd_arr.redirect_table.output = file_name
                    cmd_arr.redirect_table.output_mode = redirect_tokens_map[red_token]
            return cmd_arr

        self.current_token = next(tokens_iter)

        yield command_arr()
        while not match({TokenType.EOS}):
            if match({TokenType.SEMICOLON, TokenType.NEWLINE}):
                self.current_token = next(tokens_iter)
                continue
            yield command_arr()

        self.current_token = Token(TokenType.UNEXP)
        ## TODO RAISE SYNTAX ERROR

    def get_code_obj(self, tokens: List[Token]) -> CodeType:
        def parse_cmd(cmd: Command) -> str:
            return f"{cmd.name}({cmd.args})"
            ##return f"{cmd.name}(" + ", ".join(f'"{arg}"' for arg in cmd.args) + ")"


        def get_code_blocks() -> Iterator[str]:
            for cmd_array in self._parse(tokens_iter):

                code_block: str = f"res: str = {parse_cmd(cmd_array.commands[-1])}\n" + \
                     f"print(res, end='', file=namespace.output_stream)\n"

                for cmd in reversed(cmd_array.commands[:-1:]):
                    code_block = f"with io.StringIO({parse_cmd(cmd)}) as namespace.current_input_stream:\n" + \
                                    indent(code_block, "\t")

                withitems = []

                if cmd_array.redirect_table.inp:
                    withitems.append(f"open('{cmd_array.redirect_table.inp}', 'r') as namespace.current_input_stream")

                if cmd_array.redirect_table.output:
                    withitems.append(
                        f"open('{cmd_array.redirect_table.output}', '{cmd_array.redirect_table.output_mode}') as namespace.output_stream"
                    )

                if withitems:
                    code_block = f"with {', '.join(withitems)}:\n" + indent(code_block, "\t")

                yield code_block

        tokens_iter = iter(tokens)

        code_string: str = "namespace.current_input_stream = default_input\nnamespace.output_stream = default_output\n" + \
            "\n".join(get_code_blocks())

        return compile(code_string, "<SHELL>", "exec")
