from ._parser import parse_to_argv
from itertools import zip_longest
import shlex

string_to_commandline = lambda string: shlex.split(string)

class EAError(Exception):
	""" basic exception for Eval args """
		
class EAOverflowError(OverflowError):
	""" when Eval_Args have more args to handle than what it can handle """
	def __init__(self,message,*,lenght,but,data={}):
		super(EAOverflowError,self).__init__(message)
		self.lenght = lenght
		self.but = but
		self.data = data
class MissingError(EAError):
	""" when argument is missing and Missing_okay is true """
	def __init__(self,message,*,names=[],data={}):
		super(MissingError,self).__init__(message)
		self.names = names
		self.data = data

class Missing(object):
	def __repr__(self):
		return "Missing"
Missing = Missing()

def split_string(string:str):
	""" split string """
	return string.split()

def eval_args(EA:list, args:list, allow_overflow:bool=False,Missing_okay:bool=True,fillvalue:any=Missing):
	"""
	eval_args(["whatup","hmm","*","hehe"],"good ye? more stuff :)".split()) -> \
	({'whatup': 'good', 'hmm': 'ye?', 'hehe': ['more', 'stuff', ':)']}, [])
	"""
	# tuple(zip(*enumerate(EA))) -> ((0, 1, 2, 3), ('whatup', 'hmm', '*', 'hehe'))
	# zip(*tuple(zip(*enumerate(EA))),args) -> [(0, 'whatup', 'good'), (1, 'hmm', 'ye?'), (2, '*', 'more'), (3, 'hehe', 'stuff')]
	# dict(list(zip(EA,args))) -> {'whatup': 'good', 'hmm': 'ye?', 'hehe': 'stuff'}
	star = False
	variables = {}
	args_copy = args.copy()
	for index,argname,item in zip_longest(*zip(*enumerate(EA)),args,fillvalue=fillvalue):
		if argname is fillvalue:
			break
		elif star:
			li = args[len(variables)::]
			variables[argname] = li
			for _ in range(len(args_copy)):
				del args_copy[0]
			break
		if argname == "*":
			star = True
			if index == len(EA)-1:
				raise ValueError("excepted arg name after '*'")
			continue
		else:
			variables[argname] = item
			if item is not fillvalue:
				del args_copy[0]
	data = {"args":args_copy,"variables":variables}
	if Missing_okay is not None and Missing_okay is True and fillvalue in list(variables.values()):
		names = [repr(key) for key,value in variables.items() if value is fillvalue]
		raise  MissingError(f"missing {len(names)} required {'arguments' if len(names) > 1 else 'argument'}: {', '.join(names)}",names = names,data=data)
	if args_copy and not allow_overflow:
		lenght = len(args)-1 if "*" not in args else len(args)-2
		but = lenght+len(args_copy)
		raise EAOverflowError(f"takes {lenght} argument but {but} were given",lenght=lenght,but=but,data=data)
	return variables,args_copy

def parse_EA_default(defaults,variables):
	defaults = defaults.copy()
	defaults.update(variables)
	return defaults


def parse_annotation(f,*_args,**_kw):
	from inspect import _POSITIONAL_ONLY,\
				_POSITIONAL_OR_KEYWORD,_KEYWORD_ONLY,signature
	sign = signature(f)
	params = sign.parameters.values()
	if not list(params): # if params is empty
		return _args,_kw
	args = []
	kw = {}
	kw.update(_kw)
	for index,param in enumerate(params):
		try:
			item = _args[index]
		except IndexError:
			if param.kind in [_KEYWORD_ONLY,_POSITIONAL_OR_KEYWORD] and param.name in _kw:
				if param.annotation is not param.empty:
					kw[param.name] = param.annotation(_kw[param.name])
				else:
					kw[param.name] = _kw[param.name]
			continue
		if param.kind in [_POSITIONAL_ONLY,_POSITIONAL_OR_KEYWORD]:
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
		if param.kind in [_KEYWORD_ONLY,_POSITIONAL_OR_KEYWORD] and param.name in _kw:
			if param.annotation is not param.empty:
				kw[param.name] = param.annotation(_kw[param.name])
			else:
				kw[param.name] = _kw[param.name]
	return args,kw
