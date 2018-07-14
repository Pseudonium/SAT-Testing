import pdb


def true_false_rules(logic_array):
    new_array = []
    # pdb.set_trace()
    if logic_array[0] == "AND" and any(
            element is False for element in logic_array):
        new_array.append(False)
        return new_array
    elif logic_array[0] == "OR" and any(
            element is True for element in logic_array):
        new_array.append(True)
        return new_array
    else:
        for element in logic_array:
            if isinstance(element, list):
                new_array.append(true_false_rules(element))
            elif logic_array[0] == "AND" and element is not True:
                new_array.append(element)
            elif logic_array[0] == "OR" and element is not False:
                new_array.append(element)
    return new_array


def set_variable(logic_array, var_num, value):
    new_array = []
    for element in logic_array:
        if isinstance(element, list):
            new_array.append(set_variable(element, var_num, value))
        elif element == var_num:
            new_array.append(value)
        elif element == var_num * -1:
            new_array.append(not value)
        else:
            new_array.append(element)
    return new_array


print(true_false_rules(["AND", False, 2, -3]))
print(set_variable(
    ["AND", ["OR", ["AND", 1, 7], ["AND", 2, -7], 3],
     ["OR", ["AND", 4, 7], ["AND", 5, -7], 6]], 7, False))
