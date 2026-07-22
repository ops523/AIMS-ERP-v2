from pathlib import Path

import qrcode


QR_FOLDER = Path("qr")

QR_FOLDER.mkdir(exist_ok=True)


class QRService:

    @staticmethod
    def generate(asset_id: str):

        filename = QR_FOLDER / f"{asset_id}.png"

        img = qrcode.make(asset_id)

        img.save(filename)

        return str(filename)
