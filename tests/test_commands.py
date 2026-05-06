import asyncio
import unittest
from commandkit import CommandLine, BadArgument, CommandNotFoundError, Greedy
from typing import Union, Optional, Literal

class TestCommands(unittest.IsolatedAsyncioTestCase):
	async def asyncSetUp(self):
		self.cmder = CommandLine()

	async def test_basic_command(self):
		@self.cmder.command()
		def ping():
			return "pong"
		
		res = await self.cmder.process_command("ping")
		self.assertEqual(res, "pong")

	async def test_sync_args(self):
		@self.cmder.command()
		def add(a: int, b: int):
			return a + b
		
		res = await self.cmder.process_command("add 10 20")
		self.assertEqual(res, 30)

	async def test_async_command(self):
		@self.cmder.command()
		async def slow_add(a: int, b: int):
			await asyncio.sleep(0.01)
			return a + b
		
		res = await self.cmder.process_command("slow_add 5 5")
		self.assertEqual(res, 10)

	async def test_greedy_args(self):
		@self.cmder.command()
		def sum_all(nums: Greedy[int]):
			return sum(nums)
		
		res = await self.cmder.process_command("sum_all 1 2 3 4 5")
		self.assertEqual(res, 15)

	async def test_keyword_only_rest(self):
		@self.cmder.command()
		def say(prefix: str, *, message: str):
			return f"{prefix}: {message}"
		
		res = await self.cmder.process_command("say System hello world this is a test")
		self.assertEqual(res, "System: hello world this is a test")

	async def test_union_types(self):
		@self.cmder.command()
		def check(val: Union[int, str]):
			return type(val).__name__
		
		self.assertEqual(await self.cmder.process_command("check 123"), "int")
		self.assertEqual(await self.cmder.process_command("check abc"), "str")

	async def test_optional_args(self):
		@self.cmder.command()
		def greet(name: Optional[str] = "Guest"):
			return f"Hello {name}"
		
		self.assertEqual(await self.cmder.process_command("greet Bob"), "Hello Bob")
		self.assertEqual(await self.cmder.process_command("greet"), "Hello Guest")

	async def test_literal_args(self):
		@self.cmder.command()
		def move(direction: Literal["up", "down"]):
			return direction
		
		self.assertEqual(await self.cmder.process_command("move up"), "up")
		with self.assertRaises(BadArgument):
			await self.cmder.process_command("move left")

	async def test_errors(self):
		with self.assertRaises(CommandNotFoundError):
			await self.cmder.process_command("nonexistent")
		
		@self.cmder.command()
		def must_be_int(a: int):
			return a
		
		with self.assertRaises(BadArgument):
			await self.cmder.process_command("must_be_int abc")

if __name__ == "__main__":
	unittest.main()
