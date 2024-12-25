"""a module containing Classes and functions to parse and manage command strings"""

from typing import Iterable
from .parser import eval_args


class PrefixError(Exception):
    """raise when str doesn't starts with prefix(s)"""


def get_word(string: str) -> str:
    """take whatever the first word of string

    Parameters
    ----------
        string: str
                the string to take the first word

    Returns
    -------
        str
                the first word of the string
    """
    return str(string).split()[0]


def skip_prefix(string: str, prefix: str):
    """skip prefix(s) if string doesn't starts with prefix(s) raise PrefixError()
    if string equal prefix returns an empty string("") else remove the prefix
    """
    if not string.startswith(prefix):
        raise PrefixError(f"the {string!r} doesn't start with prefix({prefix!r})")
    return string.removeprefix(prefix)


# Base.py
class CommandError(Exception):
    """basic CommandError exception"""


class InvalidCommandError(CommandError):
    """when entered a command doesn't start with prefix or command is None or empty"""


class CommandParser:
    """
    A class to parse and manage command strings with a specified prefix.
    """

    prefix: str
    """The prefix that command strings must start with."""

    def parse(self, string: str) -> Iterable[str]:
        """parse the input string

        Parameters
        ----------
            string: str
                the string to parse

        Returns
        -------
            Iterable[str]
                the parsed string
        """
        return str.split(skip_prefix(string, self.prefix))

    def __init__(self, prefix: str):
        if not isinstance(prefix, str):
            raise ValueError(
                f"excepted str but got ({type(prefix).__name__!r}) instead"
            )
        if " " in prefix:
            raise PrefixError("prefix should not contain spaces")
        self.prefix = prefix

    def startswith_prefix(self, string: str) -> bool:
        """check if the input string start with prefix(s)"""
        return string.startswith(self.prefix)

    def process_string(
        self, expected_args: list[str], string: str, allow_overflow: bool = True
    ) -> tuple[dict[str, str | list[str]], list[str]]:
        """wrapper function of eval_args


        Parameters
        ----------
            expected_args: list[str]
                the format of the arguments
            string: str
                string to be split
            allow_overflow: bool (default: True)
                whether to allow extra arguments

        Raises
        ------
            InvalidCommandError
                if the command doesn't start with prefix or command is None or empty

        Returns
        -------
            tuple[dict[str, str | list[str]], list[str]]
                tuple of two elements; the arguments, the remaining arguments

        """
        if self.startswith_prefix(string):
            return eval_args(
                expected_args, self.parse(string.strip()), allow_overflow=allow_overflow
            )
        raise InvalidCommandError(f"command must start with prefix({self.prefix!r})")

    def get_command_name(self, string: str):
        """get command name from string

        Parameters
        ----------
            string: str
                string to be parsed

        Returns
        -------
            str
                command name
        """
        args = self.parse(string)
        return args[0] if args else ""

    def get_command_args(self, string: str):
        """get command args from string

        Parameters
        ----------
            string: str
                string to be parsed

        Returns
        -------
            list[str]
                command args
        """
        args = self.parse(string)[1::]  # remove the command name
        return args
