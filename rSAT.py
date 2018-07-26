import pdb
import os


class Error(Exception):
    pass


class KeywordNumError(Error, TypeError):
    pass


class LogicStatement:
    def __init__(self, dimacs_filepath: str = None, logic_list: list = None):
        if dimacs_filepath and logic_list:
            raise KeywordNumError(
                "Cannot pass both filepath and list as arguments")
        elif dimacs_filepath:
            self.operator = "AND"
            self.contents = []
            self.dimacs_parser(dimacs_filepath)
        elif logic_list:
            self.operator = logic_list[0]
            self.contents = [
                LogicStatement(logic_list=element)
                if isinstance(element, list)
                else element for element in logic_list

    def __str__(self):


    def dimacs_parser(self, dimacs_filepath):
        raise NotImplementedError


x= LogicStatement(
    logic_list=["AND",
                ["OR", ["AND", 1, 7], ["AND", 2, -7], 3],
                ["OR", ["AND", 4, 7], ["AND", 5, -7], 6]]
)
print(x)
