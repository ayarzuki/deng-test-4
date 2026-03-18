from app.utils import generate_raw_id, generate_user_id


class TestGenerateRawId:
    def test_length_is_13(self):
        raw_id = generate_raw_id()
        assert len(raw_id) == 13

    def test_contains_only_lowercase_and_digits(self):
        raw_id = generate_raw_id()
        assert raw_id.isalnum()
        assert raw_id == raw_id.lower()

    def test_generates_unique_values(self):
        ids = {generate_raw_id() for _ in range(100)}
        assert len(ids) > 90  # statistically should be unique


class TestGenerateUserId:
    def test_length_is_7(self):
        user_id = generate_user_id()
        assert len(user_id) == 7

    def test_is_numeric(self):
        user_id = generate_user_id()
        assert user_id.isdigit()

    def test_within_range(self):
        user_id = generate_user_id()
        assert 1000000 <= int(user_id) <= 9999999

    def test_generates_unique_values(self):
        ids = {generate_user_id() for _ in range(100)}
        assert len(ids) > 90
