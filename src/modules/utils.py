import logging
import pathlib
from py7zr import unpack_7zarchive
import os
import shutil
import gzip
import re

SUPPORTED_FORMATS = [
    ".7z", ".tar.bz2", ".tbz2", ".gz", ".tar.gz", ".tgz", ".tar", ".tar.xz", ".txz", ".zip"
]


def gunzip(gzipped_file_name, work_dir) -> None:
    """gunzip the given gzipped file"""

    filename = os.path.split(gzipped_file_name)[-1]
    filename = re.sub(r"\.gz$", "", filename, flags=re.IGNORECASE)

    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    with gzip.open(gzipped_file_name, 'rb') as f_in:
        with open(os.path.join(work_dir, filename), 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


class FormatRegistrator:
    def __init__(self):
        pass

    @staticmethod
    def register_formats() -> None:
        """
        Registers unpack formats in shutil.
        """

        shutil.register_unpack_format("7zip",
                                      [".7z"],
                                      unpack_7zarchive,
                                      description="7zip archive")

        shutil.register_unpack_format("gz", [".gz", ], gunzip)

    @staticmethod
    def unregister_formats() -> None:
        """
        Unregisters formats that register_formats method registered.
        This exists for easier test writing because shutil returns RegistryError
        when trying to register already registered format.
        """
        shutil.unregister_unpack_format("7zip")
        shutil.unregister_unpack_format("gz")


class Decompressor:
    def __init__(self, file_path, file_out_path):
        self.file_path = file_path
        self.file_out_path = file_out_path

    def decompress(self) -> None:

        if self._is_supported_filetype():
            shutil.unpack_archive(self.file_path, self.file_out_path)
            # logging.info(f"Processed: {self.file_path}")
        else:
            logging.warning(f"File {self.file_path} cannot be processed: unsupported file type.")

    def _is_supported_filetype(self) -> bool:
        extension = pathlib.Path(self.file_path).suffix
        if extension not in SUPPORTED_FORMATS:
            extensions = pathlib.Path(self.file_path).suffixes[-2:]
            extension = "".join(extensions)
            if extension not in SUPPORTED_FORMATS:
                return False
        return True
