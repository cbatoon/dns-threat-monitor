# DNS Cache Monitor

Watches the Windows DNS client cache, checks the domains and IPs it finds against
VirusTotal, and raises an alert when something is flagged as malicious.

## Status

- [x] **Step 1 – Collect:** read the DNS cache, keep public A/AAAA records only, remove duplicates
- [ ] **Step 2 – Store:** save records in SQLite with first seen / last seen / last checked
- [ ] **Step 3 – Check:** look up new IPs and domains on VirusTotal (4 requests/min, 500/day on the free API)
- [ ] **Step 4 – Alert:** send detections to a syslog server and notify
- [ ] **Step 5 – Schedule:** run every 10–15 minutes with Windows Task Scheduler

## Requirements

- Windows 10/11 (for the live DNS cache)
- Python 3.8+ (no extra packages needed yet)

## Usage

```
python main.py                              # read the live DNS cache (Windows)
python main.py --sample sample_cache.json   # test with saved data on any OS
python -m unittest -v                       # run the tests
```

## How it works

`collector.py` runs `Get-DnsClientCache` through PowerShell and converts the output
to JSON. It keeps IPv4 (A) and IPv6 (AAAA) records and drops private, loopback, and
link-local addresses, since they can't be looked up on VirusTotal and shouldn't be
sent to a third party.

## Known limitations

- Reading the DNS cache requires running as administrator. Without it, Windows returns an empty cache instead of an error.
- Cache entries expire based on their TTL, so a short-lived lookup can disappear
  between polls.
- Browsers using DNS over HTTPS ("Secure DNS") may resolve names without going
  through the Windows cache.
