# commandkit

easy tool to parse string to commands, easy tool to create commandlines

# installation

Run the following to install:

```cmd
pip install commandkit
```

### or

```cmd
python -m pip install commandkit
```

if that didn't work, try replacing `pip` with `pip3`.

need help? or have bugs to report, let me know in [here](https://discord.gg/vzEZnC7CM8) or open an issue

## simple example

```python
from commandkit.commander import CommandLine
cmder = CommandLine() # class

@cmder.command(name="foo") # if name is None take function name
def foo(cmd, num):
  # do stuff with the cmd and num
  ...

@cmder.command(description="Calculator f(num) = num * 5")
def bar(num:int):
  return num*5

cmder.process_command("foo kick 10")
```

# places

- [commandkit wiki](https://github.com/programminglaboratorys/commandkit/wiki)
- [pypi](https://pypi.org/project/commandkit/)
- [github](https://github.com/programminglaboratorys/commandkit)
