import logging
import glob
import os

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

from decompress import Decompressor
from configuration import UnzipConfiguration, DecompressConfiguration


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

        # Set parameters based on component ID (kds-team.processor-unzip/keboola.processor-decompress)
        if self.environment_variables.get("KBC_COMPONENTID") == "kds-team.processor-unzip":
            self.params = UnzipConfiguration(**self.configuration.parameters)

            # Indicator for decompress class
            is_unzip = True

            # Parameters for unzip processor
            password = self.params.password_7z if hasattr(self.params, "password_7z") else None
            to_folder = self.params.extract_to_folder if hasattr(self.params, "extract_to_folder") else False

            # Initialize parameters that are not used in unzip processor
            graceful = None
            compression_type = None
            zlib_window_size = None

            # Varibles for enabling default unzip behavior
            remove_ext = True

        else:
            self.params = DecompressConfiguration(**self.configuration.parameters)

            is_unzip = False

            # Parameters for decompress processor
            graceful = self.params.graceful if hasattr(self.params, "graceful") else False
            compression_type = self.params.compression_type if hasattr(self.params, "compression_type") else None
            zlib_window_size = self.params.zlib_window_size if hasattr(self.params, "zlib_window_size") else 15

            # Initialize parameters that are not used in decompress processor
            password = None
            to_folder = True

            # Varibles for enabling default decompress behavior
            remove_ext = False

        logging.info("Extraction starting.")

        d = Decompressor(password=password, graceful=graceful, zlib_window_size=zlib_window_size, is_unzip=is_unzip)
        try:
            for file in self._get_in_files():
                file_out_path = self._get_out_path(file, to_folder, remove_ext)
                d.run_decompressor(file, file_out_path, compression_type)
        finally:
            # Unregistering formats is here for easier tests writing.
            d.unregister_formats()

        logging.info("Extraction done.")

    def _get_in_files(self) -> list:
        files = glob.glob(os.path.join(self.files_in_path, "**/*"), recursive=True)
        return [f for f in files if not os.path.isdir(f)]

    def _get_out_path(self, filepath, to_folder, remove_ext) -> str:
        filename, relative_dir = self._get_filename_from_path(filepath, remove_ext)
        out_path = os.path.join(self.files_out_path, relative_dir)
        if to_folder:
            out_path = os.path.join(self.files_out_path, relative_dir, filename)
        return out_path

    def _get_filename_from_path(self, file_path, remove_ext) -> tuple[str]:
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
