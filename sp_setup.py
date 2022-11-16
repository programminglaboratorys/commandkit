from setupfast import SetupFast,__export_file__
import datetime

classifiers = [
  'Development Status :: 5 - Production/Stable',
  "Intended Audience :: Developers",
  'Programming Language :: Python :: 3',
  'License :: OSI Approved :: MIT License'
]

__version__ = '0.1.0'
__author__  = 'programminglaboratorys'

setup = SetupFast(
  year = datetime.datetime.now().year,
  name='commandkit',
  version=__version__,
  description="",
  author=__author__,
  author_email='programming.laboratorys@gmail.com',
  classifiers=__import__("json").dumps(classifiers,indent=2),
  keywords='commandkit,command,commandline,basic,commander',
  install_requires=[]
)

setup.readme += """

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

**Soon**

"""
def ef(f,mode="w"):
  if "setup" not in f.name:
    try:
      name,type = f.name.split(".")
    except ValueError:
      name,type = f.name,""
    f.name = name.upper()+"."+type
  print("exporting",f.name,end="")
  s= __export_file__(f,mode="w")
  print(", done")

logs = {__version__:{
            "date":__import__("datetime").datetime.fromtimestamp(__import__("time").time()).strftime("%Y/%m/%d"),
            "context":["First Release"]}
            }

setup.setup(logs,"TOKEN",
	__export_file__=lambda f:ef(f,mode="w"))
from os.path import join,split
import sys
if __name__ == "__main__":
  args = sys.argv
  if len(args) < 2:
    print("error: missing argument <path>")
    exit(1)
  path = args[1]
  _,name = split(args[1])
  setup.copy(path,join(__import__("os").getcwd(),name))
  print(f"package({name}) had been copied")