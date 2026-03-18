import random
import string


def generate_raw_id() -> str:
    """Generate a random string + int of length 13."""
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choices(chars, k=13))


def generate_user_id() -> str:
    """Generate a random int of length 7."""
    return str(random.randint(1000000, 9999999))
