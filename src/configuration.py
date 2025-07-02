import logging

from pydantic import BaseModel, Field, ValidationError


class ConfigurationException(Exception):
    pass


class Configuration(BaseModel):
    debug: bool = Field(title="Debug mode", default=False)

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise ConfigurationException(f"Validation Error: {', '.join(error_messages)}")

        if self.debug:
            logging.debug("Component will run in Debug mode")


class UnzipConfiguration(Configuration):
    extract_to_folder: bool = Field(title="Extract to folder", default=False)
    password_7z: str = Field(title="7z Password", default=None)


class DecompressConfiguration(Configuration):
    graceful: bool = Field(title="Graceful mode", default=False)
    compression_type: str = Field(title="Compression type", default=None)
    zlib_window_size: int = Field(title="Zlib window size", default=15, ge=8, le=15)
