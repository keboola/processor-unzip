'''
Template Component main class.

'''

import logging
import os
import glob
import decompressor as dc
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

    def get_out_path(self, filepath):
        out_path = self.files_out_path
        if self.configuration.parameters.get(EXTRACT_TO_FOLDER):
            out_path = os.path.join(self.files_out_path, get_filename_from_path(filepath))
        return out_path

    @staticmethod
    def set_debug_mode():
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info('Running version %s', APP_VERSION)
        logging.info('Loading configuration...')

    def run(self):
        '''
        Main execution code
        '''

        logging.info("Extraction starting.")

        in_files = _get_in_files(self.files_in_path)

        for file in in_files:
            file_out_path = self.get_out_path(file)
            file_decompressor = dc.Decompressor(file, file_out_path)
            file_decompressor.decompress()

        logging.info("Extraction finished.")


def _get_in_files(path):
    return glob.glob(os.path.join(path, '*'))


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
