from typing import Any


class ConversionError(Exception):
	"""Raised when type conversion fails."""

	def __init__(self, message: str, argument: str, converter: Any):
		super().__init__(message)
		self.argument = argument
		self.converter = converter


class ViewError(Exception):
	"""Base class for errors in StringView."""
	pass


class ExpectedClosingQuoteError(ViewError):
	"""Raised when a closing quote is expected but not found."""
	def __init__(self, quote: str):
		super().__init__(f"Expected closing quote: {quote}")
		self.quote = quote


class UnexpectedQuoteError(ViewError):
	"""Raised when a quote is found in an unexpected place."""
	def __init__(self, quote: str):
		super().__init__(f"Unexpected quote found: {quote}")
		self.quote = quote


class InvalidEndOfQuotedStringError(ViewError):
	"""Raised when a quoted string does not end correctly."""
	def __init__(self, char: str):
		super().__init__(f"Expected space after closing quote, got {char!r}")
		self.char = char
