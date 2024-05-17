from commandkit import *

cmds = Commander(prefix="?")

@cmds.command()
def hello(name):
    print("Hello,",name)

@cmds.command(name="exit")
def exit_(code:int=0):
    exit(code)

cmds.process_command('?hello World!')

while True:
    cmds.process_command(input("> "))

exit()
from commandkit.core      import *
from commandkit.eventer   import *
from commandkit.parser    import *
from commandkit._parser   import *
from commandkit.commander import *
from commandkit           import *
import commandkit
"""
__version__ = "0.2.0"
__author__  = "__iamme__"
"""
print(f"commandkit {commandkit.__version__} by {commandkit.__author__}")
print(f"commandkit is under the MIT license")
from commandkit.utils import CommandNotFoundError
commandline = CommandLine()
@commandline.command(name="hi")
def hello(i:int):
	[print("Hello!") for _ in range(i)]

@commandline.command(name="exit")
def exit_(code:int=0):
	exit(code)

#commandline.process_command("hi 1")#input("command: "))
import os
import traceback
while 1:
	cmd = input("(commandkit) "+os.getcwd()+"> ")
	try:
		commandline.process_command(cmd)
	except TypeError as e:
		print(e)
		#print(dir(e))
		['__cause__', '__class__', '__context__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', '__suppress_context__', '__traceback__', 'args', 'with_traceback']
		traceback.print_exc()
	except (CommandNotFoundError) as e:
		os.system(cmd)



