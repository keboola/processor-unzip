import gzip
import logging
import os
import pathlib
import re
import shutil

from py7zr import unpack_7zarchive

# TODO: I am thinking of the name of the package/module. Modules is very generic and it may also clash with Python internal naming. I wonder what is the motivation behind it?
# the src/ structure we have is a bit unusual (no root package). In this case it could be either module or package but the naming should reflect it's specific purpose.
# some best practices regarding naming conventions can be found here https://peps.python.org/pep-0423/#id95 or here https://peps.python.org/pep-0008/

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
    # TODO: I would reconsider how FormatRegistration is actually related to the Decompressor?
    """How does the user know that in order to run Decompressor.decompress he needs
       to run the registration for shutil first? It seems tightly coupled with the unpack method, yet it is not linked within the interface.


       I would consider making the register, unregisters steps ideally part of the decompress method, or part of the Decompressor constructor.
       We don't want to force the user to unregister/register. Also to prevent the global impact, the unregister can be in finally block.
       Register called only when needed.

       Another problem arises when a format appears that is not compatible with the shutil wrapper (which probably won't)
       Then the FormatRegistrator becomes completely irrelevant.

       Originally, there was a factory method that would return appropriate Decompress method based on the type to enable extensibility.
       Anyway now this is sorted by the shutil abstraction, that registers the convertor methods.

    """

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
            # TODO: This should throw User exception, otherwise job succeeds but nothing happens
            logging.warning(f"File {self.file_path} cannot be processed: unsupported file type.")

    def _is_supported_filetype(self) -> bool:
        extension = pathlib.Path(self.file_path).suffix
        if extension not in SUPPORTED_FORMATS:
            extensions = pathlib.Path(self.file_path).suffixes[-2:]
            extension = "".join(extensions)
            if extension not in SUPPORTED_FORMATS:
                return False
        return True
