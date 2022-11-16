from .parser import eval_args

class StringError(Exception):
	""" basic StringError exception """

class NoPrefixError(StringError):
	""" raise when str doesn't starts with prefix(s) """

class CommandString(str):
	def get_word(self):
		word = CommandString()
		for char in self:
			if char.isspace(): return word
			word+=char
		return word
	def skip_prefix(self,prefix):
		""" skip prefix(s) if string doesn't starts with prefix(s) raise NoPrefixError() 
		if str(self) == str(prefix) returns None
		"""
		if not self.startswith(prefix):
			raise NoPrefixError("the str doesn't start with prefix(s)")
		if str(self) == str(prefix):
			return None
		tok = CommandString()
		found_prefix = False
		for char in self:
			if tok.startswith(prefix) and not found_prefix:
				tok = CommandString()
				tok+= char
				found_prefix = True
			else:
				tok+= char
		return tok
	def __add__(self,other):
		return CommandString(str(self)+other)
	def __mul__(self,other):
		return CommandString(str(self)*value)
	def  __rmul__(self, value):
		return CommandString(value*str(self))
	def strip(self,*args,**kw):
		return CommandString(str(self).strip(*args,**kw))
	def lstrip(self,*args,**kw):
		return CommandString(str(self).lstrip(*args,**kw))
	def rstrip(self,*args,**kw):
		return CommandString(str(self).rstrip(*args,**kw))
	def split(self,*args,**kw):
		return [CommandString(w) for w in str(self).split(*args,**kw)]
	def __repr__(self):
		return f"{type(self).__name__}({repr(str(self))})"

# Base.py
class CommandError(Exception):
	""" basic CommandError exception """

class InvaildCommandError(CommandError):
	""" when entered a command doesn't start with prefix or command is None or empty """


class BaseCommand(object):
	def __init__(self, prefix: [str, CommandString]):
		super(BaseCommand, self).__init__()
		if not isinstance(prefix,(CommandString,str)):
			raise ValueError(f"excepted str/CommandString but got ({repr(type(prefix).__name__)}) instead")
		self.prefix = CommandString(prefix)
	def startswith_prefix(self,string:str):
		return str(string) \
							.startswith(self.prefix)
	def process_string(self,EA:list,string:str,allow_overflow:bool=True,**kw):
		if not self.startswith_prefix(string):
			raise InvaildCommandError(f"command must start with prefix({repr(self.prefix)})")
		args = CommandString(string).strip().skip_prefix(self.prefix)
		return eval_args(EA,args,allow_overflow=allow_overflow)
	def get_command_name(self,string:str):
		args = CommandString(string).strip().skip_prefix(self.prefix)
		if args is not None:
			args = args.split()
		return args[0] if args else None
	def get_command_args(self,string:str):
		""" return none if string == prefix """
		args = CommandString(string).strip().skip_prefix(self.prefix)
		return args.split() if args is not None else args



