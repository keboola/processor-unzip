import os
import pathlib
import re
import shutil
import gzip
import zlib

from keboola.component import UserException
from py7zr import SevenZipFile

SUPPORTED_FORMATS = [".7z", ".tar.bz2", ".tbz2", ".gz", ".zlib", ".tar.gz", ".tgz", ".tar", ".tar.xz", ".txz", ".zip"]


def gunzip(gz_file_path, extract_dir) -> None:
    """gunzip the given gzipped file"""

    base_filename = os.path.split(gz_file_path)[-1]
    out_filename = re.sub(r"\.gz$", "", base_filename, flags=re.IGNORECASE)

    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    with gzip.open(gz_file_path, "rb") as f_in:
        with open(os.path.join(extract_dir, out_filename), "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


def unpack_7zarchive(archive_path: str, extract_dir: str, password: str = None) -> None:
    os.makedirs(extract_dir, exist_ok=True)
    with SevenZipFile(archive_path, mode="r", password=password) as archive:
        archive.extractall(path=extract_dir)


def unpack_zlib(zlib_file_path, extract_dir) -> None:
    base_filename = os.path.split(zlib_file_path)[-1]
    out_filename = re.sub(r"\.zlib$", "", base_filename, flags=re.IGNORECASE)

    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    out_path = os.path.join(extract_dir, out_filename)

    with open(zlib_file_path, "rb") as f_in, open(out_path, "wb") as f_out:
        compressed_data = f_in.read()
        try:
            decompressed_data = zlib.decompress(compressed_data, wbits=zlib.MAX_WBITS)
        except zlib.error as e:
            raise UserException(f"Zlib decompression failed: {e}")
        f_out.write(decompressed_data)


class Decompressor:
    def __init__(self, password: str = None):
        self.password = password

        # Use a single function with optional password parameter
        shutil.register_unpack_format(
            "7zip",
            [".7z"],
            lambda filepath, extract_dir: unpack_7zarchive(filepath, extract_dir, self.password),
            description="7zip archive",
        )

        shutil.register_unpack_format("gz", [".gz"], gunzip)
        shutil.register_unpack_format("zlib", [".zlib"], unpack_zlib)

    def run_decompressor(self, file_path, file_out_path) -> None:
        """
        If the file in file_path is of supported type, unzips the file into file_out_path.
        Args:
            file_path: Path of the file to unzip.
            file_out_path: Path where file/files will be unzipped to.

        Returns:
            None
        """

        if self._is_supported_filetype(file_path):
            try:
                shutil.unpack_archive(file_path, file_out_path)
            except Exception as e:
                raise UserException(f"File {file_path} cannot be processed: {str(e)}")
        else:
            raise Exception(f"File {file_path} cannot be processed: unsupported file type.")

    @staticmethod
    def _is_supported_filetype(file_path) -> bool:
        """
        Returns True/False based on filetypes defined in SUPPORTED_FORMATS.
        Args:
            file_path: Path of the file to unzip.

        Returns:
            bool

        """
        extension = pathlib.Path(file_path).suffix
        if extension not in SUPPORTED_FORMATS:
            extensions = pathlib.Path(file_path).suffixes[-2:]
            extension = "".join(extensions)
            if extension not in SUPPORTED_FORMATS:
                return False
        return True

    @staticmethod
    def unregister_formats() -> None:
        """
        Unregisters formats that register_formats method registered.
        This exists for easier test writing because shutil returns RegistryError
        when trying to register already registered format.
        """
        shutil.unregister_unpack_format("7zip")
        shutil.unregister_unpack_format("gz")
        shutil.unregister_unpack_format("zlib")
