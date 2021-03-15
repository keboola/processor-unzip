import glob
import zipfile
import py7zr
import os
from pathlib import Path


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
