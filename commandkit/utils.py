from .parser import parse_annotation
from .core   import InvaildCommandError, CommandError

from typing  import Callable, Union

class BadArgument(CommandError):
	""" when a parsing error on an argument to pass into a command """
	def __init__(self, message, parameters, command_object):
		super(BadArgument, self).__init__(message)
		self.parameters     = parameters
		self.command_object = command_object

class CommandNotFoundError(CommandError):
	""" when command doesn't exist """
	def __init__(self, message, name):
		super(CommandNotFoundError, self).__init__(message)
		self.name = name


class BasicCommand(object):
	def __init__(self, function, description=None, name=None, **data):
		super(BasicCommand, self).__init__()
		self.function    = function
		self.description = description
		self.data        = data
		self.name        = name

	@staticmethod
	def command(*args, **kw):
		def inner(func):
			return BasicCommand(func,*args,**kw)
		return inner
	def __call__(self,*args,**kw):
		""" call self.function """
		return self.function(*args,**kw)
	async def __await__(self,*args,**kw):
		""" await self.function """
		return await self.function(*args,**kw)
	def __str__(self):
		""" return self.name or self.function.__name__ """
		return self.name if self.name else self.function.__name__
	def __repr__(self):
		return f"{self.__class__.__name__}({self.function.__name__}{'' if not self.description else ':'+self.description})"

class Command(BasicCommand):
	parse_annotation = lambda s,*a,**k: parse_annotation(s.function,*a,**k)
	@staticmethod
	def command(*args, **kw):
		"""  decorator for wrapping a function with a Command object. for an advance argument parsing """
		def inner(func):
			""" return command object when called """
			return Command(func,*args,**kw)
		return inner
	def _parse(self,*_args,**_kw):
		try:
			return self.parse_annotation(*_args,**_kw) # returns args, kw
		except Exception as error:
			raise BadArgument("bad argument", (_args,_kw), self) from error
	def __call__(self,*_args,**_kw):
		""" call self.function """
		args,kw = self._parse(*_args,**_kw)
		return self.function(*args,**kw)
	async def __await__(self,*_args,**_kw):
		""" await self.function """
		args,kw = self._parse(*_args,**_kw)
		return await self.function(*args,**kw)


class BasicCommands(object):
	default_command_object = BasicCommand

	@staticmethod
	def get_name_or_callable_name(name:Union[Callable, str]):
		if (not callable(name)) and (not isinstance(name,str)):
			raise ValueError(f"excepted str/function but got ({repr(type(name).__name__)}) instead")
		if callable(name):
			name = name.__name__
		return name

	def __init_subclass__(cls, default_command_object=None, **kw) -> None:
		cls.default_command_object = default_command_object or cls.default_command_object

	def __init__(self):
		self.commands  =  {}
	def add_command(self,function:Callable,name:str=None,description:str=None,data:dict={},**kw):
		""" add a new command """
		name = name if name is not None else function.__name__
		command_object = kw.get("Command",self.default_command_object)(function, description, name,**data)\
		  if not isinstance(function,BasicCommand) else function
		for ali in kw.get("aliases",[name]):
			self.commands[ali] = command_object
		return command_object
	def remove_command(self,name:Union[Callable, str]):
		""" remove a command """
		name = self.get_name_or_callable_name(name)
		if name in self.commands:
			del self.commands[name]
	def command_exists(self,name:Union[Callable, str]):
		""" check if name(s) exists as a command returns the function else returns False """
		try:
			return self.commands[self.get_name_or_callable_name(name)]
		except KeyError:
			return False
	def get_command(self,name:Union[Callable, str]):
		""" get name(s) if exists as a command returns the function else raise CommandNotFoundError"""
		try:
			return self.commands[self.get_name_or_callable_name(name)]
		except KeyError as e:
			raise CommandNotFoundError(f"command {repr(name)} do not exists", name) from e
	def call_command(self,name:Union[Callable, str],*args,**kw):
		""" call command(s) """
		return self.get_command(name)(*args,**kw)
	def command(self,*args,**kw):
		""" add a new command (function:callable, name:str, description:str, data:dict) """
		def wrapper(function):
			return self.add_command(function,*args,**kw)
		return wrapper
	def __call__(self,name:Union[Callable, str],*args,**kw):
		""" call command(s) """
		return self.call_command(name,*args,**kw)
	async def __await__(self,name:Union[Callable, str],*args,**kw):
		""" await command(s) """
		return await self.call_command(name,*args,**kw)
	def __repr__(self):
		return f"{type(self).__name__}({list(self.commands.keys())})"
	def process_command(self,string:str):
		args = self.parser(string)
		print("args", args, self.parser)
		if not args:
			raise InvaildCommandError(f"Invalid command {repr(args)}")
		command = self.get_command(args[0]) # find the function by the command name
		return command(*args[1::]) # 1:: remove the command name from the list
