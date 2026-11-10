"""
collector.py - Reads DNS cache and filters it, returns public IP lookups.

"""

import ipaddress    # check if IP is public/private
import json         # parse JSON from PowerShell
import platform 
import subprocess
from dataclasses import dataclass

# DNS record type numbers
RECORD_TYPES = {1: "A", 28: "AAAA"}

POWERSHELL_COMMAND = (
    "Get-DnsClientCache "
    "| Where-Object { $_.Type -in 1, 28 } "
    "| Select-Object Entry, Data, Type, TimeToLive "
    "| ConvertTo-Json -Compress"
)


@dataclass(frozen=True) # data shouldn't be modified
class DnsRecord:
    domain: str
    ip: str
    record_type: str  # IPv4 ("A") or IPv6 ("AAAA")
    ttl: int          # time to live


def read_raw_cache(timeout=30):
    """Run PowerShell and return the DNS cache"""
    if platform.system() != "Windows":
        raise RuntimeError(
            "Reading the DNS cache only works on Windows. "
            "Use --sample to test with a saved cache file."
        )

    result = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", POWERSHELL_COMMAND],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(f"PowerShell failed: {result.stderr.strip()}")

    return parse_powershell_json(result.stdout)


def parse_powershell_json(text):
    text = text.strip()
    if not text:
        return []
    data = json.loads(text)
    return [data] if isinstance(data, dict) else data


def is_public_ip(value):
    """True only for public addresses (not private, loopback, etc.)."""
    try:
        return ipaddress.ip_address(value).is_global
    except ValueError:
        return False  # not an IP (e.g. CNAME)


def filter_records(raw_entries):
    """Turn raw cache entries into unique DNS records with public IPs only."""
    records = {}
    for entry in raw_entries:
        record_type = RECORD_TYPES.get(entry.get("Type"))
        ip = (entry.get("Data") or "").strip()
        domain = (entry.get("Entry") or "").strip().lower().rstrip(".")

        if record_type is None or not domain or not is_public_ip(ip):
            continue

        ip = str(ipaddress.ip_address(ip))
        ttl = int(entry.get("TimeToLive") or 0)

        # dupe check
        key = (domain, ip, record_type)
        if key not in records or ttl > records[key].ttl:
            records[key] = DnsRecord(domain, ip, record_type, ttl)

    return sorted(records.values(), key=lambda r: (r.domain, r.ip))


def collect(sample_path=None):
    """Return filtered records."""
    if sample_path:
        with open(sample_path, encoding="utf-8") as f:
            raw = parse_powershell_json(f.read())
    else:
        raw = read_raw_cache()
    return filter_records(raw)
