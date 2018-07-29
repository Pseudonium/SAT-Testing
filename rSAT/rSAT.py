import pdb
import collections
from sys import getsizeof
import itertools
import functools
import operator


class Error(Exception):
    pass


class FormatError(Error):
    pass


def cnf_parser(dimacs_line: str) -> list:
    """Parse a single line in dimacs format."""
    line = dimacs_line
    line = line.split(" ")
    # Removes accidental whitespace
    while '' in line:
        line.remove('')
    # 0 is always at the end of the line, so remove it
    end = line.pop()
    if int(end) != 0:
        line.append(end)
        # print("Error line: ", line)
        raise FormatError(
            """0 must terminate all cnf lines.
            Error line: """, line)
    for index, element in enumerate(line):
        line[index] = int(element)
    # Make line a formal logic_list
    line.insert(0, "OR")
    return line


def dimacs_parser(dimacs_filepath: str) -> collections.namedtuple:
    """Parse a file in dimacs format."""
    try:
        f = open(dimacs_filepath)
    except IOError:
        raise IOError(
            "File {} corrupted or not found.".format(dimacs_filepath)
        )
    else:
        Parameters = collections.namedtuple(
            'Parameters', ['logic_list', 'var_num', 'clause_num']
        )
        with f:
            logic_list = ["AND"]
            cnf_reached = False
            for line in f:
                if cnf_reached:
                    # Some formats have a % at the end of the file.
                    if line[0] == "%":
                        break
                    line = cnf_parser(line)
                    logic_list.append(line)
                elif line[0] == "p":
                    cnf_reached = True
                    line = line.split(" ")
                    while '' in line:
                        line.remove('')
                    var_num = int(line[2])
                    clause_num = int(line[3])
        return Parameters(logic_list, var_num, clause_num)


def custom_abs(x: int) -> tuple:
    """Return a comparison tuple using abs; positives take precedence."""
    return (abs(x), x < 0)


@functools.total_ordering
class LogicStatement:

    def __init__(self, logic_list: list, dimacs_dict: dict = None):
        """
        Create a new LogicStatement object.

        Positional arguments:
            logic_list --- Representation of the statement.
            Format is [operator, *sub_statements/variables]

        Optional arguments:
            dimacs_dict -- Info from the dimacs file used to create it.
            Contains the number of variables and the number of clauses.
        """
        self.operator = logic_list[0]
        self.contents = [
            LogicStatement(element) if isinstance(element, list)
            else LogicLiteral(element) for element in itertools.islice(
                logic_list, 1, len(logic_list))
        ]
        if dimacs_dict is not None:
            for key, value in dimacs_dict.items():
                setattr(self, key, value)
            self.attr_dict = dimacs_dict

    def __repr__(self):
        if hasattr(self, 'attr_dict'):
            return "{}({}, {})".format(
                type(self).__name__,
                self.display, self.attr_dict)
        else:
            return "{}({})".format(type(self).__name__, self.display)

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

    def __iter__(self):
        return iter(self.contents)

    @classmethod
    def from_dimacs(cls, dimacs_filepath: str):
        """Construct LogicStatement object from a dimacs file."""
        parsed_file = dimacs_parser(dimacs_filepath)
        return cls(
            parsed_file.logic_list, {
                'var_num': parsed_file.var_num,
                'clause_num': parsed_file.clause_num
            }
        )

    @property
    def display(self) -> list:
        """Get a display of the LogicStatement object.

        Used for __str__ and comparisons in unittests.
        """
        return [self.operator] + [
            element.display if isinstance(element, LogicStatement)
            else element for element in self
        ]

    @property
    def var_tuple(self) -> tuple:
        """Get a tuple of all variables in the LogicStatement.

        They are sorted by their absolute value,
        with positives before negatives.
        """
        var_set = set()
        for element in self:
            if isinstance(element, LogicStatement):
                var_set.update(element.var_tuple)
            else:
                var_set.add(element)
        return tuple(sorted(var_set, key=custom_abs))

    @property
    def abs_var_tuple(self) -> tuple:
        """Get all variables in the LogicStatement, ignoring negations.

        Used for sorting, as LogicStatements containing smaller variables
        are considered smaller than those that contain larger variables.
        """
        return tuple(sorted({abs(x) for x in self.var_tuple}))

    def sort(self):
        """Sort a LogicStatement object.

        Used so that display comparisons remain consistent,
        even if LogicStatement is changed to a different order.

        Statements are chosen arbitrarily to be smaller than variables,
        so that the format is:

        [operator, Statement, Statement, Statement, ...,
         variable, ..., variable]
        """
        statements = []
        variables = []
        for element in self:
            if isinstance(element, LogicStatement):
                element.sort()
                statements.append(element)
            else:
                variables.append(element)
        statements.sort()
        variables.sort(key=custom_abs)
        self.contents = statements + variables
        return self


class LogicLiteral(LogicStatement):
    def __init__(self, var_num):
        self.contents = [var_num]
        self.var = var_num
        self.operator = None

    def __str__(self):
        return str(self.var)

    def __mul__(self, other):
        if isinstance(other, LogicLiteral):
            return LogicStatement(["AND", self.var, other.var])
        return NotImplemented

    @property
    def display(self):
        return self.var

    @property
    def var_tuple(self):
        return self.var,

    @property
    def abs_var_tuple(self):
        return abs(self.var),

    def sort(self):
        return self


if __name__ == "__main__":

    x = LogicStatement(
        ["AND",
            ["OR", ["AND", 1, 7], ["AND", 2, -7], 3],
            ["OR", ["AND", 4, 7], 6, ["AND", 5, -7]]]
    )
    # print(x)
    # y = LogicStatement.from_dimacs("../../SAT-Testing-instances/uf20-01.cnf")
    # print(y)
    # print(repr(y))
    z = dimacs_parser("test_ksat.dimacs")
    # print(z)
    # pdb.set_trace()
    a = LogicStatement.from_dimacs("test_ksat.dimacs")
    # print(a)
    # pdb.set_trace()
    # a.sort()
    # print(a)
    # print(x.sort())
    pass
