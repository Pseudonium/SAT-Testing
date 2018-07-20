import itertools
import copy


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
            self.contents = frozenset()
            self.dimacs_parser(dimacs_file)
        elif logic_array:
            self.operator = logic_array[0]
            self.contents = frozenset([
                LogicStatement(logic_array=element, parent=self)
                if isinstance(element, list) else element
                for element in logic_array[1:]])

    def __repr__(self):
        """
        Returns a constructor of the object, as a string.
        """
        return "LogicStatement(logic_array={})".format([self.operator] + [
            element.display() if isinstance(element, LogicStatement)
            else list(element) if isinstance(element, frozenset) else element
            for element in self.contents])

    def __str__(self):
        """
        Returns an array of the statement, for printing.

        Format of the array:
        ["Operator", [LogicStatement], ..., variable, [LogicStatement], ...]
        """
        return str(self.display())

    def display(self) -> list:
        """
        Returns an array of the statement.

        Format of the array:
        ["Operator", [LogicStatement], ..., variable, [LogicStatement], ...]
        """
        return [self.operator] + [
            element.display() if isinstance(element, LogicStatement)
            else list(element) if isinstance(element, frozenset) else element
            for element in self.contents]

    def dimacs_parser(self, dimacs_file):
        """
        Take CNF instance and parse it into a logic statement.
        """
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
                    self.contents |= {LogicStatement(
                        logic_array=line, parent=self)}
                elif line[0] == "p":
                    cnf_reached = True
                    line = line.split(" ")
        return self

    @staticmethod
    def bool_conversion(element):
        """
        Convert the element into the appropriate form for simplify_bool.

        Apply simplify_bool recursively if the element is a LogicStatement.

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

        Otherwise loop through and apply bool_conversion on each element.
        """
        if self.operator == "OR" and any(
                element is True for element in self.contents):
            self.contents = frozenset({True})
            return self
        elif self.operator == "AND" and any(
                element is False for element in self.contents):
            self.contents = frozenset({False})
            return self
        elif self.contents == (frozenset({True}) or frozenset({False})):
            return self
        else:
            self.contents = frozenset([
                LogicStatement.bool_conversion(element)
                for element in copy.deepcopy(self.contents)
                if LogicStatement.bool_conversion(element)])
            return self

    @staticmethod
    def set_variable_conversion(element, var_num: int, value: bool):
        """
        Convert element into the appropriate form for set_variable.
        """
        if isinstance(element, LogicStatement):
            return element.set_variable(var_num, value)
        elif element == var_num:
            return value
        elif element == var_num * -1:
            return not value
        else:
            return element

    def set_variable(self, var_num: int, value: bool):
        """
        Set a truth value to a certain variable in the logic array.
        """
        self.contents = frozenset([
            LogicStatement.set_variable_conversion(element, var_num, value)
            for element in copy.deepcopy(self.contents)])
        return self

    def simplify_singleton(self):
        """
        Add contents of statements with one or none sub-statements to self.
        """
        for statement in self.contents:
            if isinstance(statement, LogicStatement):
                statement.simplify_singleton()
                if len(statement.contents) < 2:
                    for element in statement.contents:
                        self.contents |= {element}
                    self.contents -= {statement}
                    del statement
        return self

    def simplify_operator(self):
        """
        Add contents of statements with the same operator as self.
        """
        for statement in self.contents:
            if isinstance(statement, LogicStatement):
                statement.simplify_operator()
                if statement.operator == self.operator:
                    for element in statement.contents:
                        self.contents |= {element}
                    self.contents -= {statement}
                    del statement
        return self

    def negate(self):
        """
        Negate the object - normal logic rules are applied.
        """
        if self.operator == "AND":
            self.operator = "OR"
        else:
            self.operator = "AND"
        self.contents = frozenset([
            element.negate() if isinstance(element, LogicStatement)
            else element*-1 for element in copy.deepcopy(self.contents)])
        return self

    def simplify(self):
        """
        Keep applying simplify methods until the object no longer changes.
        """
        old_display = self.display()[:]
        self.simplify_bool().simplify_operator().simplify_singleton()
        if old_display == self.display():
            return self
        else:
            return self.simplify()

    def every_true(self, check_var, total_other_variables):
        check_array = itertools.product(
            [True, False],
            repeat=total_other_variables)
        setter = list(range(1, total_other_variables + 1))
        good_combos = []
        for combo in check_array:
            self_copy_1 = copy.deepcopy(self)
            for var, value in zip(setter, combo):
                self_copy_1.set_variable(var, value)
            self_copy_1.simplify()
            self_copy_2 = copy.deepcopy(self_copy_1)
            self_copy_3 = copy.deepcopy(self_copy_1)
            if (
                    self_copy_1.contents == frozenset({True})
                    or (
                        self_copy_2.set_variable(
                            check_var, True).simplify(
                        ).contents == frozenset({True})
                        and self_copy_3.set_variable(
                            check_var, False).simplify(
                        ).contents == frozenset({True}))):
                good_combos.append(combo)
            del self_copy_1
            del self_copy_2
            del self_copy_3
        final_set = frozenset()
        for combo in good_combos:
            inner_set = frozenset(
                {index + 1 for index in range(len(combo)) if combo[index]})
            final_set |= {inner_set}
        for set in final_set:
            for other in final_set:
                if set < other:
                    final_set -= frozenset({other})
        return final_set


if __name__ == "__main__":
    pass
