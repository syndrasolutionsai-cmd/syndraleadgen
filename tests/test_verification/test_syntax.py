from leadforge.verification.syntax import check_syntax, is_role_based


def test_valid_email_passes():
    assert check_syntax("john@acme.com") is True


def test_invalid_format_fails():
    assert check_syntax("not-an-email") is False
    assert check_syntax("@nodomain.com") is False
    assert check_syntax("noatsign.com") is False


def test_role_based_detected():
    assert is_role_based("info@acme.com") is True
    assert is_role_based("support@acme.com") is True
    assert is_role_based("hello@acme.com") is True
    assert is_role_based("contact@acme.com") is True


def test_personal_email_not_role_based():
    assert is_role_based("john.smith@acme.com") is False
    assert is_role_based("jsmith@acme.com") is False
