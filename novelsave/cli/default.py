import argparse

from typing import List, Text, Tuple


class DefaultSubcommandArgumentParser(argparse.ArgumentParser):
    __default_subparser = None

    def set_default_subparser(self, name):
        self.__default_subparser = name

    def _parse_known_args(self, arg_strings: List[Text], namespace: argparse.Namespace) \
            -> Tuple[argparse.Namespace, List[str]]:

        in_args = set(arg_strings)
        d_sp = self.__default_subparser
        if d_sp is not None and not {'-h', '--help'}.intersection(in_args):
            for x in self._subparsers._actions:
                subparser_found = (
                        isinstance(x, argparse._SubParsersAction) and
                        in_args.intersection(x._name_parser_map.keys())
                )
                if subparser_found:
                    break
            else:
                # insert default in first position, this implies no
                # global options without a sub_parsers specified
                arg_strings = [d_sp] + arg_strings

        return super(DefaultSubcommandArgumentParser, self)._parse_known_args(arg_strings, namespace)
