from pathlib import Path

from components.qr_label_generator import QRLabelGenerator

payload = "ADW|MR|123456789"

output = Path(
    "storage/qr/media_rolls/test.png"
)

QRLabelGenerator.generate(
    payload,
    output,
)

print("QR Generated")
print(output)
