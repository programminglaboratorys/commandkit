""" commandkit is a package to make managing and implementing events managers, commands easier """

from .commander import Command, Commander, CommandLine
from .core import CommandError, CommandParser

__all__ = ["Command", "Commander", "CommandLine", "CommandError", "CommandParser"]


__version__ = "0.2.0"
__author__ = "programminglaboratorys"
__description__ = "simple library to implement commands, events dispatchers"
