"""
Template Component main class.

"""
import logging
import glob
import os

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException
from modules.utils import Decompressor, FormatRegistrator

# configuration variables
EXTRACT_TO_FOLDER = 'extract_to_folder'

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
REQUIRED_PARAMETERS = [EXTRACT_TO_FOLDER]


class Component(ComponentBase):
    """
        Extends base class for general Python components. Initializes the CommonInterface
        and performs configuration validation.

        For easier debugging the data folder is picked up by default from `../data` path,
        relative to working directory.

        If `debug` parameter is present in the `config.json`, the default logger is set to verbose DEBUG mode.
    """

    def __init__(self):
        super().__init__()
        self.params = None

    def run(self):
        """
        Main execution code
        """

        # check for missing configuration parameters
        self.validate_configuration_parameters(REQUIRED_PARAMETERS)
        self.params = self.configuration.parameters

        logging.info("Extraction starting.")
        FormatRegistrator.register_formats()

        for file in self._get_in_files():
            file_out_path = self._get_out_path(file)
            Decompressor(file, file_out_path).decompress()

        logging.info("Extraction done.")
        FormatRegistrator.unregister_formats()

    def _get_in_files(self):
        files = glob.glob(os.path.join(self.files_in_path, "**/*"), recursive=True)
        return [f for f in files if not os.path.isdir(f)]

    def _get_out_path(self, filepath) -> str:
        filename, relative_dir = self._get_filename_from_path(filepath)
        out_path = os.path.join(self.files_out_path, relative_dir)
        if self.params.get(EXTRACT_TO_FOLDER):
            out_path = os.path.join(self.files_out_path, relative_dir, filename)
        return out_path

    def _get_filename_from_path(self, file_path, remove_ext=True):
        """
        Get file name while keeping the nested structure.
        :param file_path:
        :param remove_ext:
        :return:
        """
        relative_dir = os.path.dirname(file_path).replace(self.files_in_path, '').lstrip('/').lstrip('\\')
        filename = os.path.basename(file_path)

        if remove_ext:
            filename = filename.split(".")[0]

        return filename, relative_dir


"""
        Main entrypoint
"""
if __name__ == "__main__":
    try:
        comp = Component()
        # this triggers the run method by default and is controlled by the configuration.action parameter
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
