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
    pass