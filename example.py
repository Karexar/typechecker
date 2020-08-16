from typecheck import *

class Foo:
    def __init__(self):
        pass

class Bar:
    def __init__(self):
        pass
    @accepts(Any, int)
    def foo(self, arg):
        return "ok"

# Example 1
@accepts(int)
def foo1(arg):
    return "ok"

# Example 2
@returns(int)
def foo2(arg):
    return arg

# Example 3
@accepts(list)
@returns(int)
def foo3(arg):
    return arg[0]

# Example 4
@accepts(int, Tuple[Dict[str, List[int]], Set[float]])
def foo4(arg1, arg2):
    return "ok"

# Example 5
@returns(None)
def foo5(arg):
    return arg

# Example 6
@returns(Tuple[str, str])
def foo6(arg):
    return arg

# Example 7
@accepts(Foo)
def foo7(arg):
    return "ok"

# Example 9
@accepts(Union[int, list])
def foo9(arg):
    return "ok"
