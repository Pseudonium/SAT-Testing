import pdb


def logic_rules(logic_array: list) -> list:
    if logic_array[0] == "AND" and any(
            element is False for element in logic_array):
        return [False]
    elif logic_array[0] == "OR" and any(
            element is True for element in logic_array):
        return [True]
    else:
        return [
            logic_conversion(element) for element in logic_array
            if logic_conversion(element)]


def logic_conversion(element):
    if isinstance(element, list):
        return logic_rules(element)
    elif not isinstance(element, bool):
        return element
    else:
        return False


def set_variable(logic_array: list, var_num: int, value: bool) -> list:
    return [
        set_variable_converter(element, var_num, value)
        for element in logic_array]


def set_variable_converter(element, var_num: int, value: bool):
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
