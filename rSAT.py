import pdb
import os
import collections


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
        print("Error line: ", line)
        raise FormatError("0 must terminate all cnf lines.")
    line = [int(element) for element in line[:]]
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
                    var_num = line[2]
                    clause_num = line[3]
        return Parameters(logic_list, var_num, clause_num)

    # raise NotImplementedError


class LogicStatement:

    def __init__(self, logic_list: list, dimacs_dict: dict = None):
        self.operator = logic_list[0]
        self.contents = [
            LogicStatement(element) if isinstance(element, list)
            else element for element in logic_list[1:]
        ]
        if dimacs_dict is not None:
            for key, value in dimacs_dict.items():
                setattr(self, key, value)
            self.attr_dict = dimacs_dict

    def __repr__(self):
        if hasattr(self, 'attr_dict'):
            return "LogicStatement({}, {})".format(
                self.display(), self.attr_dict)
        else:
            return "LogicStatement({})".format(self.display())

    def __str__(self):
        return str(self.display())

    def display(self):
        return [self.operator] + [
            element.display() if isinstance(element, LogicStatement)
            else element for element in self.contents
        ]

    @classmethod
    def from_dimacs(cls, dimacs_filepath: str):
        parsed_file = dimacs_parser(dimacs_filepath)
        return cls(
            parsed_file.logic_list, {
                'var_num': parsed_file.var_num,
                'clause_num': parsed_file.clause_num
            }
        )


if __name__ == "__main__":

    x = LogicStatement(["AND",
                        ["OR", ["AND", 1, 7], ["AND", 2, -7], 3],
                        ["OR", ["AND", 4, 7], ["AND", 5, -7], 6]]
                       )
    print(x)
    print(repr(x))
    y = LogicStatement.from_dimacs("../rSAT-instances/uf20-01.cnf")
    print(y)
    print(repr(y))
