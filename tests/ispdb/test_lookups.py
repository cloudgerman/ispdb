import requests
import requests_mock

from dns.rdtypes.ANY.MX import MX
from ispdb import args, lookups
from pytest_mock import MockerFixture


def test_protocol_exclussion() -> None:
    params = args.parse(["test@testable.com"])
    assert lookups.protocols(params) == lookups._PROTOCOLS

    for protocol in lookups._PROTOCOLS:
        params = args.parse([f"--no-{protocol}", "test@testable.com"])
        assert lookups.protocols(params) == [
            p for p in lookups._PROTOCOLS if p != protocol
        ]


def test_https_returns_xml() -> None:
    params = args.parse(["--no-http", "--no-dns", "test@testable.com"])
    prot = lookups.protocols(params)

    for lookup in lookups.pipeline(params.email, prot):
        assert lookup.protocol() == "https"

        assert isinstance(lookup, lookups.URLLookup)
        with requests_mock.Mocker() as m:
            m.get(lookup.url, text="<clientConfig />")
            assert lookup.query() == "<clientConfig />"
        break


def test_https_doesn_not_return_xml() -> None:
    params = args.parse(["--no-http", "--no-dns", "test@testable.com"])
    prot = lookups.protocols(params)

    for lookup in lookups.pipeline(params.email, prot):
        assert lookup.protocol() == "https"

        assert isinstance(lookup, lookups.URLLookup)
        with requests_mock.Mocker() as m:
            m.get(lookup.url, text="text")
            assert not lookup.query()
        break


def test_https_404() -> None:
    params = args.parse(["--no-http", "--no-dns", "test@testable.com"])
    prot = lookups.protocols(params)

    for lookup in lookups.pipeline(params.email, prot):
        assert lookup.protocol() == "https"

        assert isinstance(lookup, lookups.URLLookup)
        with requests_mock.Mocker() as m:
            m.get(lookup.url, status_code=404)
            assert not lookup.query()
        break


def test_https_connection_timeout() -> None:
    params = args.parse(["--no-http", "--no-dns", "test@testable.com"])
    prot = lookups.protocols(params)

    for lookup in lookups.pipeline(params.email, prot):
        assert lookup.protocol() == "https"

        assert isinstance(lookup, lookups.URLLookup)
        with requests_mock.Mocker() as m:
            m.get(lookup.url, exc=requests.exceptions.ConnectTimeout)
            assert not lookup.query()
        break


def test_dns_with_empty_response(mocker: MockerFixture) -> None:
    _hosts = mocker.patch("ispdb.lookups.DNSLookup._hosts")
    _hosts.return_value = []

    params = args.parse(["--no-http", "--no-https", "test@testable.com"])
    prot = lookups.protocols(params)

    for lookup in lookups.pipeline(params.email, prot):
        assert lookup.protocol() == "dns"
        assert isinstance(lookup, lookups.DNSLookup)
        res = lookup.query()
        assert not res, res


def test_dns_with_1_hostname(mocker: MockerFixture) -> None:
    _hosts = mocker.patch("dns.resolver.resolve")
    _hosts.return_value = [MX(255, 255, 10, "mail.testable.com.")]  # type: ignore

    params = args.parse(["--no-http", "--no-https", "test@testable.com"])
    prot = lookups.protocols(params)

    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, text="<clientConfig />")
        for lookup in lookups.pipeline(params.email, prot):
            assert lookup.protocol() == "dns"
            assert isinstance(lookup, lookups.DNSLookup)
            res = lookup.query()
            assert res == "<clientConfig />"
