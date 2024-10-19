"""
Query order:
1 GET autoconfig.example.com
2 GET https://autoconfig.example.com/mail/config-v1.1.xml?emailaddress=fred@example.com
3 GET https://example.com/.well-known/autoconfig/mail/config-v1.1.xml
4 GET http://autoconfig.example.com/mail/config-v1.1.xml?emailaddress=fred@example.com
5 GET http://example.com/.well-known/autoconfig/mail/config-v1.1.xml
6 GET https://autoconfig.thunderbird.net/v1.1/example.com
7 DNS "MX example.com", extract domain and perform this process again
"""

import argparse
import logging

import dns.name
import dns.resolver
import requests

from dns.rdtypes.ANY.MX import MX
from typing import Iterable
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

_REQUESTS_TIMEOUT = 1


_PROTOCOLS = ["https", "http", "dns"]


def protocols(params: argparse.Namespace) -> list[str]:
    protocols = list(_PROTOCOLS)
    if params.no_https:
        protocols.remove("https")
    if params.no_http:
        protocols.remove("http")
    if params.no_dns:
        protocols.remove("dns")
    return protocols


def pipeline(
    email: str,
    protocols: list[str],
    domain: str = "",
) -> Iterable["Lookup"]:
    if not domain:
        _, domain = email.rsplit("@", 1)

    urls = [
        f"https://autoconfig.{domain}",
        f"https://autoconfig.{domain}/mail/config-v1.1.xml?emailaddress={email}",
        f"https://{domain}/.well-known/autoconfig/mail/config-v1.1.xml",
        f"http://autoconfig.{domain}/mail/config-v1.1.xml?emailaddress={email}",
        f"http://{domain}/.well-known/autoconfig/mail/config-v1.1.xml",
        f"https://autoconfig.thunderbird.net/v1.1/{domain}",
    ]
    for url in urls:
        lookup: Lookup = URLLookup(url)
        if lookup.protocol() in protocols:
            yield lookup
    lookup = DNSLookup(email, domain)
    if lookup.protocol() in protocols:
        yield lookup


class Lookup:
    def protocol(self) -> str:
        raise NotImplementedError

    def query(self) -> str:
        raise NotImplementedError


class URLLookup(Lookup):
    def __init__(self, url: str) -> None:
        up = urlparse(url)
        self.scheme = up.scheme
        self.hostname = up.hostname
        self.url = url

    def protocol(self) -> str:
        return self.scheme

    def query(self) -> str:
        try:
            r = requests.get(self.url, timeout=_REQUESTS_TIMEOUT)
            if r.status_code == requests.codes.ok:
                logger.debug(f"[{self.scheme}] {self.hostname}: OK for {self.url}")
                if r.text and "<clientConfig " in r.text:
                    return r.text
                else:
                    logger.debug(
                        f"[{self.scheme}] {self.hostname}: ERROR[no XML] for {self.url}"
                    )
            else:
                logger.debug(
                    f"[{self.scheme}] {self.hostname}: ERROR[{r.status_code}] for {self.url}"
                )

        except requests.exceptions.RequestException:
            logger.debug(f"[{self.scheme}] {self.hostname}: ERROR for {self.url}")

        return ""


class DNSLookup(Lookup):
    def __init__(self, email: str, domain: str) -> None:
        self.email = email
        self.domain = domain

    def protocol(self) -> str:
        return "dns"

    def _resolve_dns(self) -> Iterable[MX]:
        for record in dns.resolver.resolve(self.domain, "MX"):
            assert isinstance(record, MX)
            yield record

    def _hosts(self) -> Iterable[str]:
        cached: list[dns.name.Name] = []
        for record in self._resolve_dns():
            host = record.exchange
            try:
                while True:
                    host = host.parent()
                    if host in cached:
                        break
                    cached.append(host)
                    hostname = host.to_text(omit_final_dot=True)
                    if "." not in hostname:
                        # we don't want to query email setup for top level domains
                        break
                    yield hostname
            except dns.name.NoParent:
                pass

    def _protocols(self) -> list[str]:
        return [p for p in _PROTOCOLS if p != "dns"]

    def query(self) -> str:
        protocols = self._protocols()
        for host in self._hosts():
            logger.debug(f"[dns] {self.domain}: Verifying {host} as mail domain")
            for lookup in pipeline(self.email, domain=host, protocols=protocols):
                res = lookup.query()
                if res:
                    return res
        return ""
