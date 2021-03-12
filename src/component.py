'''
Template Component main class.

'''

import glob
import logging
import os
import zipfile
import py7zr
from pathlib import Path
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


def get_files_with_extension(path, extension):
    files = [f for f in glob.glob(path + "/**." + extension, recursive=True)
             if not f.endswith('.manifest') and Path(f).is_file()]
    return files


def get_filename_from_path(path, remove_ext=True):
    if remove_ext:
        return path.split("/")[-1].split(".")[0]
    else:
        return path.split("/")[-1]


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

    @staticmethod
    def set_debug_mode():
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info('Running version %s', APP_VERSION)
        logging.info('Loading configuration...')

    def run(self):
        '''
        Main execution code
        '''

        files_zip = get_files_with_extension(self.files_in_path, "zip")
        if len(files_zip) > 0:
            logging.info(f"Extracting {len(files_zip)} .zip files.")
        for file in files_zip:
            with zipfile.ZipFile(file, 'r') as zip_ref:
                out_path = self.get_out_path(file)
                zip_ref.extractall(out_path)

        files_7z = get_files_with_extension(self.files_in_path, "7z")
        if len(files_7z) > 0:
            logging.info(f"Extracting {len(files_7z)} .7z files.")
        for file in files_7z:
            out_path = self.get_out_path(file)
            archive = py7zr.SevenZipFile(file, mode='r')
            archive.extractall(path=out_path)
            archive.close()

        logging.info("Extraction finished.")

    def get_out_path(self, filepath):
        out_path = self.files_out_path
        if self.configuration.parameters.get(EXTRACT_TO_FOLDER):
            out_path = os.path.join(self.files_out_path, get_filename_from_path(filepath))
        return out_path


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
