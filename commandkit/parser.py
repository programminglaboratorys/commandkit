from ._parser import parse_to_argv
from itertools import zip_longest
from inspect import _POSITIONAL_ONLY,\
				_POSITIONAL_OR_KEYWORD,_KEYWORD_ONLY,signature


__all__ = ["Missing","EAError","EAOverflowError","MissingError","eval_args","parse_annotation"]

Missing = type('Missing', (object,), {'__repr__': lambda s: "Missing"})() # creating a new type. thanks to: stackoverflow.com/questions/1528932/how-to-create-inline-objects-with-properties > https://stackoverflow.com/a/1528993


class EAError(Exception):
	""" basic exception for Eval args """

class EAOverflowError(OverflowError,EAError):
	""" when eval_args have more args to handle than what it can handle """
	def __init__(self,message: str,*,lenght: int, num:int ,data:dict ={}):
		super(EAOverflowError,self).__init__(message)
		self.lenght = lenght # expexcted lenght
		self.num = num
		self.data = data     # the args that has been parsed

class MissingError(EAError):
	""" when argument(s) is missing """
	def __init__(self,message: str,*, names: list =[], data: dict ={}):
		super(MissingError,self).__init__(message)
		self.names = names
		self.data = data



def eval_args(EA:list, args:list, allow_overflow:bool=False, Missing_okay:bool=True, Missing:any=Missing):
	"""
	eval_args(["whatup","hmm","*","hehe"],"good ye? more stuff :)".split()) -> \
	({'whatup': 'good', 'hmm': 'ye?', 'hehe': ['more', 'stuff', ':)']}, [])
	"""
	# tuple(zip(*enumerate(EA))) -> ((0, 1, 2, 3), ('whatup', 'hmm', '*', 'hehe'))
	# zip(*tuple(zip(*enumerate(EA))),args) -> [(0, 'whatup', 'good'), (1, 'hmm', 'ye?'), (2, '*', 'more'), (3, 'hehe', 'stuff')]
	# dict(list(zip(EA,args))) -> {'whatup': 'good', 'hmm': 'ye?', 'hehe': 'stuff'}
	star = False # truns True when reached to the keyword arguments (e.g ["*","kw"])
	variables = {}
	for index,argname,item in zip_longest(*zip(*enumerate(EA)),args.copy(),fillvalue=Missing):
		if argname is Missing: # when the argname is missing
			break
		elif star:
			li = args[len(variables)::]
			variables[argname] = li
			for _ in range(len(args)):
				del args[0]
			break
		if argname == "*":
			star = True
			print(index,len(EA)-1,sep=":")
			if   index == len(EA)-1:
				raise ValueError("excepted an argument name after '*'")
			continue
		else:
			variables[argname] = item
			if item is not Missing: # avoid index error
				del args[0]
	if (not Missing_okay) and Missing in variables.values():
		names = [repr(key) for key,value in variables.items() if value is Missing]
		raise  MissingError(f"missing {len(names)} required {'arguments' if len(names) > 1 else 'argument'}: {', '.join(names)}",names = names,d={"args":args,"variables":variables})
	if args and not allow_overflow: # there  is still args in
		lenght = (len(args)-1 if "*" not in args else len(args)-2) # expexcted lenght
		num = len(args) # the overflow 
		raise EAOverflowError(f"takes {lenght} argument but {num} were given",lenght=lenght,num=num,data={"args":args,"variables":variables})
	return variables,args # return , the overflowed arguments


def parse_annotation(f,*_args,**_kw):
	sign = signature(f)
	params = sign.parameters.values()
	if not list(params): # if params is empty
		return _args,_kw
	args = []
	kw = {} | _kw
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
