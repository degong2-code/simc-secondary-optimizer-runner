#!/usr/bin/env python3
"""Fetch ONE build-pinned SpellItemEnchantment CSV; v217 seals it.

A separate source extension: never alter v161's historical 10-table snapshot,
and do not download the other DB2 tables. Only the exact-build Wago CSV.
"""
from __future__ import annotations
from urllib.parse import urlencode
from urllib.request import Request,urlopen
import re

TABLE = "SpellItemEnchantment"
MAX_BYTES = 32_000_000
BUILD = re.compile(r"[0-9]+(?:\.[0-9]+){3}\Z")


class GemEnchantFetchBlocked(ValueError):
    pass


def fetch(*,build,transport=urlopen):
    if not isinstance(build,str) or BUILD.fullmatch(build) is None:
        raise GemEnchantFetchBlocked("V267_EXPLICIT_GAME_BUILD_REQUIRED")
    url="https://wago.tools/db2/"+TABLE+"/csv?"+urlencode({
        "build":build,"locale":"enUS"})
    request=Request(url,headers={
        "User-Agent":"SIMC-Secondary-v267-single-enchant-source/1.0",
        "Accept":"text/csv"})
    try:
        with transport(request,timeout=90) as response:
            if response.status!=200:
                raise GemEnchantFetchBlocked("V267_ENCHANT_CSV_HTTP_NON200")
            data=response.read(MAX_BYTES+1)
    except (OSError,TimeoutError) as exc:
        raise GemEnchantFetchBlocked(
            "V267_ENCHANT_CSV_NETWORK_UNAVAILABLE") from exc
    if not (0<len(data)<=MAX_BYTES):
        raise GemEnchantFetchBlocked("V267_ENCHANT_CSV_SIZE_INVALID")
    return data,url
