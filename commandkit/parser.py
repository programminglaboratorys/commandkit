"""
this module contains the parsers

functions to parse strings to argv, parse annotations and eval args based on 
"""

from itertools import zip_longest
from inspect import (
    _POSITIONAL_ONLY,
    _POSITIONAL_OR_KEYWORD,
    _KEYWORD_ONLY,
    signature,
    Parameter,
)
from typing import Any, Tuple, Dict, Iterable, Callable
from ._parser import parse_to_argv


__all__ = [
    "Missing",
    "EAError",
    "EAOverflowError",
    "MissingError",
    "eval_args",
    "parse_annotation",
    "parse_to_argv",
]

# fmt: off
# pylint: disable=line-too-long
Missing = type("Missing", (object,), {"__repr__": lambda s: "Missing"})()  # creating a new type to datermize an argument is missing. thanks to: https://stackoverflow.com/a/1528993


class EAError(Exception):
    """basic exception for Eval args"""


class EAOverflowError(OverflowError, EAError):
    """when eval_args have more args to handle than what it can handle"""

    def __init__(
        self, message: str, args: list, variables: dict, expected_length: int
    ):
        super().__init__(message)
        self.expected_length = expected_length
        self.args = args
        self.variables = variables


class MissingError(EAError):
    """when argument(s) is missing"""

    def __init__(self, message: str, args: list, variables: dict, names: list):
        super().__init__(message)
        self.names = names
        self.args = args
        self.variables = variables


def eval_args(
    expected_args: list,
    args: list,
    allow_overflow: bool = False,
    missing_okay: bool = True,
    missing: Any = Missing,
) -> tuple[dict[str, str | list[str]], list[str]]:
    """A function to simulate python functions positional/var positional arguments.

    Note: it modify args argument
    
    Parameters
    ----------
        expected_args: list
            the format of the arguments
        args: list
            arguments
        allow_overflow: bool (default: False)
            whether to allow extra arguments
        missing_okay: bool (default: True)
            whether to allow missing arguments
        missing: Any (default: Missing)
            the value to use for missing arguments
    
    Raises
    ------
        ValueError
            if a star was provided but not followed by an argument name
        MissingError
            if a required argument is missing
        EAOverflowError
            if too many arguments are provided

    Returns
    -------
        tuple[dict[str, str | list[str]], list[str]]
            tuple of two elements; the arguments, the remaining arguments

    -------
	Example
    -------
    .. highlight:: python
    .. code-block:: python

	>> eval_args(["whatup","hmm","*","hehe"],"good ye? more stuff :)".split())
	({'whatup': 'good', 'hmm': 'ye?', 'hehe': ['more', 'stuff', ':)']}, [])
    """
    # tuple(zip(*enumerate(expected_args))) -> ((0, 1, 2, 3), ('whatup', 'hmm', '*', 'hehe'))
    # zip(*tuple(zip(*enumerate(expected_args))),args) -> [(0, 'whatup', 'good'), (1, 'hmm', 'ye?'), (2, '*', 'more'), (3, 'hehe', 'stuff')]
    # dict(list(zip(expected_args,args))) -> {'whatup': 'good', 'hmm': 'ye?', 'hehe': 'stuff'}
    star = False  # turns True when reached to the var arguments (e.g ["*","args"])
    variables = {}
    for index, argname, item in zip_longest(
        *zip(*enumerate(expected_args)), args.copy(), fillvalue=missing
    ):
        if argname is missing:  # when the argname is missing
            break
        if star:
            li = args[len(variables)::]
            variables[argname] = li
            for _ in range(len(args)):
                del args[0]
            break
        if argname == "*":
            star = True
            if index == len(expected_args) - 1:
                raise ValueError("excepted an argument name after '*'")
            continue
        variables[argname] = item
        if item is not missing:  # avoid index error
            del args[0]

    if (not missing_okay) and missing in variables.values():
        names = [repr(key) for key, value in variables.items() if value is missing]
        raise MissingError(
            f"missing {len(names)} required {'arguments' if len(names) > 1 else 'argument'}: {', '.join(names)}",
            args,
            variables,
            names=names,
        )

    if args and not allow_overflow:  # there  is still args in
        length = len(args) - 1 if "*" not in args else len(args) - 2  # expected length
        raise EAOverflowError(
            f"takes {length} argument but {len(args)} were given",
            args,
            variables,
            expected_length=length,
        )

    return variables, args  # return , the overflowed arguments


def parse_annotation(f: Callable, _args: Tuple[Any], _kw: Dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
    """wrapper function of _parse_annotation
    
    Parameters
    ----------
    	f: function
    		the function to parse its argument
    	_args: Tuple[Any]
    		the arguments to parse
    	_kw: Dict[str, Any]
    		the keyword arguments to parse
    
    Returns
    -------
        tuple[list[Any], dict[str, Any]]
            The list of parsed positional arguments, The dictionary of parsed keyword arguments.
    """
    sign = signature(f)
    params = sign.parameters.values()
    return _parse_annotation(params, _args, _kw)


def _parse_annotation(params: Iterable[Parameter], _args: Tuple[Any], _kw: Dict[str, Any]):
    """
    Parses the given arguments and keyword arguments according to the callable annotations.

    Parameters
    ----------
    params : Iterable[Parameter]
        The callable parameters to parse against.
    _args : Tuple[Any]
        The positional arguments to parse.
    _kw : Dict[str, Any]
        The keyword arguments to parse.

    Returns
    -------
    list[Any]
        The list of parsed positional arguments.
    Dict[str, Any]
        The dictionary of parsed keyword arguments.
    """

    args = []
    kw = _kw.copy()
    for index, param in enumerate(params):
        try:
            item = _args[index]
        except IndexError:
            if (
                param.kind in [_KEYWORD_ONLY, _POSITIONAL_OR_KEYWORD]
                and param.name in _kw
            ):
                if param.annotation is not param.empty:
                    kw[param.name] = param.annotation(_kw[param.name])
                else:
                    kw[param.name] = _kw[param.name]
            continue
        if param.kind in [_POSITIONAL_ONLY, _POSITIONAL_OR_KEYWORD]:
            if param.annotation is not param.empty:
                args.append(param.annotation(item))
            else:
                args.append(item)
        elif param.kind is param.VAR_POSITIONAL:
            for item in _args[index::]:
                if param.annotation is not param.empty:
                    args.append(param.annotation(item))
                else:
                    args.append(item)
            break
    return args, kw
