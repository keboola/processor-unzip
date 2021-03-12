'''
Template Component main class.

'''

import glob
import logging
import os
import zipfile
import py7zr
from pathlib import Path

from kbc.env_handler import KBCEnvHandler

# configuration variables
EXTRACT_TO_FOLDER = "extract_to_folder"

# #### Keep for debug
KEY_DEBUG = 'debug'

# list of mandatory parameters => if some is missing, component will fail with readable message on initialization.
MANDATORY_PARS = []
MANDATORY_IMAGE_PARS = []

APP_VERSION = '0.0.1'


def get_files_with_extension(path, extension):
    files = [f for f in glob.glob(path + "/**." + extension, recursive=True)
             if not f.endswith('.manifest') and Path(f).is_file()]
    return files


def get_filename_from_path(path, remove_ext=True):
    if remove_ext:
        return path.split("/")[-1].split(".")[0]
    else:
        return path.split("/")[-1]


class Component(KBCEnvHandler):

    def __init__(self, debug=False):
        # for easier local project setup
        default_data_dir = Path(__file__).resolve().parent.parent.joinpath('data').as_posix() \
            if not os.environ.get('KBC_DATADIR') else None

        KBCEnvHandler.__init__(self, MANDATORY_PARS, log_level=logging.DEBUG if debug else logging.INFO,
                               data_path=default_data_dir)
        # override debug from config
        if self.cfg_params.get(KEY_DEBUG):
            debug = True
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
        logging.info('Running version %s', APP_VERSION)
        logging.info('Loading configuration...')

        try:
            # validation of mandatory parameters. Produces ValueError
            self.validate_config(MANDATORY_PARS)
            self.validate_image_parameters(MANDATORY_IMAGE_PARS)
        except ValueError as e:
            logging.exception(e)
            exit(1)

    def run(self):
        '''
        Main execution code
        '''
        params = self.cfg_params  # noqa

        in_file_path = os.path.join(self.data_path, 'in', 'files')

        files_zip = get_files_with_extension(in_file_path, "zip")
        if len(files_zip) > 0:
            logging.info(f"Extracting {len(files_zip)} .zip files.")
        for file in files_zip:
            with zipfile.ZipFile(file, 'r') as zip_ref:
                out_path = self.get_out_path(file)
                zip_ref.extractall(out_path)

        files_7z = get_files_with_extension(in_file_path, "7z")
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
        if self.cfg_params.get(EXTRACT_TO_FOLDER):
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
