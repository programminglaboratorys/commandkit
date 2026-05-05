"""
This module contains a class responsible for managing event listeners and dispatching events.
"""

import asyncio
import inspect
from typing import Callable


class EventManager:
	"""responsible for managing event listeners and dispatching events.

	Parameters
	----------
		events: dict[str, list[Callable]]
	"""

	def __init__(self, events: dict[str, list[Callable]] = None):
		self.extra_events: dict[str, list[Callable]] = events or {}

	async def dispatch(self, event_name: str, /, *args, **kwargs):
		"""dispatch an event

		Parameters
		----------
			event_name: str
				the name of the event
			*args:
				the arguments of the event
			**kwargs:
				the keyword arguments of the event
		"""
		# bleh in C++ version, make sure to just remove on_ when being added to extra_events (add_listen or just have the function name be OnEvent(name, handler))
		ev = "on_" + event_name
		tasks = []
		for event in self.extra_events.get(ev, []):
			tasks.append(self.schedule_event(event, ev, *args, **kwargs))
		if tasks:
			await asyncio.gather(*tasks)

	async def schedule_event(self, event: Callable, ev: str, /, *args, **kwargs):
		"""handles firing the event

		Parameters
		----------
			event: Callable
				the event to fire
			ev: str
				the event name
			*args:
				the arguments of the event
			**kwargs:
				the keyword arguments of the event
		"""
		if inspect.iscoroutinefunction(event):
			res = await event(*args, **kwargs)
		else:
			res = event(*args, **kwargs)
		return res, ev

	def add_listen(self, func: Callable, name: str = None):
		"""adds a new event listener

		Parameters
		----------
			func: Callable
				the listener
			name: str (default: None)
				the name of the listener. (uses the listeners name if None).
		"""
		name = name or func.__name__

		if name in self.extra_events:
			self.extra_events[name].append(func)
		else:
			self.extra_events[name] = [func]
		return func

	def remove_listen(self, func: Callable, name: str = None):
		"""removes an event listener

		Parameters
		----------
			func: Callable
				the listener
			name: str (default: None)
				the name of the listener. (uses the listeners name if None).
		"""
		name = name or func.__name__

		if name in self.extra_events:
			try:
				self.extra_events[name].remove(func)
			except ValueError:
				pass
		return func

	def event(self, func: Callable):
		"""a decorator to add an event listener

		Parameters
		----------
			func: Callable
				the listener function
		"""
		self.add_listen(func)
		return func
