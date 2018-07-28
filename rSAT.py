import pdb
import os
import collections
from sys import getsizeof
import itertools
from functools import total_ordering


class Error(Exception):
    pass


class FormatError(Error):
    pass


def cnf_parser(dimacs_line):
    line = dimacs_line
    line = line.split(" ")
    while '' in line:
        line.remove('')
    # 0 is always at the end of the line, so we remove it
    end = line.pop()
    if end != '0\n':
        line.append(end)
        #print("Error line: ", line)
        raise FormatError(
            """0 must terminate all cnf lines.
            Error line: """, line)
    for index, element in enumerate(line):
        line[index] = int(element)
    line.insert(0, "OR")
    return line


def dimacs_parser(dimacs_filepath):
    try:
        f = open(dimacs_filepath)
    except IOError:
        raise IOError("File either corrupted or not found.")
    else:
        Parameters = collections.namedtuple(
            'Parameters', ['logic_list', 'var_num', 'clause_num'])
        with f:
            logic_list = ["AND"]
            cnf_reached = False
            for line in f:
                if cnf_reached:
                    if line[0] == "%":
                        break
                    line = cnf_parser(line)
                    logic_list.append(LogicStatement(line))
                elif line[0] == "p":
                    cnf_reached = True
                    line = line.split(" ")
                    while '' in line:
                        line.remove('')
                    var_num = int(line[2])
                    clause_num = int(line[3])
        return Parameters(logic_list, var_num, clause_num)


def custom_abs(x):
    return (abs(x), x < 0)


@total_ordering
class LogicStatement:

    def __init__(self, logic_list: list, dimacs_dict: dict = None):
        self.operator = logic_list[0]
        self.contents = [
            LogicStatement(element) if isinstance(element, list)
            else element for element in itertools.islice(
                logic_list, 1, len(logic_list))
        ]
        self.other_attr = False
        if dimacs_dict is not None:
            for key, value in dimacs_dict.items():
                setattr(self, key, value)
            self.other_attr = True

    def __repr__(self):
        if self.other_attr:
            return "LogicStatement({}, {})".format(
                self.display, self.attr_dict)
        else:
            return "LogicStatement({})".format(self.display)

    def __str__(self):
        return str(self.display)

    def __eq__(self, other):
        self.sort()
        return (
            (self.operator, self.contents) == (other.operator, other.contents))

    def __lt__(self, other):
        if self.abs_var_tuple == other.abs_var_tuple:
            return self.var_tuple > other.var_tuple
        else:
            return self.abs_var_tuple < other.abs_var_tuple

    @classmethod
    def from_dimacs(cls, dimacs_filepath: str):
        parsed_file = dimacs_parser(dimacs_filepath)
        return cls(
            parsed_file.logic_list, {
                'var_num': parsed_file.var_num,
                'clause_num': parsed_file.clause_num
            }
        )

    @property
    def display(self) -> list:
        return [self.operator] + [
            element.display if isinstance(element, LogicStatement)
            else element for element in self.contents
        ]

    @property
    def var_tuple(self) -> tuple:
        master_set = set()
        for element in self.contents:
            if isinstance(element, LogicStatement):
                master_set.update(element.var_tuple)
            else:
                master_set.add(element)
        return tuple(sorted(master_set, key=custom_abs))

    @property
    def abs_var_tuple(self) -> tuple:
        return tuple(sorted({abs(x) for x in self.var_tuple}))

    def sort(self):
        statements = []
        variables = []
        for element in self.contents:
            if isinstance(element, LogicStatement):
                element.sort()
                statements.append(element)
            else:
                variables.append(element)
        statements.sort()
        variables.sort(key=custom_abs)
        self.contents = statements + variables
        return self


if __name__ == "__main__":

    x = LogicStatement(["AND",
                        ["OR", ["AND", 1, 7], ["AND", 2, -7], 3],
                        ["OR", ["AND", 4, 7], 6, ["AND", 5, -7]]]
                       )
    # print(x)
    # print(repr(x))
    y = LogicStatement.from_dimacs("../rSAT-instances/uf20-01.cnf")
    # print(y)
    # print(repr(y))
    z = dimacs_parser("test_ksat.dimacs")
    # print(z)
    a = LogicStatement.from_dimacs("test_ksat.dimacs")
    print(a)
    a.sort()
    print(a)
    print(x.sort())
