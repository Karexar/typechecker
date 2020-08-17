# Python type-checker

The *typecheck* module provides a nice way to check for parameter and return value types at runtime using decorators. One benefit is that we do not need to test for types in test functions anymore, because the decorators already handle this.

## Usage

```python
from typecheck import *

# use accepts and returns decorator as described in the examples...
```

## Examples

Here are some examples of how to use the decorators. In a python interpreter, run:
```python
from example import *
```
and try calling the foo functions with different parameters

### Example 1

Type check on argument

```python
@accepts(int)
def foo1(arg):
    return "ok"
```
```zsh
>>> foo1(1)
'ok'
>>> foo(0.5)
TypeError: Type error on parameter 0 of method 'foo1' :
              Expected :  int
              Have :      float
```

### Example 2

Type check on return value

```python
@returns(int)
def foo2(arg):
    return arg
```
```zsh
>>> foo2(1)
1
>>> foo2(0.5)
TypeError: Type error on return value of method 'foo2' :
            Expected :  int
            Have :      float
```
### Example 3

Combining accepts and returns. This will raise a TypeError if we don't give a list of int as parameter

```python
@accepts(list)
@returns(int)
def foo3(arg):
    return arg[0]
```
```zsh
>>> foo3([1,2])
1
>>> foo3([0.5, 1.5])
TypeError: Type error on return value of method 'foo3' :
            Expected :  int
            Have :      float
```

### Example 4
Complex type architecture. Not giving the exact architecture will raise a TypeError.
```python
@accepts(int, Tuple[Dict[str, List[int]], Set[float]])
def foo4(arg1, arg2):
    return "ok"
```
```zsh
>>> foo4(1, ({"a":[1,2]}, {0.5, 1.5}) )
'ok'
>>> foo4(1, ({"a":[1.5,2.5]}, {0.5, 1.5}) )
TypeError: Type error on parameter 1 of method 'foo4' :
            Expected :  tuple[dict[str, list[int]], set[...]]
            Have :      tuple[dict[str, list[float]], set[...]]
```

### Example 5
Giving something else than None will raise a TypeError
```python
@returns(None)
def foo5(arg):
    return arg
```
```zsh
>>> foo5(None)
>>> foo5(1)
TypeError: Type error on return value of method 'foo5' :
            Expected : NoneType
            Have     : int
```

### Example 6

Multiple return values are supported

```python
@returns(Tuple[str, str])
def foo6(arg):
    return arg
```
```zsh
>>> foo6(("a", "b"))
('a', 'b')
>>> foo6(("a", 1))
TypeError: Type error on return value of method 'foo6' :
             Expected :  tuple[str, str]
             Have :      tuple[str, int]
```

### Example 7
Passing a class as an expected type is supported
```python
from toy_class.py :
class Foo:
    def __init__(self):
        pass

@accepts(Foo)
def foo7(arg):
    return "ok"
```
```zsh
>>> foo = Foo()
>>> foo7(foo)
'ok'
>>> foo7(1)
TypeError: Type error on parameter 0 of method 'foo7' :
            Expected :  Foo
            Have :      int
```

### Example 8

Passing Any will allow any type for the parameter, this is particularly useful when decorating method, since we cannot expect the type of the class for the first parameter (self), since the class is not defined at this point.

```python
class Bar:
    def __init__(self):
        pass

    @accepts(Any, int)
    def foo(arg):
        return "ok"
```

```zsh
>>> bar = Bar()
>>> bar.foo(1)
'ok'
>>> bar.foo(0.5)
TypeError: Type error on parameter 1 of method 'foo' :
             Expected :  int
             Have :      float
```

### Example 9

Unions are supported, which is useful when argument can be int or None for example.

```python
@accepts(Union[int, list])
def foo9(arg):
    return "ok"
```
```zsh
>>> foo9(1)
'ok'
>>> foo9([1])
'ok'
>>> foo9(1.5)
TypeError: Type error on parameter 0 of method 'foo9' :
            Expected :  union[int, list]
            Have :      union[float]
```

### Example 10

Keyword arguments are supported. We need to specify the argument names and the types, in case the kwargs are given in random order.

```python
@accepts(int, x=int, y=int)
def foo10(arg, x=1, y=1):
    return "ok"
```
```zsh
>>> foo10(1, y=1)
'ok'
>>> foo10(1, y=1, x=1)
'ok'
>>> foo10(1, y=1, x=1.5)
TypeError: Type error on parameter 'x' of method 'foo10' :
             Expected :  int
             Have :      float
```
