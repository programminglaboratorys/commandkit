"""
Type conversion system for commandkit.

Converts string arguments to typed values based on annotations.
Handles Union, Optional, custom converters, and callable fallback.
"""

from typing import Callable
from typing import Any, Dict, Union, Literal, get_args, get_origin

from .error import ConversionError

class Converter:
    """Base class for custom converters.

    Example
    -------
    .. code-block:: python

        class HexColor(Converter):
            def convert(self, argument: str) -> int:
                return int(argument.lstrip('#'), 16)
    """

    def convert(self, argument: str) -> Any:
        raise NotImplementedError


class Greedy:
    """Marker class for greedy argument parsing.
    
    Example: Greedy[int] consumes all successful int conversions.
    """
    def __init__(self, converter: Any):
        self.converter = converter

    def __class_getitem__(cls, item: Any):
        return cls(item)


_BOOL_TRUTHY = frozenset(('yes', 'y', 'true', 't', '1', 'enable', 'on'))
_BOOL_FALSY = frozenset(('no', 'n', 'false', 'f', '0', 'disable', 'off'))


def _convert_bool(argument: str) -> bool:
    lowered = argument.lower()
    if lowered in _BOOL_TRUTHY:
        return True
    if lowered in _BOOL_FALSY:
        return False
    raise ConversionError(
        f'could not convert "{argument}" to bool', argument, bool
    )


CONVERTER_MAPPING: Dict[type, Union[Callable, Converter]] = {
    bool: _convert_bool,
}


def register_converter(type_: type, converter: Any) -> None:
    """Register a custom converter (callable or Converter instance)."""
    CONVERTER_MAPPING[type_] = converter


def unregister_converter(type_: type) -> None:
    """Remove a registered converter."""
    CONVERTER_MAPPING.pop(type_, None)


def _do_convert(converter: Any, argument: str) -> Any:
    """Dispatch single conversion. Mapping → Converter instance → callable."""

    if converter in CONVERTER_MAPPING:
        conv = CONVERTER_MAPPING[converter]
        if isinstance(conv, Converter):
            return conv.convert(argument)
        return conv(argument)

    if isinstance(converter, Converter):
        return converter.convert(argument)

    if isinstance(converter, type) and issubclass(converter, Converter):
        return converter().convert(argument)

    if callable(converter):
        try:
            return converter(argument)
        except Exception as e:
            raise ConversionError(
                f'{getattr(converter, "__name__", converter)} '
                f'failed on "{argument}"',
                argument,
                converter,
            ) from e

    raise ConversionError(
        f'no converter for {converter}', argument, converter
    )


def run_converters(converter: Any, argument: str) -> Any:
    """Convert argument using annotation. Unwraps Union/Optional first.

    Parameters
    ----------
    converter : Any
        Type annotation or Converter instance.
    argument : str
        Raw string to convert.

    Raises
    ------
    ConversionError
        If all conversion attempts fail.
    """

    origin = get_origin(converter)
    if origin is Literal:
        values = get_args(converter)
        for val in values:
            try:
                if type(val)(argument) == val:
                    return val
            except (ValueError, TypeError):
                continue
        raise ConversionError(
            f'"{argument}" not in allowed values: {values}', argument, converter
        )

    if origin is Union:
        args = get_args(converter)
        errors = []

        for conv in args:
            if conv is type(None):
                continue
            try:
                return run_converters(conv, argument)
            except (ConversionError, ValueError, TypeError) as e:
                errors.append(e)

        if type(None) in args:
            return None

        if errors:
            raise errors[-1]

        raise ConversionError(
            f'all converters in Union failed for "{argument}"',
            argument,
            converter,
        )

    return _do_convert(converter, argument)
