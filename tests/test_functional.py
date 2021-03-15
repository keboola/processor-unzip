'''
Created on 12. 11. 2018

@author: esner
'''
import filecmp
import os
import unittest
from os import path
from os.path import dirname

from component import Component

FUNCTIONAL_TEST_DIR = path.join(dirname(path.realpath(__file__)), 'functional')
FOLDERED_TEST_DIR = path.join(dirname(path.realpath(__file__)), 'foldered')


class TestFunctional(unittest.TestCase):

    def test_functional(self):
        '''
        tests if the resulting hierarchy of files conforms to the specififed one
        '''
        os.path.dirname(os.path.realpath(__file__))
        test_errors = []
        for test in os.listdir(FUNCTIONAL_TEST_DIR):
            if test.startswith('.'):
                continue
            test_dir = path.join(FUNCTIONAL_TEST_DIR, test)
            data_dir = path.join(test_dir, 'source', 'data')
            os.environ["KBC_DATADIR"] = data_dir
            comp = Component()
            comp.run()
            result = self.compare_output_structure(test_dir)
            if result:
                test_errors.append(f'Functional test {test} failed with error: {result}!')

        self.assertEqual(test_errors, [], msg=', \n '.join(test_errors))

    def test_files_outputed_to_folders(self):
        '''
        tests if the resulting hierarchy of files conforms to the specififed one
        '''
        os.path.dirname(os.path.realpath(__file__))
        test_errors = []
        for test in os.listdir(FOLDERED_TEST_DIR):
            if test.startswith('.'):
                continue
            test_dir = path.join(FOLDERED_TEST_DIR, test)
            data_dir = path.join(test_dir, 'source', 'data')
            os.environ["KBC_DATADIR"] = data_dir
            comp = Component()
            comp.run()
            result = self.compare_output_structure(test_dir, compare_dir=True)
            if result:
                test_errors.append(f'Foldered test {test} failed with error: {result}!')

        self.assertEqual(test_errors, [], msg=', \n '.join(test_errors))

    def compare_output_structure(self, test_dir, compare_dir=False):
        '''
        compares the expected output files/tables with the actual output files
        '''

        files_expected_path = path.join(test_dir, 'expected', 'data', 'out', 'files')
        tables_expected_path = path.join(test_dir, 'expected', 'data', 'out', 'tables')
        files_real_path = path.join(test_dir, 'source', 'data', 'out', 'files')
        tables_real_path = path.join(test_dir, 'source', 'data', 'out', 'tables')

        # report differences
        filecmp.dircmp(files_real_path, files_expected_path).report()

        out_files_expected = [file for file in os.listdir(files_expected_path) if not file.startswith('.')]
        out_tables_expected = [file for file in os.listdir(tables_expected_path) if not file.startswith('.')]
        out_files_real = [file for file in os.listdir(files_real_path) if not file.startswith('.')]
        out_tables_real = [file for file in os.listdir(tables_real_path) if not file.startswith('.')]

        if set(out_files_real) != set(out_files_expected) or set(out_tables_real) != set(out_tables_expected):
            return "Files do not match"

        error = ""

        if not compare_dir:
            match, mismatch_files, errors_files = filecmp.cmpfiles(files_real_path, files_expected_path,
                                                                   [os.path.basename(f) for f in out_files_expected])
        if compare_dir:
            mismatch_files = filecmp.dircmp(files_real_path, files_expected_path).diff_files
            errors_files = filecmp.dircmp(files_real_path, files_expected_path).funny_files

        mismatch_files = [file for file in mismatch_files if not file.startswith('.')]
        match, mismatch_tables, errors_tables = filecmp.cmpfiles(tables_real_path, tables_expected_path,
                                                                 [os.path.basename(f) for f in out_tables_expected])

        if mismatch_files or errors_files:
            error += f"Result files {mismatch_files} are different from what expected. Found errors {errors_files}"

        if mismatch_tables or errors_tables:
            error += f"\n Result tables {mismatch_tables} are different from what expected. " \
                     f"Found errors {errors_tables}"

        return error


if __name__ == "__main__":
    unittest.main()
