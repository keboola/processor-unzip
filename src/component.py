'''
Template Component main class.

'''

import glob
import logging
import os
import zipfile
from pathlib import Path

import py7zr
from keboola.component import CommonInterface

# configuration variables
EXTRACT_TO_FOLDER = "extract_to_folder"

# #### Keep for debug
KEY_DEBUG = 'debug'

# list of mandatory parameters => if some is missing, component will fail with readable message on initialization.
REQUIRED_PARAMETERS = []
REQUIRED_IMAGE_PARS = []

APP_VERSION = '0.0.1'


def get_local_data_path():
    return Path(__file__).resolve().parent.parent.joinpath('data').as_posix()


def get_data_folder_path():
    data_folder_path = None
    if not os.environ.get('KBC_DATADIR'):
        data_folder_path = get_local_data_path()
    return data_folder_path


class Component(CommonInterface):
    def __init__(self):
        # for easier local project setup
        data_folder_path = get_data_folder_path()
        super().__init__(data_folder_path=data_folder_path)
        try:
            # validation of required parameters. Produces ValueError
            self.validate_configuration(REQUIRED_PARAMETERS)
            self.validate_image_parameters(REQUIRED_IMAGE_PARS)
        except ValueError as e:
            logging.exception(e)
            exit(1)

        if self.configuration.parameters.get(KEY_DEBUG):
            self.set_debug_mode()

    def run(self):
        '''
        Main execution code
        '''

        logging.info("Extraction starting.")

        in_files = self._get_in_files()

        for file in in_files:
            file_out_path = self.get_out_path(file)
            file_decompressor = Decompressor(file, file_out_path)
            file_decompressor.decompress()

        logging.info("Extraction finished.")

    def get_out_path(self, filepath):
        filename, relative_dir = self.get_filename_from_path(filepath)
        out_path = os.path.join(self.files_out_path, relative_dir)
        if self.configuration.parameters.get(EXTRACT_TO_FOLDER):
            out_path = os.path.join(self.files_out_path, relative_dir, filename)
        return out_path

    def get_filename_from_path(self, file_path, remove_ext=True):
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

    def _get_in_files(self):
        files = glob.glob(os.path.join(self.files_in_path, "**/*"), recursive=True)
        return [f for f in files if not os.path.isdir(f)]

    def set_debug_mode(self):
        logging.getLogger().setLevel(logging.DEBUG)


class Decompressor:
    def __init__(self, file_path, file_out_path):
        self.file_path = file_path
        self.file_out_path = file_out_path

    def decompress(self):
        file_type = self._get_file_type()
        decompressor = _get_decompressor(file_type)
        if decompressor:
            decompressor(self.file_path, self.file_out_path)

    def _get_file_type(self):
        extension = os.path.splitext(self.file_path)[1]
        return extension


def _get_decompressor(file_type):
    if file_type == ".7z":
        return _decompress_7z

    elif file_type == ".zip":
        return _decompress_zip


def _decompress_7z(file, file_outpath):
    archive = py7zr.SevenZipFile(file, mode='r')
    archive.extractall(path=file_outpath)
    archive.close()


def _decompress_zip(file, file_outpath):
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(file_outpath)


"""
        Main entrypoint
"""
if __name__ == "__main__":
    try:
        comp = Component()
        comp.run()
    except Exception as exc:
        logging.exception(exc)
        exit(1)
