import asyncio
import unittest
from commandkit.transformers.view import StringView
from commandkit.transformers.converter import run_converters, ConversionError
from commandkit import EventManager
from typing import Union, Literal

class TestStringView(unittest.TestCase):
	def test_basic_tokenization(self):
		view = StringView("hello world")
		self.assertEqual(view.get_quoted_word(), "hello")
		view.skip_ws()
		self.assertEqual(view.get_quoted_word(), "world")

	def test_quoted_tokens(self):
		view = StringView('"hello world" "test"')
		self.assertEqual(view.get_quoted_word(), "hello world")
		view.skip_ws()
		self.assertEqual(view.get_quoted_word(), "test")

	def test_read_rest(self):
		view = StringView("cmd arg1 arg2 arg3")
		view.get_quoted_word() # skip cmd
		view.skip_ws()
		self.assertEqual(view.read_rest().strip(), "arg1 arg2 arg3")

	def test_eof(self):
		view = StringView("one")
		view.get_quoted_word()
		self.assertTrue(view.eof)

class TestConverters(unittest.TestCase):
	def test_basic_converters(self):
		self.assertEqual(run_converters(int, "123"), 123)
		self.assertEqual(run_converters(float, "1.5"), 1.5)
		self.assertEqual(run_converters(bool, "yes"), True)
		self.assertEqual(run_converters(bool, "no"), False)

	def test_union_converter(self):
		conv = Union[int, str]
		self.assertEqual(run_converters(conv, "123"), 123)
		self.assertEqual(run_converters(conv, "abc"), "abc")

	def test_literal_converter(self):
		conv = Literal["a", "b"]
		self.assertEqual(run_converters(conv, "a"), "a")
		with self.assertRaises(ConversionError):
			run_converters(conv, "c")

class TestEventManager(unittest.IsolatedAsyncioTestCase):
	async def test_event_dispatch(self):
		em = EventManager()
		called = []

		@em.event
		def on_test_sync(arg):
			called.append(arg)

		@em.event
		async def on_test_async(arg):
			await asyncio.sleep(0.01)
			called.append(arg)

		await em.dispatch("test_sync", "sync_data")
		await em.dispatch("test_async", "async_data")
		
		self.assertIn("sync_data", called)
		self.assertIn("async_data", called)

if __name__ == "__main__":
	unittest.main()
