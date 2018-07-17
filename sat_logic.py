import pdb


class LogicStatement():
    def __init__(self, logic_list=[], dimacs_file=None):
        """
        Creates a new LogicStatement object.

        Parameters:

            logic_list ---- Take in a logic array and convert it into a
            LogicStatement object.

            dimacs_file --- Allows LogicStatement objects to be directly created
            from a file in conventional dimacs format.
        """
        if dimacs_file:
            self.operator = "AND"
            self.logic_parser(dimacs_file)
        elif logic_list:
            self.operator = logic_list[0]
            self.contents = [
                LogicStatement(logic_list=element)
                if isinstance(element, list)
                else element for element in logic_list[1:]]

    def logic_parser(self, dimacs_file):
        """Take CNF instance and parse it into a logic statement."""
        with open(dimacs_file) as f:
            cnf_reached = False
            for line in f:
                if cnf_reached:
                    line = line.split(" ")
                    line.insert(0, "OR")
                    self.contents.append(LogicStatement(logic_array=line))
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
    def logic_conversion(element):
        """Convert the element into the appropriate form for logic_rules.

        Apply logic_rules recursively if the element is itself a logic array.

        If the element is a boolean, it is not added, as either:
            1: The operator is "OR" and the element is 'False'
            2: The operator is "AND" and the element is 'True'
        The other two combinations are already covered in logic_rules.
        """
        if isinstance(element, LogicStatement):
            return element.logic_rules()
        elif not isinstance(element, bool):
            return element
        else:
            return False

    def logic_rules(self):
        """
        Simplify logic array based on AND and OR rules.

        Immediately return [True] or [False] for these situations:

            1: Operator is "OR", and 'True' is in the array -> [True].
            2: Operator is "AND", and 'False' is in the array -> [False].

        Otherwise, loop through list, and apply logic_conversion on each element.
        """
        if self.operator == "OR" and any(
                element is True for element in self.contents):
            self.contents = [True]
            return self
        elif self.operator == "AND" and any(
                element is False for element in self.contents):
            self.contents = [False]
            return self
        else:
            self.contents = [
                LogicStatement.logic_conversion(element)
                for element in self.contents[:]
                if LogicStatement.logic_conversion(element)]
            return self

    @staticmethod
    def set_variable_converter(element, var_num: int, value: bool):
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
            LogicStatement.set_variable_converter(element, var_num, value)
            for element in self.contents[:]]
        return self


x = LogicStatement(logic_list=[
    "AND", ["OR", ["AND", 1, 7], ["AND", 2, -7], 3],
    ["OR", ["AND", 4, 7], ["AND", 5, -7], 6]])
