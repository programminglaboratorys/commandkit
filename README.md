# {name}
{description}

# installation

Run the following to install:
```cmd
pip install {installation}
```
### or
```cmd
python -m pip install {installation}
```
if that didn't work, try replacing `pip` with `pip3`.

need help? or have bugs to report, let me know in [here](https://discord.gg/vzEZnC7CM8)

## simple example
```python
from UnknownName.commander import CommandLine
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
# docs

## **Soon**

