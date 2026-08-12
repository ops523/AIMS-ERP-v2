from services.qr_service import QRService


class FakeMediaRoll:
    def __init__(self, qr_path: str):
        self.qr_image_path = qr_path


def test_qr_artifact_cleanup_deletes_existing_file(tmp_path):
    qr_path = tmp_path / "media-roll-test.png"
    qr_path.write_bytes(b"test-qr")

    QRService.delete_qr_artifact(
        FakeMediaRoll(str(qr_path))
    )

    assert not qr_path.exists()


def test_qr_artifact_cleanup_is_safe_when_file_is_missing(tmp_path):
    qr_path = tmp_path / "missing-qr.png"

    QRService.delete_qr_artifact(
        FakeMediaRoll(str(qr_path))
    )

    assert not qr_path.exists()


def test_qr_artifact_cleanup_is_safe_without_path():
    QRService.delete_qr_artifact(
        FakeMediaRoll("")
    )
