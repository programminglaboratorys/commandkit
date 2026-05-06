""" commandkit is a package to make managing and implementing events managers, commands easier """

from .commander import CommandManager
from .core import Command, CommandError, BadArgument, CommandNotFoundError
from .EventManager import EventManager
from .parsers.converter import Greedy

__all__ = [
	"Command",
	"CommandManager",
	"CommandError",
    "EventManager",
	"BadArgument",
	"CommandNotFoundError",
	"Greedy",
]


__version__ = "0.3.1"
__author__ = "programminglaboratorys"
__description__ = "simple library to implement commands, events dispatchers"
