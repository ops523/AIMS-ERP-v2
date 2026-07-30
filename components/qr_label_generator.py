from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H


class QRLabelGenerator:

    BOX_SIZE = 10

    BORDER = 4

    ERROR_LEVEL = ERROR_CORRECT_H

    @classmethod
    def generate(
        cls,
        payload: str,
        output_path: str | Path,
    ):

        qr = qrcode.QRCode(

            version=1,

            error_correction=cls.ERROR_LEVEL,

            box_size=cls.BOX_SIZE,

            border=cls.BORDER,

        )

        qr.add_data(payload)

        qr.make(fit=True)

        image = qr.make_image(
            fill_color="black",
            back_color="white",
        )

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        image.save(output_path)

        return str(output_path)
