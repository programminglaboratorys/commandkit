"""module contains classes to manage and dispatch commands"""
from typing import Dict
from typing import Optional
import inspect
from typing import Any, Callable

from .core import Command, CommandNotFoundError, BadArgument
from .transformers.view import StringView
from .transformers.converter import run_converters, Greedy


class CommandManager:
	"""
	A class to manage and dispatch commands.
	"""

	def __init__(self, prefix: str = ""):
		"""initialize the commander

		Parameters
		----------
			prefix: str (default: "")
				the prefix that command strings must start with
		"""
		self.prefix = prefix
		self.commands: Dict[str, Command] = {}

	def add_command(self, command: Command):
		"""add a new command

		Parameters
		----------
			command: Command
				the command object to add
		"""
		self.commands[command.name] = command
		for alias in command.aliases:
			self.commands[alias] = command

	def get_command(self, name: str) -> Optional[Command]:
		"""get command by name or alias

		Parameters
		----------
			name: str
				the name or alias of the command

		Returns
		-------
			Optional[Command]
				the command object if found
		"""
		return self.commands.get(name)

	def command(self, name: str = None, description: str = None, **kwargs):
		"""a decorator to register a command

		Parameters
		----------
			name: str (default: None)
				the name of the command
			description: str (default: None)
				a short description of the command
		"""
		def decorator(callback: Callable) -> Command:
			cmd = Command(callback, name=name, description=description, **kwargs)
			self.add_command(cmd)
			return cmd
		return decorator

	async def invoke(self, command: Command, view: StringView) -> Any:
		"""invokes a command by parsing arguments from a StringView

		Parameters
		----------
			command: Command
				the command to invoke
			view: StringView
				the view containing raw arguments
		"""
		signature = inspect.signature(command.callback)
		args = []
		kwargs = {}

		for param in signature.parameters.values():
			view.skip_ws()
			if isinstance(param.annotation, Greedy):
				greedy = param.annotation
				values = []
				while not view.eof:
					view.skip_ws()
					prev_index = view.index
					arg_str = view.get_quoted_word()
					if arg_str is None:
						break
					
					try:
						value = run_converters(greedy.converter, arg_str)
						values.append(value)
					except Exception:
						view.index = prev_index
						break
				
				if not values and param.default is inspect.Parameter.empty:
					raise BadArgument(f"Missing greedy argument: {param.name}", param.name, command)
				
				value = values
			else:
				if view.eof:
					if param.default is inspect.Parameter.empty:
						raise BadArgument(f"Missing argument: {param.name}", param.name, command)
					continue

				if param.kind == inspect.Parameter.KEYWORD_ONLY:
					arg_str = view.read_rest().strip()
				else:
					arg_str = view.get_quoted_word()
				
				if arg_str is None or (param.kind == inspect.Parameter.KEYWORD_ONLY and not arg_str):
					if param.default is inspect.Parameter.empty:
						raise BadArgument(f"Missing argument: {param.name}", param.name, command)
					continue

				if param.annotation is not inspect.Parameter.empty:
					try:
						value = run_converters(param.annotation, arg_str)
					except Exception as e:
						raise BadArgument(str(e), param.name, command) from e
				else:
					value = arg_str

			if param.kind == inspect.Parameter.KEYWORD_ONLY:
				kwargs[param.name] = value
			else:
				args.append(value)

		return await command.invoke(*args, **kwargs)

	async def process_command(self, string: str) -> Any:
		"""processes a raw string to find and execute a command

		Parameters
		----------
			string: str
				the raw command string to process
		"""
		view = StringView(string)
		if self.prefix:
			if not view.skip_string(self.prefix):
				return None

		view.skip_ws()
		cmd_name = view.get_quoted_word()
		if not cmd_name:
			return None

		command = self.get_command(cmd_name)
		if not command:
			raise CommandNotFoundError(f"Command '{cmd_name}' not found", cmd_name)

		return await self.invoke(command, view)


class CommandLine(CommandManager):
	"""
	A commander variant specialized for command-line style parsing.
	"""

	def __init__(self):
		"""initialize the command line interface"""
		super().__init__(prefix="")
