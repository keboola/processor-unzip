import os
import re
import shutil
import gzip
import zlib
import logging

from keboola.component import UserException
from py7zr import SevenZipFile

SUPPORTED_FORMATS = [
    ".zip",
    ".7z",
    ".gz",
    ".tar",
    ".tar.bz2",
    ".tar.gz",
    ".tar.xz",
    ".tbz2",
    ".tgz",
    ".txz",
    ".zlib",
]


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


def unpack_zlib(zlib_file_path, extract_dir, zlib_window_size: None) -> None:
    base_filename = os.path.split(zlib_file_path)[-1]
    out_filename = re.sub(r"\.zlib$", "", base_filename, flags=re.IGNORECASE)

    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    out_path = os.path.join(extract_dir, out_filename)

    with open(zlib_file_path, "rb") as f_in, open(out_path, "wb") as f_out:
        compressed_data = f_in.read()
        try:
            wbits = zlib_window_size if zlib_window_size else zlib.MAX_WBITS
            decompressed_data = zlib.decompress(compressed_data, wbits=wbits)
        except zlib.error as e:
            raise UserException(f"Zlib decompression failed: {e}")
        f_out.write(decompressed_data)


class Decompressor:
    def __init__(self, **kwargs):
        self.password = kwargs.get("password")
        self.graceful = kwargs.get("graceful")
        self.zlib_window_size = kwargs.get("zlib_window_size")
        self.is_unzip = kwargs.get("is_unzip")

        # Safely register formats - handle already registered formats
        try:
            shutil.register_unpack_format(
                "7zip",
                [".7z"],
                lambda filepath, extract_dir: unpack_7zarchive(filepath, extract_dir, self.password),
                description="7zip archive",
            )
        except shutil.RegistryError:
            # Format already registered, that's fine
            pass

        try:
            shutil.register_unpack_format("gz", [".gz"], lambda filepath, extract_dir: gunzip(filepath, extract_dir))
        except shutil.RegistryError:
            pass

        try:
            shutil.register_unpack_format(
                "zlib",
                [".zlib"],
                lambda filepath, extract_dir: unpack_zlib(filepath, extract_dir, self.zlib_window_size),
            )
        except shutil.RegistryError:
            pass

    def run_decompressor(self, file_path: str, file_out_path: str, compression_type: str = None) -> None:
        """
        If the file in file_path is of supported type, unzips the file into file_out_path.
        Args:
            file_path: Path of the file to unzip.
            file_out_path: Path where file/files will be unzipped to.

        Returns:
            None
        """
        has_supported_format = any(file_path.endswith(ext) for ext in SUPPORTED_FORMATS)

        if has_supported_format or compression_type:
            try:
                shutil.unpack_archive(file_path, file_out_path)

            except Exception as e:
                if self.graceful is not None:
                    if self.graceful:
                        logging.warning(f"Unpacking of {file_path} ended with error: {e} \nContinuing...")
                    else:
                        raise UserException(
                            f"Unpacking of {file_path} ended with error: {e} "
                            "\nIf you want to continue with processors run on failure, "
                            "set the 'graceful' parameter to true."
                        )
                else:
                    raise UserException(
                        f"Unpacking of {file_path} ended with error: {e} "
                        "\nIf you want to continue with processors run on failure, "
                        "set the 'graceful' parameter to true."
                    )

        else:
            if self.graceful is not None:
                if self.graceful:
                    logging.warning(
                        f"Unsupported file format for file {file_path}. Supported formats are: {SUPPORTED_FORMATS}"
                        "\nSkipping..."
                    )
                else:
                    raise UserException(
                        f"Unsupported file format for file {file_path}. Supported formats are: {SUPPORTED_FORMATS}"
                        "\nIf you want to skip unsupported files, set the 'graceful' parameter to true."
                    )
            else:
                if self.is_unzip:
                    logging.warning(
                        f"Unsupported file format for file {file_path}. Supported formats are: {SUPPORTED_FORMATS}"
                        "\nSkipping..."
                    )
                else:
                    raise UserException(
                        f"Unsupported file format for file {file_path}. Supported formats are: {SUPPORTED_FORMATS}"
                        "\nIf you want to skip unsupported files, set the 'graceful' parameter to true."
                    )

    @staticmethod
    def unregister_formats() -> None:
        """
        Unregisters formats that register_formats method registered.
        This exists for easier test writing because shutil returns RegistryError
        when trying to register already registered format.
        """
        try:
            shutil.unregister_unpack_format("7zip")
        except KeyError:
            pass  # Format not registered, that's fine

        try:
            shutil.unregister_unpack_format("gz")
        except KeyError:
            pass

        try:
            shutil.unregister_unpack_format("zlib")
        except KeyError:
            pass
