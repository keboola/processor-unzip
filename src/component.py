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

        files_7z = get_files_with_extension(in_file_path, "7z")
        files_zip = get_files_with_extension(in_file_path, "zip")

        if len(files_zip) > 0:
            logging.info(f"Extracting {len(files_zip)} .zip files.")

        if len(files_7z) > 0:
            logging.info(f"Extracting {len(files_7z)} .7z files.")

        for file in files_7z:
            archive = py7zr.SevenZipFile(file, mode='r')
            archive.extractall(path=self.files_out_path)
            archive.close()

        for f in files_zip:
            with zipfile.ZipFile(f, 'r') as zip_ref:
                # zipinfo.filename = do_something_to(zipinfo.filename
                zip_ref.extractall(self.files_out_path)

        logging.info("Extraction finished.")


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
