import pdb
import os


class LogicStatement():
    def __init__(
            self, logic_array: list=[], dimacs_file: "file_path"=None,
            parent: "LogicStatement"=None):
        """
        Creates a new LogicStatement object.

        Parameters:

            logic_array ---- Take in a logic array and convert it into a
            LogicStatement object.

            dimacs_file --- Allows LogicStatement objects to be directly
            created from a file in conventional dimacs format.
        """
        if parent:
            self.parent = parent
        if dimacs_file:
            self.operator = "AND"
            self.contents = []
            self.dimacs_parser(dimacs_file)
        elif logic_array:
            self.operator = logic_array[0]
            self.contents = [
                LogicStatement(logic_array=element, parent=self)
                if isinstance(element, list) else element
                for element in logic_array[1:]]

    def dimacs_parser(self, dimacs_file):
        """Take CNF instance and parse it into a logic statement."""
        with open(dimacs_file) as f:
            cnf_reached = False
            for line in f:
                if cnf_reached:
                    if line[0] == "%":
                        break
                    line = line.split(" ")
                    if '' in line:
                        line.remove('')
                    line.pop()
                    line = [int(element) for element in line[:]]
                    line.insert(0, "OR")
                    self.contents.append(LogicStatement(
                        logic_array=line, parent=self))
                elif line[0] == "p":
                    cnf_reached = True
                    line = line.split(" ")
                    self.total_var_num = line[2]
                    self.total_clause_num = line[3]
        return self

    def display(self) -> list:
        """Returns an array of the statement, for printing.

        Format of the array:
        ["Operator", [LogicStatement], ..., variable, [LogicStatement], ...]
        """
        return [self.operator] + [
            element.display() if isinstance(element, LogicStatement)
            else element for element in self.contents]

    @staticmethod
    def bool_conversion(element):
        """Convert the element into the appropriate form for simplify_bool.

        Apply simplify_bool recursively if the element is itself a logic array.

        If the element is a boolean, it is not added, as either:
            1: The operator is "OR" and the element is 'False'
            2: The operator is "AND" and the element is 'True'
        The other two combinations are already covered in simplify_bool.
        """
        if isinstance(element, LogicStatement):
            return element.simplify_bool()
        elif not isinstance(element, bool):
            return element
        else:
            return False

    def simplify_bool(self):
        """
        Simplify logic array based on AND and OR rules.

        Immediately return [True] or [False] for these situations:

            1: Operator is "OR", and 'True' is in the array -> [True].
            2: Operator is "AND", and 'False' is in the array -> [False].

        Otherwise, loop through list, and apply bool_conversion on each element.
        """
        if self.operator == "OR" and any(
                element is True for element in self.contents):
            self.contents = [True]
            # self.parent.simplify_bool()
            return self
        elif self.operator == "AND" and any(
                element is False for element in self.contents):
            self.contents = [False]
            # self.parent.simplify_bool()
            return self
        else:
            self.contents = [
                LogicStatement.bool_conversion(element)
                for element in self.contents[:]
                if LogicStatement.bool_conversion(element)]
            return self

    @staticmethod
    def set_variable_conversion(element, var_num: int, value: bool):
        """Convert element into the appropriate form for set_variable."""
        if isinstance(element, LogicStatement):
            return element.set_variable(var_num, value)
        elif element == var_num:
            return value
        elif element == var_num * -1:
            return not value
        else:
            return element

    def set_variable(self, var_num: int, value: bool):
        """Set a truth value to a certain variable in the logic array."""
        self.contents = [
            LogicStatement.set_variable_conversion(element, var_num, value)
            for element in self.contents[:]]
        return self

    def simplify_singleton(self):
        """
        Add contents of statements with one or none sub-statements to parent.
        """
        for statement in self.contents:
            if isinstance(statement, LogicStatement):
                statement.simplify_singleton()
                if len(statement.contents) < 2:
                    for element in statement.contents:
                        self.contents.append(element)
                    self.contents.remove(statement)
                    del statement
        return self

    def simplify_operator(self):
        for statement in self.contents:
            if isinstance(statement, LogicStatement):
                statement.simplify_operator()
                if statement.operator == self.operator:
                    for element in statement.contents:
                        self.contents.append(element)
                    self.contents.remove(statement)
                    del statement
        return self

    def remove_duplicates(self, master=False):
        for element in self.display():
            if isinstance(element, LogicStatement):
                element.remove_duplicates()
        new_contents = []
        for element in self.contents:
            if element not in new_contents:
                new_contents.append(element)
        self.contents = new_contents
        return self

    def negate(self):
        if self.operator == "AND":
            self.operator = "OR"
        else:
            self.operator = "AND"
        self.contents = [
            element.negate() if isinstance(element, LogicStatement)
            else element*-1 for element in self.contents[:]]
        return self

    def simplifier(self):
        old_display = self.display()[:]
        self.simplify_bool().simplify_operator()
        self.simplify_singleton().remove_duplicates()
        if old_display == self.display():
            return self
        else:
            return self.simplifier()


"""
x = LogicStatement(logic_array=[
    "AND", ["OR", ["AND", 1, 7], ["AND", 2, -7], 3],
    ["OR", ["AND", 4, 7], ["AND", 5, -7], 6]])

print(x.set_variable(7, True).display())
print(x.simplifier().display())

# pdb.set_trace()
#y = LogicStatement(dimacs_file="../rSAT-instances/uf20-01.cnf")
# print(y.display())
# print(y.negate().display())

test = LogicStatement(logic_array=[
    "AND", ["OR", 1], ["OR", 2, 3], ["OR", ["AND", 1]]])

# print(test.display())
# pdb.set_trace()
# print(test.simplify_singleton().remove_duplicates().display())
test2 = [1, 2, [3, 3, 5], [6, 7, [8, 8, 9]]]
# pdb.set_trace()
"""
