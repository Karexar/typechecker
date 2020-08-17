from typecheck import *
import pytest
import re


def get_foo_params(*types, **kwargs_types):
    """Create a toy function that returns True all the time and is decorated
    by the accepts function.
    Parameters:
        types - tuple :
            All the types the toy function is expected to take as parameters
            types
    Returns:
        bar - function :
            the toy function
    """
    @accepts(*types, **kwargs_types)
    def bar(*args, **kwargs):
        return True
    return bar

def get_foo_return(typ):
    """Create a toy function that returns all the arguments given and is
    decorated by the returns function.
    Parameters:
        types - tuple :
            All the types the toy function is expected to take as parameters
            types
    Returns:
        bar - function :
            the toy function
    """
    @returns(typ)
    def bar(args):
        return args
    return bar

def get_error_regex(expected, actual):
    """Build a regex to check if the message of the TypeError exception
    corresponds to the message we expected
    Parameters:
        expected - str:
            The string representing the expected type architecture
        actual - str:
            The string representing the actual type architecture
    """
    expected = re.escape(expected)
    actual = re.escape(actual)
    return r"Expected :\s+" + expected + r".*\n\s+Have\s+:\s+" + actual + "$"

def test_accepts_wrong_params_count():
    foo = get_foo_params(int)
    assert(foo(1))
    expected = r"int"
    actual = r"float"
    regex = r"Mismatch count of args/types \(0/1\)"
    with pytest.raises(ValueError, match=regex):
        foo()


# Note that the parameters are given as a tuple
@pytest.mark.parametrize("types, args",
    [
     ((int,),                       (1,)),
     ((Any,),                       (1,)),
     ((Dict[int, Any],),            ({1:"a", 2:1.5},)),
     ((Set[Any],),                  ({1,2,"a"},)),
     ((List[Any],),                 ([1,2,3],)),
     ((Union[int, str],),           (1,)),
     ((Union[int, str],),           ("a",)),
     ((Union[int, List[int]],),     ([1],)),
     ((Tuple[Union[int, str], int],),
                                    (("a", 1),)),
     ((Tuple[int, Any],),           ((1, "a"),)),
     ((int, float, str),            (1, 1.1, "")),
     ((List[str],),                 (["a", "b"],)),
     ((Set[int],),                  ({1, 2},)),
     ((Tuple[str, int, float],),    (("x", 1, 1.1),)),
     ((Dict[str, int],),            ({"a":1, "b":1, "c":1},)),
     ((Dict[str, Tuple[int, List[Set[int]], List[float]]],),
                                    ({"a":(1,[{1,2,3}],[1.1, 1.2])},))
    ])
def test_accepts_correct(types, args):
    foo = get_foo_params(*types)
    try:
        assert(foo(*args))
    except (TypeError, ValueError, AssertionError) as e:
        print("types    : " + str(types))
        print("args     : " + str(args))
        raise(e)

def test_kwargs():
    foo = get_foo_params(int, x=int, y=int)
    foo(1, x=1, y=1)
    foo(1, y=1, x=1)
    foo(1, x=1)
    foo(1, y=1)
    regex = r"Have :      float"
    with pytest.raises(TypeError, match=regex):
        foo(1, x=1, y=1.5)

# Note that the parameters are given as a tuple
@pytest.mark.parametrize("types, expected, actual, args",
    [((int,),               r"int",         r"float",       (1.1,)),
     ((int, float, str),    r"int",         r"float",       (1.1, 1.1, "")),
     ((int, float, str),    r"float",       r"int",         (1, 1, "")),
     ((int, float, str),    r"str",         r"int",         (1, 1.1, 1)),
     ((List[str],),         r"list[str]",   r"list[int]",   ([1,1],)),
     ((Set[int],),          r"set[int]",    r"set[float]",  ({1, 1.1},)),
     ((Dict[str, int],),    r"dict",        r"list",        ([1,1],)),
     ((Union[str, int],),
        r"union[str, int]",
            r"union[float]",        (1.5,)),
     ((Tuple[str, int, float],),
        r"tuple[str, int, float]",
            r"tuple[str, int, int]",
                (("x", 1, 1),)),
     ((Dict[str, int],),
        r"dict[str, int]",
            r"dict[str, float]",
                ({"a":1, "b":1.1, "c":1},)),
     ((Dict[str, Tuple[int, List[Set[int]], List[float]]],),
        r"dict[str, tuple[int, list, list]]",
            r"dict[str, tuple[int, list, tuple]]",
                ({"a":(1,[{1,2,3}],(1.1, 1.2))},))])
def test_accepts_wrong(types, expected, actual, args):
    foo = get_foo_params(*types)
    error_regex = get_error_regex(expected, actual)
    try:
        with pytest.raises(TypeError, match=error_regex):
            foo(*args)
    except Exception as e:
        print("types    : " + str(types))
        print("expected : " + str(expected))
        print("actual   : " + str(actual))
        print("args     : " + str(args))
        raise(e)


@pytest.mark.parametrize("typ, values",
    [(int,                       1),
     (None,                      None),
     (List[str],                 ["a", "b"]),
     (Set[int],                  {1, 2}),
     (Tuple[str, int, float],    ("x", 1, 1.1)),
     (Dict[str, int],            {"a":1, "b":1, "c":1}),
     (Dict[str, Tuple[int, List[Set[int]], List[float]]],
            {"a":(1,[{1,2,3}],[1.1, 1.2])})])
def test_returns_correct(typ, values):
    foo = get_foo_return(typ)
    try:
        foo(values)
    except (TypeError, ValueError, AssertionError) as e:
        print("Expected return type :  " + str(typ))
        print("Return values        :  " + str(values))
        raise(e)


@pytest.mark.parametrize("types, expected, actual, values",
    [(int,               r"int",         r"float",       1.1),
     (None,              r"NoneType",    r"int",         1),
     (List[str],         r"list[str]",   r"list[int]",   [1,1]),
     (Set[int],          r"set[int]",    r"set[float]",  {1, 1.1}),
     (Dict[str, int],    r"dict",        r"list",        [1,1]),
     (Tuple[str, int, float],
                         r"tuple[str, int, float]",
                                         r"tuple[str, int, int]",
                                                         ("x", 1, 1)),
     (Dict[str, int],
                         r"dict[str, int]",
                                         r"dict[str, float]",
                                                       {"a":1, "b":1.1, "c":1}),
     (Dict[str, Tuple[int, List[Set[int]], List[float]]],
                         r"dict[str, tuple[int, list, list]]",
                                         r"dict[str, tuple[int, list, tuple]]",
                                               {"a":(1,[{1,2,3}],(1.1, 1.2))})])
def test_returns_wrong(types, expected, actual, values):
    foo = get_foo_return(types)
    error_regex = get_error_regex(expected, actual)
    try:
        with pytest.raises(TypeError, match=error_regex):
            foo(values)
    except Exception as e:
        print("types            : " + str(types))
        print("expected type    : " + str(expected))
        print("actual type      : " + str(actual))
        print("return value     : " + str(values))
        raise(e)
