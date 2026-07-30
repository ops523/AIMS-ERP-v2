from __future__ import annotations

from pathlib import Path
from datetime import datetime
import shutil


class StorageManager:

    BASE_DIR = Path("storage")

    QR_DIR = BASE_DIR / "qr"

    LABEL_DIR = BASE_DIR / "labels"

    UPLOAD_DIR = BASE_DIR / "uploads"

    TEMP_DIR = BASE_DIR / "temp"

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

    @classmethod
    def qr_folder(
        cls,
        entity: str,
    ) -> Path:

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
    ) -> Path:

        folder = cls.LABEL_DIR / entity

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder

    @classmethod
    def build_qr_filename(
        cls,
        document_number: str,
    ) -> str:

        safe = (
            document_number
            .replace("/", "_")
            .replace("\\", "_")
            .replace(" ", "_")
        )

        return f"{safe}.png"

    @classmethod
    def build_label_filename(
        cls,
        document_number: str,
    ) -> str:

        safe = (
            document_number
            .replace("/", "_")
            .replace("\\", "_")
            .replace(" ", "_")
        )

        return f"{safe}_label.png"

    @classmethod
    def qr_path(
        cls,
        entity: str,
        document_number: str,
    ) -> Path:

        return (
            cls.qr_folder(entity)
            / cls.build_qr_filename(document_number)
        )

    @classmethod
    def label_path(
        cls,
        entity: str,
        document_number: str,
    ) -> Path:

        return (
            cls.label_folder(entity)
            / cls.build_label_filename(document_number)
        )

    @classmethod
    def delete_file(
        cls,
        path: str | Path,
    ):

        path = Path(path)

        if path.exists():

            path.unlink()

    @classmethod
    def copy_file(
        cls,
        source: str | Path,
        destination: str | Path,
    ):

        shutil.copy2(source, destination)

    @classmethod
    def timestamp():

        return datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )
