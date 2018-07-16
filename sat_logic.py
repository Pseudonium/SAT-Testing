import pdb


class LogicStatement(list):
    pass


class LogicLiteral():
    pass


def logic_rules(logic_array: list) -> list:
    """
    Simplify logic array based on AND and OR rules.

    Immediately return [True] or [False] for these situations:

        1: Operator is "OR", and 'True' is in the array -> [True].
        2: Operator is "AND", and 'False' is in the array -> [False].

    Otherwise, loop through list, and apply logic_conversion on each element.
    """
    if logic_array[0] == "OR" and any(
            element is True for element in logic_array):
        return [True]
    elif logic_array[0] == "AND" and any(
            element is False for element in logic_array):
        return [False]
    else:
        return [
            logic_conversion(element) for element in logic_array
            if logic_conversion(element)]


def logic_conversion(element):
    """Convert the element into the appropriate form for logic_rules.

    Apply logic_rules recursively if the element is itself a logic array.

    If the element is a boolean, it is not added, as either:
        1: The operator is "OR" and the element is 'False'
        2: The operator is "AND" and the element is 'True'
    The other two combinations are already covered in logic_rules.
    """
    if isinstance(element, list):
        return logic_rules(element)
    elif not isinstance(element, bool):
        return element
    else:
        return False


def set_variable(logic_array: list, var_num: int, value: bool) -> list:
    """Set a truth value to a certain variable in the logic array."""
    return [
        set_variable_converter(element, var_num, value)
        for element in logic_array]


def set_variable_converter(element, var_num: int, value: bool):
    """Convert element into the appropriate form for set_variable."""
    if isinstance(element, list):
        return set_variable(element, var_num, value)
    elif element == var_num:
        return value
    elif element == var_num * -1:
        return not value
    else:
        return element


"""
x = set_variable(
    ["AND", ["OR", ["AND", 1, 7], ["AND", 2, -7], 3],
     ["OR", ["AND", 4, 7], ["AND", 5, -7], 6]], 7, True)
print(x)
print(logic_rules(x))
"""
