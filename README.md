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

need help? or have bugs to report, let me know in [here](https://discord.gg/vzEZnC7CM8)

## simple example

```python
from commandkit import CommandLine
cmder = CommandLine()

@cmder.command(name="foo")
def foo(cmd, num):
  # do stuff with the cmd and num
  ...

@cmder.command(description="Calculate f(num) = num * 5")
def bar(num: int):
  return num*5

cmder.process_command("foo kick 10")
print(cmder.process_command("bar 10")) # output: 50
```

# Documentation

you can check commandkit docs [here](https://commandkit.readthedocs.io/en/latest/)
