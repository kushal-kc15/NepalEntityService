"""Configuration for Nepal Entity Service v2."""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration class for nes2."""

    # Default database path for v2
    DEFAULT_DB_PATH = "nes-db/v2"

    @classmethod
    def get_db_path(cls, override_path: Optional[str] = None) -> Path:
        """Get the database path.

        Args:
            override_path: Optional path to override the default database path

        Returns:
            Path object for the database directory
        """
        if override_path:
            return Path(override_path)

        # Check for environment variable
        env_path = os.getenv("NES2_DB_PATH")
        if env_path:
            return Path(env_path)

        # Use default path
        return Path(cls.DEFAULT_DB_PATH)

    @classmethod
    def ensure_db_path_exists(cls, db_path: Optional[Path] = None) -> Path:
        """Ensure the database path exists, creating it if necessary.

        Args:
            db_path: Optional database path, uses default if not provided

        Returns:
            Path object for the database directory
        """
        if db_path is None:
            db_path = cls.get_db_path()

        db_path.mkdir(parents=True, exist_ok=True)
        return db_path


# Global configuration instance
config = Config()
