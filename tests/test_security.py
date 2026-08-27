from utils.security import (
    hash_password,
    verify_password,
)


def test_password_hash_is_not_plaintext():
    password = "TestPassword123!"

    password_hash = hash_password(password)

    assert password_hash != password
    assert password_hash.startswith("$argon2id$")


def test_correct_password_verifies():
    password = "TestPassword123!"

    password_hash = hash_password(password)

    assert verify_password(
        password,
        password_hash,
    ) is True


def test_wrong_password_does_not_verify():
    password_hash = hash_password(
        "TestPassword123!"
    )

    assert verify_password(
        "WrongPassword123!",
        password_hash,
    ) is False


def test_empty_password_is_rejected():
    try:
        hash_password("")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_invalid_hash_returns_false():
    assert verify_password(
        "TestPassword123!",
        "not-a-valid-password-hash",
    ) is False


def test_password_hashes_are_unique():
    password = "TestPassword123!"

    hash_1 = hash_password(password)
    hash_2 = hash_password(password)

    assert hash_1 != hash_2

    assert verify_password(password, hash_1)
    assert verify_password(password, hash_2)