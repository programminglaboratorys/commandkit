from .parser import eval_args


class CommandError(Exception):
	""" basic CommandError exception """

class InvaildCommandError(CommandError):
	""" when entered a command doesn't start with prefix(s) or command is empty/ """

class PrefixError(Exception):
	""" raise when str doesn't starts with prefix(s) """

class CommandString(str):
	def get_word(self) -> str: # take whatever is the first word
		return str(self).split()[0]
	def skip_prefix(self,prefix:str):
		""" skip prefix(s) if string doesn't starts with prefix(s) raise PrefixError() 
		if self equal prefix returns an empty string("") else remove the prefix
		"""
		if " " in prefix:
			raise PrefixError("prefix should not contain spaces")
		if not self.startswith(prefix):
			raise PrefixError(f"the {repr(self)} doesn't start with prefix({repr(prefix)})")
		return self.removeprefix(prefix)
	def __add__(self,other):
		return CommandString(str(self)+other)
	def __mul__(self,other):
		return CommandString(str(self)*other)
	def  __rmul__(self, value):
		return CommandString(value*str(self))
	def strip(self,*args,**kw):
		return CommandString(str(self).strip(*args,**kw))
	def lstrip(self,*args,**kw):
		return CommandString(str(self).lstrip(*args,**kw))
	def rstrip(self,*args,**kw):
		return CommandString(str(self).rstrip(*args,**kw))
	def split(self,*args,**kw) -> list:
		return [CommandString(w) for w in str(self).split(*args,**kw)]
	def __repr__(self):
		return f"{type(self).__name__}({repr(str(self))})"

class CommandParser(object):
	""" to parse and """
	@staticmethod
	def parser(string:str):
		return str.split(string)
	
	def __init_subclass__(cls, parser=None, default_command_object=None) -> None:
		print("init sub class!", cls, locals())
		cls.parser = parser or cls.parser
		cls.default_command_object = default_command_object or cls.default_command_object

	def __init__(self, prefix: str|CommandString, parser=None):
		super(CommandParser, self).__init__()
		if not isinstance(prefix,str):
			raise ValueError(f"excepted str/CommandString but got ({repr(type(prefix).__name__)}) instead")
		if " " in self.prefix:
			raise PrefixError("prefix should not contain spaces")
		self.prefix = CommandString(prefix)
		self.parser = parser if parser is not None else self.parser

	def startswith_prefix(self,string:str):
		""" check if the input string start with prefix(s) """
		return string.startswith(self.prefix)

	def process_string(self, EA:list, string:str,allow_overflow:bool=True,**kw):
		if not self.startswith_prefix(string):
			raise InvaildCommandError(f"command must start with prefix({repr(self.prefix)})")
		args = CommandString(string).strip().skip_prefix(self.prefix)
		return eval_args(EA,self.split(args),allow_overflow=allow_overflow,**kw)

	def split(self,string:str):
		return self.parser(CommandString(string).skip_prefix(self.prefix))

	def get_command_name(self,string:str):
		""" returns an empty string if string equal prefix or when there is nothing after the prefix """
		args = self.split(string)
		return args[0] if args else ""

	def get_command_args(self,string:str):
		""" returns an empty string if string equal prefix """
		args = self.split(string)[1::] # remove the command name
		return args if not args else args



