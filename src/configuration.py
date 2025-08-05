import logging

from pydantic import BaseModel, Field, ValidationError, field_validator


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
    zlib_window_size: int = Field(title="Zlib window size", default=None)

    @field_validator("zlib_window_size")
    def validate_zlib_window_size(cls, v):
        if v == 0:
            return v  # 0 is valid (automatic detection)
        if -15 <= v <= -8:
            return v  # Raw deflate format
        if 8 <= v <= 15:
            return v  # Standard zlib format
        raise ValueError("zlib_window_size must be 0, or in range -15 to -8 (raw deflate), or 8 to 15 (standard zlib)")
