'''
Template Component main class.

'''

import glob
import logging
import os
import sys
import zipfile
from pathlib import Path

from kbc.env_handler import KBCEnvHandler

# configuration variables


# #### Keep for debug
KEY_DEBUG = 'debug'

# list of mandatory parameters => if some is missing, component will fail with readable message on initialization.
MANDATORY_PARS = []
MANDATORY_IMAGE_PARS = []

APP_VERSION = '0.0.1'


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
        # ####### EXAMPLE TO REMOVE
        # intialize instance parameteres

        # ####### EXAMPLE TO REMOVE END

    def run(self):
        '''
        Main execution code
        '''
        params = self.cfg_params  # noqa

        params = self.cfg_params  # noqa
        files = [f for f in glob.glob(os.path.join(self.data_path, 'in', 'files') + "/**.zip", recursive=True)
                 if not f.endswith('.manifest') and Path(f).is_file()]
        logging.info(f"Extracting {len(files)} files.")
        for f in files:
            with zipfile.ZipFile(f, 'r') as zip_ref:
                zip_ref.extractall(self.files_out_path)
        logging.info("Extraction finished.")


"""
        Main entrypoint
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        debug_arg = sys.argv[1]
    else:
        debug_arg = False
    try:
        comp = Component(debug_arg)
        comp.run()
    except Exception as exc:
        logging.exception(exc)
        exit(1)
