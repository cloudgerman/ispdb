import pytest

from ispdb import args


def test_valid_args() -> None:
    argv = ["email@testable.com"]
    params = args.parse(argv)
    assert params.email == "email@testable.com"
    assert not params.silent
    assert not params.debug
    assert not params.no_https
    assert not params.no_http
    assert not params.no_dns


def test_no_args() -> None:
    with pytest.raises(SystemExit):
        args.parse([])


def test_incompatible_args() -> None:
    argv = ["-s", "-d", "email@testable.com"]
    with pytest.raises(SystemExit):
        args.parse(argv)


def test_not_an_email() -> None:
    for txt in ("email_testable.com", "@testable.com", "email@"):
        with pytest.raises(SystemExit):
            args.parse([txt])
