"""
Template Component main class.

"""

import logging
import glob
import os

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException
from decompress import Decompressor, SUPPORTED_FORMATS

# configuration variables
EXTRACT_TO_FOLDER = "extract_to_folder"
PASSWORD_7Z = "#password_7z"
GRACEFUL = "graceful"

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
REQUIRED_PARAMETERS = []


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

        self.params = self.configuration.parameters

        logging.info("Extraction starting.")

        password = self.params.get(PASSWORD_7Z)
        graceful = self.params.get(GRACEFUL)

        d = Decompressor(password=password)
        for file in self._get_in_files():
            file_extension = os.path.splitext(file)[-1]
            if file_extension in SUPPORTED_FORMATS:
                file_out_path = self._get_out_path(file)
                try:
                    d.run_decompressor(file, file_out_path)

                except Exception as e:
                    if graceful:
                        logging.error(f"Error processing file {file}: {e}")
                    else:
                        raise UserException(f"Error processing file {file}: {e}")
            else:
                logging.warning(f"Unsupported file {file} will be skipped.")

        logging.info("Extraction done.")

        # Unregistering formats is here for easier tests writing.
        d.unregister_formats()

    def _get_in_files(self) -> list:
        files = glob.glob(os.path.join(self.files_in_path, "**/*"), recursive=True)
        return [f for f in files if not os.path.isdir(f)]

    def _get_out_path(self, filepath) -> str:
        filename, relative_dir = self._get_filename_from_path(filepath)
        out_path = os.path.join(self.files_out_path, relative_dir)
        if self.params.get(EXTRACT_TO_FOLDER):
            out_path = os.path.join(self.files_out_path, relative_dir, filename)
        return out_path

    def _get_filename_from_path(self, file_path, remove_ext=True) -> tuple[str]:
        relative_dir = os.path.dirname(file_path).replace(self.files_in_path, "").lstrip("/").lstrip("\\")
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
