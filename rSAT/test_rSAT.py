import unittest
import rSAT
from rSAT import LogicStatement
import collections


class TestRSAT(unittest.TestCase):

    def test_cnf_parser(self):
        line1 = "1 -3 2 0\n"
        line2 = "  1 4  -5 0\n"
        line3 = "4 -3 -2 "

        self.assertEqual(rSAT.cnf_parser(line1), ["OR", 1, -3, 2])
        self.assertEqual(rSAT.cnf_parser(line2), ["OR", 1, 4, -5])
        self.assertRaises(rSAT.FormatError, rSAT.cnf_parser, line3)

    def test_dimacs_parser(self):
        self.assertRaises(IOError, rSAT.dimacs_parser, "dummy")
        Parameters = collections.namedtuple(
            'Parameters', ['logic_list', 'var_num', 'clause_num']
        )
        self.assertEqual(
            rSAT.dimacs_parser("test_ksat.dimacs"),
            Parameters(
                logic_list=['AND',
                            ['OR', -1, -3, 5],
                            ['OR', 2, 3, -4],
                            ['OR', 2, 3, 4],
                            ['OR', 1, -2, -3],
                            ['OR', -2, 4, -3],
                            ['OR', -1, -4, 5],
                            ['OR', 1, -2, -5],
                            ['OR', -5, -2, 4],
                            ['OR', -5, -4, -1],
                            ['OR', -3, 4, 2]
                            ],
                var_num=5, clause_num=10
            )
        )

    def test_display(self):
        x = LogicStatement(
            ["AND",
                ["OR", ["AND", 1, 7], ["AND", 2, -7], 3],
                ["OR", ["AND", 4, 7], ["AND", 5, -7], 6]
             ]
        )
        self.assertEqual(
            x.display,
            ["AND",
                ["OR", ["AND", 1, 7], ["AND", 2, -7], 3],
                ["OR", ["AND", 4, 7], ["AND", 5, -7], 6]
             ]
        )

    def test_sort(self):
        x = LogicStatement(
            ["AND",
                ["OR", ["AND", 7, 1], ["AND", 2, -7], 3],
                ["OR", ["AND", -4, 4, 7], 6, ["AND", 5, -7]]
             ]
        )
        self.assertEqual(
            x.sort().display,
            ["AND",
                ["OR", ["AND", 1, 7], ["AND", 2, -7], 3],
                ["OR", ["AND", 4, -4, 7], ["AND", 5, -7], 6]
             ]
        )


if __name__ == "__main__":
    unittest.main()
