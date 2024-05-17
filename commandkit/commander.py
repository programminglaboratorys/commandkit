from .core   import CommandParser, CommandString
from .parser import parse_to_argv
from .utils  import BasicCommands


class Commander(BasicCommands,CommandParser):
	parser = lambda self,sub: CommandString(sub).skip_prefix(self.prefix).split(" ")
	def __init__(self, prefix:str, parser=None):
		super(Commander,self).__init__()
		self.prefix = CommandString(prefix)
		self.parser = parser or self.parser

class CommandLine(BasicCommands):
	""" works like Commander but by default parses string to argv and without any prefixs """
	parser = parse_to_argv
	def __init__(self, parser=None):
		super(CommandLine,self).__init__()
		self.parser = parser or self.parser

"""
examples of 
>>> cmds = CommandLine()
>>> @cmds.command()
... def hello(name):
...     print("Hello,",name)
>>> cmds('hello',"World!") # or cmds('hello',name="World!")
Hello, World!
"""

"""
>>> cmds = Commander(prefix="?")
>>> @cmds.command()
... def hello(name):
...     print("Hello,",name)
...
>>> cmds.process_command('?hello World!')
Hello, World!
"""