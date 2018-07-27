import pdb
import os


class Error(Exception):
    pass


def dimacs_parser(dimacs_filepath):
    raise NotImplementedError


class LogicStatement:

    def __init__(self, logic_list: list):
        self.operator = logic_list[0]
        self.contents = [
            LogicStatement(element) if isinstance(element, list)
            else element for element in logic_list[1:]
        ]

    @classmethod
    def from_dimacs(cls, dimacs_filepath: str):
        return cls(dimacs_parser(dimacs_filepath))


x = LogicStatement(["AND",
                    ["OR", ["AND", 1, 7], ["AND", 2, -7], 3],
                    ["OR", ["AND", 4, 7], ["AND", 5, -7], 6]]
                   )
print(x)
y = LogicStatement.from_dimacs("../rSAT-instances/uf20-01.cnf")
