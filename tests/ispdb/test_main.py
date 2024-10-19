from io import StringIO
from typing import Iterable

from ispdb.main import main
from ispdb.lookups import Lookup


def test_no_lookups() -> None:
    def _pipeline(email: str, protocols: list[str]) -> Iterable[Lookup]:
        assert email == "test@testable.com"
        assert protocols == ["https", "http", "dns"]

        if False:
            yield Lookup()  # type: ignore

    res = main(["test@testable.com"], pipeline=_pipeline)
    assert res == 0


def test_lookup_with_exception() -> None:
    def _pipeline(email: str, protocols: list[str]) -> Iterable[Lookup]:
        if False:
            yield Lookup()  # type: ignore
        raise ValueError

    res = main(["test@testable.com"], pipeline=_pipeline)
    assert res == 1


def test_lookups_success() -> None:
    def _pipeline(email: str, protocols: list[str]) -> Iterable[Lookup]:
        assert email == "test@testable.com"
        assert protocols == ["https", "http", "dns"]

        class TLookup(Lookup):
            def protocol(self) -> str:
                return "p"

            def query(self) -> str:
                return "text"

        yield TLookup()

    stdout = StringIO()
    res = main(["test@testable.com"], stdout=stdout, pipeline=_pipeline)
    assert res == 0
    assert stdout.getvalue() == "text\n"
