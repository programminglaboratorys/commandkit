"""module containing Classes and functions to manage commands"""
import asyncio
import inspect
from typing import Any, Callable


class CommandError(Exception):
	"""basic CommandError exception"""


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


class Command:
	"""
	Represents a command.
	"""

	def __init__(
		self, callback: Callable, name: str = None, description: str = None, **kwargs
	):
		"""initialize a command

		Parameters
		----------
			callback: Callable
				the function or coroutine representing the command
			name: str (default: None)
				the name of the command
			description: str (default: None)
				a short description of the command
		"""
		self.callback = callback
		self.name = name or callback.__name__
		self.description = description or inspect.getdoc(callback)
		self.aliases = kwargs.get("aliases", [])
		self.extras = kwargs.get("extras", {})

	async def invoke(self, *args, **kwargs) -> Any:
		"""call the command function

		Parameters
		----------
			args: tuple
				positional arguments
			kwargs: dict
				keyword arguments

		Returns
		-------
			Any
				whatever the command returns
		"""
		if inspect.iscoroutinefunction(self.callback):
			return await self.callback(*args, **kwargs)
		return self.callback(*args, **kwargs)


