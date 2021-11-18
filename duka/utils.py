"""Collection of utils functions."""
import secrets
import string

chars_string = string.ascii_lowercase + string.digits + string.ascii_uppercase


def random_string(
    *,
    size: int = 11,
    chars: str = chars_string,
) -> str:
    """Generate random string.

    Args:
        size: Size of the random sting.
        chars: A sting of chars to use.

    Returns:
        Random string.

    """
    return "".join(secrets.choice(chars) for _ in range(size))
