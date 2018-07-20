import unittest
import sat_logic
import os
import pdb


def display(self) -> list:
    """
    Returns an array of the statement.

    Format of the array:
    ["Operator", [LogicStatement], ..., variable, [LogicStatement], ...]
    """
    return [self.operator] + [
        display(element) if isinstance(element, sat_logic.LogicStatement)
        else list(element) if isinstance(element, frozenset) else element
        for element in self.contents]


def convert_to_set(iterable):
    new_iterable = frozenset()
    for element in iterable:
        if isinstance(element, list):
            element = convert_to_set(element)
        new_iterable |= {element}
    return new_iterable


class TestCalc(unittest.TestCase):

    def test_display(self):
        x = sat_logic.LogicStatement(logic_array=[
            "AND", ["OR", ["AND", 1, 7], ["AND", 2, -7], 3],
            ["OR", ["AND", 4, 7], ["AND", 5, -7], 6]])
        self.assertEqual(convert_to_set(x.display()), convert_to_set([
            "AND", ["OR", ["AND", 1, 7], ["AND", 2, -7], 3],
            ["OR", ["AND", 4, 7], ["AND", 5, -7], 6]]))

    def test_dimacs_parser(self):
        with open("test_file.txt", "w+") as f:
            for i in range(10):
                f.write("c This is a comment.\n")
            f.write("p cnf 4 2\n")
            f.write("1 2 -3 0\n")
            f.write("-1 3 -4 0\n")

        x = sat_logic.LogicStatement(dimacs_file="test_file.txt")
        self.assertEqual(convert_to_set(display(x)), convert_to_set(
            ["AND", ["OR", 1, 2, -3], ["OR", -1, 3, -4]]))

        os.remove("test_file.txt")

    def test_simplify_bool(self):
        x = sat_logic.LogicStatement(logic_array=[
            "AND", ["OR", ["AND", 1, True], ["AND", 2, False], 3],
            ["OR", ["AND", 4, True], ["AND", 5, False], 6]])
        self.assertEqual(
            convert_to_set(display(x.simplify_bool())),
            convert_to_set(
                ['AND',
                    ['OR', ['AND', 1], 3, ['AND', False]],
                    ['OR', ['AND', 4], 6, ['AND', False]]]))

    def test_set_variable(self):
        x = sat_logic.LogicStatement(logic_array=[
            "AND", ["OR", ["AND", 1, 7], ["AND", 2, -7], 3],
            ["OR", ["AND", 4, 7], ["AND", 5, -7], 6]])
        self.assertEqual(
            convert_to_set(display(x.set_variable(7, True))),
            convert_to_set([
                "AND", ["OR", ["AND", 1, True], ["AND", 2, False], 3],
                ["OR", ["AND", 4, True], ["AND", 5, False], 6]]))

    def test_simplify_singleton(self):
        x = sat_logic.LogicStatement(logic_array=[
            "AND", ["OR", 1], ["OR", 2, 3], ["OR", ["AND", 1]]])
        self.assertEqual(
            convert_to_set(display(x.simplify_singleton())),
            convert_to_set(['AND', 1, ['OR', 2, 3]]))

    def test_simplify_operator(self):
        x = sat_logic.LogicStatement(logic_array=[
            "AND", ["AND", 1, 2, ["OR", 3, 4]], ["OR", 5, 6, ["OR", 7, 8]]
        ])
        self.assertEqual(
            convert_to_set(display(x.simplify_operator())),
            convert_to_set(['AND', 1, 2, ['OR', 3, 4], ['OR', 8, 5, 6, 7]])
        )

    def test_every_true(self):
        x = sat_logic.LogicStatement(logic_array=[
            "AND", ["OR", ["AND", 1, 7], ["AND", 2, -7], 3],
            ["OR", ["AND", 4, 7], ["AND", 5, -7], 6]])
        self.assertEqual(
            x.every_true(7, 6),
            frozenset(
                {frozenset({3, 6}), frozenset({1, 2, 6}),
                 frozenset({1, 2, 4, 5}), frozenset({3, 4, 5})}))


if __name__ == "__main__":
    unittest.main()
