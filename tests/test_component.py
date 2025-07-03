"""
Created on 12. 11. 2018

@author: esner
"""

import unittest
import mock
import os
import tempfile
from freezegun import freeze_time

from component import Component
from keboola.component.exceptions import UserException


class TestComponent(unittest.TestCase):
    # set global time to 2010-10-10 - affects functions like datetime.now()
    @freeze_time("2010-10-10")
    # set KBC_DATADIR env to non-existing dir
    @mock.patch.dict(os.environ, {"KBC_DATADIR": "./non-existing-dir"})
    def test_run_no_cfg_fails(self):
        with self.assertRaises(ValueError):
            comp = Component()
            comp.run()

    @mock.patch.dict(os.environ, {"KBC_COMPONENTID": "keboola.processor-decompress", "KBC_DATADIR": "/tmp"})
    @mock.patch.object(
        Component, "configuration", mock.PropertyMock(return_value=mock.Mock(parameters={"compression_type": "zip"}))
    )
    def test_decompress_invalid_zip_file(self):
        # Create a temporary file that's not a valid zip
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as temp_file:
            temp_file.write('"val1","val2"\n')
            temp_file_path = temp_file.name

        try:
            # Mock the component to use our temp file
            with mock.patch.object(Component, "_get_in_files", return_value=[temp_file_path]):
                with mock.patch.object(Component, "_get_out_path", return_value="/fake/path/out"):
                    with self.assertRaises(UserException):
                        comp = Component()
                        comp.run()
        finally:
            # Clean up the temp file
            os.unlink(temp_file_path)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
