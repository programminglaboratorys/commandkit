"""module contains a class to manage commands"""

from typing import Callable, Awaitable
from dataclasses import dataclass, field

from .core import CommandParser, CommandError
from .parser import parse_annotation, parse_to_argv


class BadArgument(CommandError):
    """when a parsing command arguments fails"""

    def __init__(self, message, parameters, command):
        super().__init__(message)
        self.parameters = parameters
        self.command = command


class CommandNotFoundError(CommandError):
    """when command doesn't exist"""

    def __init__(self, message, name):
        super().__init__(message)
        self.name = name


@dataclass(slots=True)
class BasicCommand:
    """
    Represents a basic command.
    """

    function: Callable | Awaitable
    """The function or coroutine representing the command."""
    description: str
    """A short description of the command."""
    name: str
    """The name of the command. If not provided, defaults to the function's name."""
    extra: dict = field(default_factory=dict)
    """Additional metadata."""

    def __call__(self, *args, **kw):
        """Calls the associated function with the provided arguments."""
        return self.function(*args, **kw)

    def __str__(self):
        """Returns the name of the command or the function's name."""
        return self.name if self.name else self.function.__name__

    def __eq__(self, other):
        if not isinstance(other, BasicCommand):
            raise TypeError(f"object of type '{type(other).__name__}' is not supported")
        return self.function == other.function

    def __hash__(self):
        return hash(self.function)

    def __repr__(self):
        return (
            f"{type(self).__name__}({self.function.__name__}"
            f"{':'+self.description if self.description else ''})"
        )


class BasicCommands:
    """
    A command manager
    """

    commands: dict[str, BasicCommand]
    """A dictionary mapping command names to their corresponding BasicCommand objects."""

    default_command_object = BasicCommand
    """the default class to wrap functions"""

    def get_name_or_callable_name(self, name: Callable | str):
        """either get the name of a callable or just return the name if it's a string

        Parameters
        ----------
            name: Callable | str
                callable or str

        Raises
        ------
            ValueError
                excepted str/callable but got type(s) instead

        Returns
        -------
            str
                the name of the callable or str
        """
        if (not callable(name)) and (not isinstance(name, str)):
            raise ValueError(
                f"excepted str/callable but got {type(name).__name__!r} instead"
            )
        if callable(name):
            name = name.__name__
        return name

    def __init__(self):
        self.commands = {}

    def add_command(
        self, function: Callable, name: str = None, description: str = None, **kw
    ) -> BasicCommand:
        """add a new command

        Parameters
        ----------
            function: Callable
                The function or coroutine representing the command.
            name: str (default: None)
                The name of the command. Defaults to the function's name if not provided.
            description: str (default: None)
                A short description of the command.

        Returns
        -------
            BasicCommand
                object representing the added command.
        """
        name = name if name is not None else function.__name__
        command_object = (
            self.default_command_object(
                function, description, name, kw.get("extra", {})
            )
            if not isinstance(function, BasicCommand)
            else function
        )
        for ali in kw.get("aliases", [name]):
            self.commands[ali] = command_object
        return command_object

    def remove_command(self, name: Callable | str):
        """remove a command"""
        name = self.get_name_or_callable_name(name)
        if name in self.commands:
            del self.commands[name]
        return

    def command_exist(self, name: str):
        """name(s) in commands"""
        return name in self.commands

    def get_command(self, name: Callable | str):
        """get command function raise CommandNotFoundError if command not in self.commands"""
        if self.command_exist(name):
            return self.commands[self.get_name_or_callable_name(name)]
        else:
            raise CommandNotFoundError(f"command {name!r} do not exists", name)

    def call_command(self, name: Callable | str, *args, **kw):
        """call command(s)"""
        return self.get_command(name)(*args, **kw)

    def command(self, *args, **kw):
        """a wrapper of self.add_command as a decorator"""

        def inner(function) -> BasicCommand:
            return self.add_command(function, *args, **kw)

        return inner

    def __call__(self, name: Callable | str, *args, **kw):
        """call command(s)"""
        return self.call_command(name, *args, **kw)

    def __repr__(self):
        return f"{type(self).__name__}({list(self.commands.keys())})"


class Command(BasicCommand):
    """
    Represents a command.
    """

    def parse_annotation(self, args, kwargs):
        """wrapper of parse_annotation"""
        return parse_annotation(self.function, args, kwargs)

    def _parse(self, *_args, **_kw):
        try:
            args, kw = self.parse_annotation(_args, _kw)
        except Exception as error:
            raise BadArgument("bad argument", (_args, _kw), self) from error
        return args, kw

    def __call__(self, *_args, **_kw):
        """Calls the associated function with the provided arguments."""
        args, kw = self._parse(*_args, **_kw)
        return self.function(*args, **kw)


class Commands(BasicCommands):
    """
    An advanced command manager, inherits from BasicCommands
    """

    commands: dict[str, Command]
    """A dictionary mapping command names to their corresponding Command objects."""

    default_command_object = Command
    """the default class to wrap functions"""


class Commander(Commands, CommandParser):
    """
    A class to manage commands, inherits from Commands, CommandParser

    Parameters
    ----------
        prefix: str
            the prefix that command strings must start with.
    """

    def __init__(self, prefix: str):
        super().__init__()
        self.prefix = prefix

    def process_command(self, string: str):
        """processing string to a command

        Parameters
        ----------
            string: str
                the string to process

        Returns
        -------
            Any
                whatever command(s) returns
        """
        name, *args = self.parse(string)
        command = self.get_command(name)
        return command(*args)


class CommandLine(Commander):
    """
    A class that simluates argv parsing, inherits from Commander.
    check :func:`parser.parse_to_argv` for more info.
    """

    def __init__(self):
        super(Commands, self).__init__()
        super(CommandParser, self).__init__()

    parse = staticmethod(parse_to_argv)
