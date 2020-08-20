import functools
import typing
from typing import List, Tuple, Dict, Set, Any, Union
import re

def is_generic(typ):
    """Detect if the parameter is a generic alias from the typing module (e.g.
    list, dict, tuple, set...)
    Parameters:
        typ - type or type from the typing module:
            The type to detect
    Returns:
        bool:
            Return True if 'typ' is a generic alias from the typing module, and
            False otherwise
    """
    return isinstance(typ, typing._GenericAlias)

def get_name(typ):
    """Get the name of the type given. the name should be the simplest (e.g.
    typing.Union[str, int] should be reduced to "union")
    Parameters:
        typ - type or type from the typing module:
            The type that we want the name
    Returns:
        str:
            The name of the type
    """
    if type(typ) is type:
        return typ.__name__
    else:
        group = re.search(r"^typing.(\w+)(\[|$)", str(typ))
        if group is not None:
            return group[1].lower()
        else:
            raise Exception("Could not get the name of type '" + str(typ) + "'")

def get_surrounding(type_list, index):
    """Convert the neighbors into string. This is typically used to create a
    string representation of a type architecture. As we go deeper in the
    architecture, we need to keep track of the neighbors types to print the
    architecture correctly.
    Parameters:
        type_list - type or typing._GenericAlias:
            A list of types to convert into string.
        index - int:
            The index of the current position. As an example, if we have
            [1,1,List, Set], and the current position is 2, then we will convert
            the neighbors on the left into "1, 1, " and the single neighbor on
            the right into ", Set[...]"
    Returns:
        tuple:
            A tuple containing two string elements : the left and right
            neighbors types.
    """
    left = ""
    for i in range(index):
        if is_generic(type_list[i]):
            left += type_list[i].__origin__.__name__
            left += "[...]"
        else:
            left += get_name(type_list[i])
        left += ", "

    right = ""
    for i in range(index+1, len(type_list)):
        right += ", "
        if is_generic(type_list[i]):
            right += type_list[i].__origin__.__name__
            right += "[...]"
        else:
            right += get_name(type_list[i])
    return (left, right)

def type_check(f_name, param_idx, arg, typ):
    """Check if the expected type 'typ' matches the type of the value.
    If the expected type is an iterable, iterate over all element and
    check their type as well, until all types are checked.
    We iterate by layers, which represent the deepness of the architecture
    Example : Tuple[List[int], str]
    Layer 0 : Check if the argument is a tuple
    Layer 1 : Check if elements of tuple are List and str
              Recognize List as a type from the typing module, and keep it
              for the next layer
    Layer 2 : Check if the elements of the list are int. No types from
              the typing module found, stopping
    If a type does not match, a TypeError exception is raised

    Parameters:
        f_name - str:
            The name of the function being type-checked
        param_idx - int:
            The parameter position (or return element position) currently
            being type-checked
        arg - unknown:
            The object to type-check
        typ - type or typing._GenericAlias:
            The expected type of 'arg'
    Returns:
        None

    """
    generic_alias = {list, dict, tuple, set}
    types_to_check = [typ] # the expected types
    args_to_check = [arg] # the actual values given
    # If a type error is raised, we want to print the expected type architecture
    # and the actual type architecture. For this we need to keep track of the
    # architecture as we progress in the layers. The varialbe surroundings takes
    # care of that by keeping the left and right string of the error message.
    # Example : List[int, str]
    # When inspecting the elements of the list, we have :
    #   surrounding[0] = "List[" and
    #   surrounding[1] = "]"
    surroundings = [("", "")]

    # Layer 0
    for i in range(len(types_to_check)):
        typ = types_to_check[i]
        type_expected = typ.__origin__ if is_generic(typ) else typ
        type_actual = type(args_to_check[i])

        # If the type is any or union, we don't need to check the type
        if typ is Any or get_name(typ) == "union":
            pass
        # If the type is a generic alias or a built-in type, we check the type
        elif is_generic(typ) and typ.__origin__ in generic_alias:
            if type_actual is not typ.__origin__:
                raise TypeError(error_msg(f_name,
                                          param_idx,
                                          [typ.__origin__],
                                          [type_actual],
                                          surroundings[0]))
        # if the type comes from the typing module, but none of the above
        # applied, we raise an exception
        elif getattr(typing, str(type(typ)).replace("typing.", ""), None):
            raise(NotImplementedError("The type " + str(type(typ))
                                      + " is not supported yet"))
        # If the type is another type, we check it
        elif type_actual is not typ:
            raise TypeError(error_msg(f_name,
                                      param_idx,
                                      [typ],
                                      [type_actual],
                                      surroundings[0]))

    # Layer 1+
    while len(types_to_check) > 0:
        new_types_to_check = []
        new_args_to_check = []
        new_surroundings = []

        # Check all elements
        for i in range(len(types_to_check)):
            typ = types_to_check[i]
            arg = args_to_check[i]
            surrounding = surroundings[i]

            # If the element is a typing.Union, we check if one of the child is
            # of the correct type, and add it to the args to check
            if get_name(typ) == "union":
                left = surrounding[0] + "union["
                right = "]" + surrounding[1]
                new_surrounding = (left, right)
                subtypes_expected = typ.__args__
                subtypes_expected = [x.__origin__ if is_generic(x) else x
                                         for x in subtypes_expected]
                subtype_actual = type(arg)
                # Check the type of the arg
                idx_candidate = None
                for j in range(len(subtypes_expected)):
                    if subtype_actual is subtypes_expected[j]:
                        idx_candidate = j
                if idx_candidate is None:
                    raise TypeError(error_msg(f_name,
                                              param_idx,
                                              subtypes_expected,
                                              [subtype_actual],
                                              new_surrounding))
                # Check if the element is a generic alias and add it in this
                # case
                if is_generic(subtypes_expected[j]):
                    left, right = get_surrounding(typ.__args__, idx_candidate)
                    new_types_to_check.append(typ.__args__[idx_candidate])
                    new_args_to_check.append(arg)
                    current_surrounding = (new_surrounding[0] + left,
                                           right + new_surrounding[1])
                    new_surroundings.append(current_surrounding)
            # Now check the children if the type is a generic_alias
            elif is_generic(typ):
                left = surrounding[0] + typ.__origin__.__name__ + "["
                right = "]" + surrounding[1]
                new_surrounding = (left, right)
                # We need to check each type separately
                # ---------------- tuple -------------------
                # for tuple, we need to check if each children
                # has the given type. The type may be different
                # for each child
                if typ.__origin__ is tuple:
                    subtypes_expected = typ.__args__
                    subtypes_expected = [x.__origin__ if is_generic(x) else x
                                             for x in subtypes_expected]
                    subtypes_actual = [type(x) for x in arg]
                    # Check the type of all children
                    for j in range(len(subtypes_expected)):
                        if subtypes_expected[j] is not Any and \
                           get_name(typ.__args__[j]) != "union" and \
                           subtypes_expected[j]is not subtypes_actual[j]:
                            raise TypeError(error_msg(f_name,
                                                      param_idx,
                                                      subtypes_expected,
                                                      subtypes_actual,
                                                      new_surrounding))
                    # Check if there are other collections among children and
                    # add them to the check list
                    for j in range(len(subtypes_expected)):
                        if is_generic(typ.__args__[j]) or \
                           get_name(typ.__args__[j]) == "union":
                            left, right = get_surrounding(typ.__args__, j)
                            new_types_to_check.append(typ.__args__[j])
                            new_args_to_check.append(arg[j])
                            current_surrounding = (new_surrounding[0] + left,
                                                   right + new_surrounding[1])
                            new_surroundings.append(current_surrounding)
                # -------------- set or list ----------------
                # for set and list, we need to check if each children
                # has the given type, which is the same for all
                # children
                elif typ.__origin__ is list or typ.__origin__ is set:
                    subtype_expected = typ.__args__[0].__origin__ \
                                        if is_generic(typ.__args__[0]) \
                                        else typ.__args__[0]
                    # Check the type of all children
                    for elem in arg:
                        subtype_actual = type(elem)
                        if subtype_expected is not Any and \
                           get_name(typ.__args__[0]) != "union" and \
                           subtype_actual is not subtype_expected:
                            raise TypeError(error_msg(f_name,
                                                      param_idx,
                                                      [subtype_expected],
                                                      [subtype_actual],
                                                      new_surrounding))
                    # If the children are a collection, add them all to the
                    # check list
                    if is_generic(typ.__args__[0]) or \
                       get_name(typ.__args__[0]) == "union":
                        for elem in arg:
                            new_types_to_check.append(typ.__args__[0])
                            new_args_to_check.append(elem)
                            new_surroundings.append(new_surrounding)
                # ------------------ dict -------------------
                # for dict, the children are key-value pairs,
                # we need to check the types for both key and value
                elif typ.__origin__ is dict:
                    if str(typ.__args__[0]) != "~KT":
                        # If the dict has expected key-value types (if not,
                        # __args__ will return (~KT, ~VT))
                        type_key_expected = typ.__args__[0].__origin__ \
                                            if is_generic(typ.__args__[0]) \
                                            else typ.__args__[0]
                        type_value_expected = typ.__args__[1].__origin__ \
                                            if is_generic(typ.__args__[1]) \
                                            else typ.__args__[1]
                        types_expected = [type_key_expected,
                                          type_value_expected]

                        # check the type of all key-value pairs
                        for key in arg:
                            if (type_key_expected is not Any and
                                get_name(type_key_expected) != "union" and
                                type(key) is not type_key_expected) or \
                               (type_value_expected is not Any and
                                get_name(type(arg[key])) != "union" and
                                type(arg[key]) is not type_value_expected):
                                types_actual = [type(key), type(arg[key])]
                                raise TypeError(error_msg(f_name,
                                                          param_idx,
                                                          types_expected,
                                                          types_actual,
                                                          new_surrounding))
                            # if the value is a collection, we add it to the
                            # check list
                            if is_generic(typ.__args__[1]) or \
                               get_name(typ.__args__[1]) == "union":
                                new_types_to_check.append(typ.__args__[1])
                                new_args_to_check.append(arg[key])
                                left = get_name(type_key_expected) + ", "
                                current_surrounding = (new_surrounding[0] +left,
                                                       new_surrounding[1])
                                new_surroundings.append(current_surrounding)
                else:
                    raise ValueError("Unhandled type '" + str(typ) + "'")
        types_to_check = new_types_to_check
        args_to_check = new_args_to_check
        surroundings = new_surroundings

def accepts(*types, **kwargs_types):
    """Decorator to check the parameter types

    Parameters:
        types - tuple:
            The expected types of the argument given to the decorated function
    Returns:
        function:
            A decorator wrapping the function to check its arguments before
            running it
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if len(args) != len(types):
                raise ValueError("Mismatch count of args/types ("
                                 + str(len(args)) + "/"
                                 + str(len(types)) + ")")
            if len(kwargs) > len(kwargs_types):
                raise ValueError("More kwargs given than types specified")
            # Check the type for each argument
            for i in range(len(args)):
                if types[i] != Any:
                    type_check(f.__name__, i, args[i], types[i])
            # Check the type for each keyword argument
            for i, v in enumerate(kwargs.items()):
                if v[0] not in kwargs_types:
                    raise ValueError(f"Type not specified for kwargs '{v[0]}'")
                expected_type = kwargs_types[v[0]]
                if expected_type != Any:
                    type_check(f.__name__, v[0], v[1], expected_type)
            return f(*args)
        return wrapper
    return decorator


def returns(typ):
    """Decorator to check the return types

    Parameters:
        types - tuple:
            The expected types of the return values of the decorated
            function
    Returns:
        function:
            A decorator wrapping the function to check its return values
            after running it
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            if typ is None and result is not None:
                raise TypeError("Type error on return value of method '"
                                + f.__name__ + "' :\n"
                                + "             Expected : NoneType\n"
                                + "             Have     : "
                                + type(result).__name__)
            elif typ is not None:
                type_check(f.__name__, -1, result, typ)
            return result
        return wrapper
    return decorator

def error_msg(fname, param_idx, expected, actual, surrounding):
    '''Create a type error message

    Parameters:
        param_idx - int:
            The parameter position that raised the error
        expected - list[type]:
            The list of expected types
        actual - list[type]:
            The list of actual types
        surrounding - (str, str) :
            The left and right surrounding of the type that generated the error

    Returns:
        str:
            The error message
    '''
    expected_str = ', '.join([get_name(x) for x in expected])
    actual_str = ', '.join([get_name(x) for x in actual])
    expected_str = surrounding[0] + expected_str + surrounding[1]
    actual_str = surrounding[0] + actual_str + surrounding[1]
    intro = "Type error on return value of method '" + fname + "' :\n"
    # If the type check is on the return type
    if param_idx != -1:
        if isinstance(param_idx, str):
            param_idx = "'" + param_idx + "'"
        intro = "Type error on parameter " + str(param_idx) \
                + " of method '" + fname  + "' :\n"
    msg = intro + "             Expected :  " + expected_str + "\n" \
                + "             Have :  ".ljust(25, " ") + actual_str
    return msg
