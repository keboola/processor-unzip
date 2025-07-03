import unittest
import os

from datadirtest import DataDirTester


class TestComponent(unittest.TestCase):
    def test_functional_unzip(self):
        os.environ["KBC_COMPONENTID"] = "kds-team.processor-unzip"
        functional_tests = DataDirTester(data_dir="./tests/unzip/")
        functional_tests.run()

    def test_functional_decompress(self):
        os.environ["KBC_COMPONENTID"] = "keboola.processor-decompress"
        functional_tests = DataDirTester(data_dir="./tests/decompress/")
        functional_tests.run()


if __name__ == "__main__":
    unittest.main()
