from __future__ import annotations

from pathlib import Path
from datetime import datetime
import shutil


class StorageManager:

    # ---------------------------------------------------------
    # ROOT STORAGE
    # ---------------------------------------------------------

    BASE_DIR = Path("storage")

    QR_DIR = BASE_DIR / "qr"

    LABEL_DIR = BASE_DIR / "labels"

    UPLOAD_DIR = BASE_DIR / "uploads"

    TEMP_DIR = BASE_DIR / "temp"

    # ---------------------------------------------------------
    # INITIALIZE
    # ---------------------------------------------------------

    @classmethod
    def initialize(cls):

        folders = [

            cls.QR_DIR / "media_rolls",
            cls.QR_DIR / "packages",
            cls.QR_DIR / "dispatch",
            cls.QR_DIR / "warehouse",

            cls.LABEL_DIR / "media_rolls",
            cls.LABEL_DIR / "packages",
            cls.LABEL_DIR / "dispatch",

            cls.UPLOAD_DIR,

            cls.TEMP_DIR,

        ]

        for folder in folders:

            folder.mkdir(
                parents=True,
                exist_ok=True,
            )

    # ---------------------------------------------------------
    # FOLDER HELPERS
    # ---------------------------------------------------------

    @classmethod
    def qr_folder(
        cls,
        entity: str,
    ):

        folder = cls.QR_DIR / entity

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder

    @classmethod
    def label_folder(
        cls,
        entity: str,
    ):

        folder = cls.LABEL_DIR / entity

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder

    # ---------------------------------------------------------
    # FILE NAME HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def sanitize_filename(
        filename: str,
    ):

        return (
            filename
            .replace("/", "_")
            .replace("\\", "_")
            .replace(" ", "_")
            .replace(":", "_")
        )

    @classmethod
    def qr_filename(
        cls,
        document_number: str,
    ):

        return f"{cls.sanitize_filename(document_number)}.png"

    @classmethod
    def label_filename(
        cls,
        document_number: str,
    ):

        return f"{cls.sanitize_filename(document_number)}_label.png"

    # ---------------------------------------------------------
    # FULL PATHS
    # ---------------------------------------------------------

    @classmethod
    def qr_path(
        cls,
        entity: str,
        document_number: str,
    ):

        return (
            cls.qr_folder(entity)
            /
            cls.qr_filename(document_number)
        )

    @classmethod
    def label_path(
        cls,
        entity: str,
        document_number: str,
    ):

        return (
            cls.label_folder(entity)
            /
            cls.label_filename(document_number)
        )

    # ---------------------------------------------------------
    # FILE UTILITIES
    # ---------------------------------------------------------

    @staticmethod
    def exists(path):

        return Path(path).exists()

    @staticmethod
    def delete(path):

        path = Path(path)

        if path.exists():

            path.unlink()

    @staticmethod
    def copy(
        source,
        destination,
    ):

        shutil.copy2(
            source,
            destination,
        )

    @staticmethod
    def move(
        source,
        destination,
    ):

        shutil.move(
            source,
            destination,
        )

    @staticmethod
    def timestamp():

        return datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
