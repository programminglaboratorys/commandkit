"""
This module contains a class responsible for managing event listeners and dispatching events.
"""

from typing import Callable


class EventManager:
    """responsible for managing event listeners and dispatching events.

    Parameters
    ----------
        events: dict[str, list[Callable]]
    """

    def __init__(self, events: dict[str, list[Callable]] = None):
        self.extra_events: dict[str, list[Callable]] = events or {}

    def dispatch(self, event_name: str, /, *args, **kwargs):
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
        ev = "on_" + event_name
        for event in self.extra_events.get(ev, []):
            self.schedule_event(event, ev, *args, **kwargs)

    def schedule_event(self, event: Callable, ev: str, /, *args, **kwargs):
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
        return event(*args, **kwargs), ev

    def add_listen(self, func: Callable, name: str = None):
        """adds a new event listener

        Parameters
        ----------
            func: Callable
                the listener
            name: str (default: None)
                the name of the listener. (uses the listeners name if None).
        """
        name = func.__name__ if name is None else name
        if name in self.extra_events:
            self.extra_events[name].append(func)
        else:
            self.extra_events[name] = [func]

    def remove_listen(self, func: Callable, name: str = None):
        """removes a event listener

        Parameters
        ----------
            func: Callable
                the listener
            name: str (defaults: None)
                the name of the listener. (uses the listeners name if None)
        """
        name = func.__name__ if name is None else name
        if name in self.extra_events:
            try:
                self.extra_events[name].remove(func)
            except ValueError:
                pass

    def event(self, func: Callable):
        """adds a new event listener; used as a decorator

        Parameters
        ----------
            func: Callable
                the listener

        """
        return self.add_listen(func)
