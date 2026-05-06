# commandkit

a standalone library to bring discord.py developer experience to your python applications, focus on building your logic rather then an event manager or command manager

## Features

- **Familiar Decorator API** – Leverages the intuitive `discord.py` pattern for registering commands and events.
- **Automatic Type Conversion** – Uses Python type hints to automatically convert input strings into integers, floats, or custom objects.
- **Asynchronous by Design** – Built from the ground up for `asyncio`, allowing command and event handlers to run concurrently within your existing event loop.
- **Zero Bloat** – A focused codebase with zero dependencies.

# Installation

been tested in python 3.10

Run the following to install:

```cmd
pip install commandkit
```

### or

```cmd
python -m pip install commandkit
```

if that didn't work, try replacing `pip` with `pip3`.

need help? or have bugs to report, let me know in [here](https://github.com/programminglaboratorys/commandkit/issues)

# Quick Examples

```python
import asyncio
from commandkit import CommandLine, Greedy

cmder = CommandLine(prefix="!")

@cmder.command()
def add(a: int, b: int):
	"""Adds two numbers."""
	return a + b

@cmder.command()
async def announce(title: str, *, message: str):
	"""Capture the rest of the string as a single argument."""
	await asyncio.sleep(0.1)
	return f"[{title}] {message}"

async def main():
	# Sync command call
	res = await cmder.process_command("!add 10 20")
	print(res) # 30

	# Rest capture
	res = await cmder.process_command('!announce "System Alert" This is a test message.')
	print(res) # [System Alert] This is a test message.

if __name__ == "__main__":
	asyncio.run(main())
```

---

## Event Management

CommandKit includes a standalone `EventManager` for dispatching async events.

```python
from commandkit import EventManager
import asyncio

em = EventManager()

@em.event
async def on_message(arg):
	print(f"Event received: {arg}")

async def run_events():
	# dispatch("test") will trigger all "on_message" events
	await em.dispatch("message", "Hello World!")

asyncio.run(run_events())
```

# Documentation

you can check commandkit docs [here](https://commandkit.readthedocs.io/en/latest/)

## Contributing

We value technical contributions and bug reports.

- **Issues:** [Open a ticket](https://github.com/programminglaboratorys/commandkit/issues) for bugs or feature requests.
- **PRs:** Pull requests are welcome. Please ensure code follows PEP 8 standards.

## License

CommandKit is distributed under the [MIT License](LICENSE).
