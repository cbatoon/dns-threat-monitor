"""
main.py - Run the DNS cache collector and print what it found.

Usage (on Windows):
    python main.py

Test a saved cache file (works on any OS):

    python main.py --sample sample_cache.json


"""

import argparse
import sys

from collector import collect


def main():
    parser = argparse.ArgumentParser(description="DNS cache monitor - collection step")
    parser.add_argument("--sample", help="read a saved cache JSON file")
    args = parser.parse_args()

    try:
        records = collect(args.sample)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not records:
        print("No public DNS records in the cache.")
        return

    print(f"{'DOMAIN':<40} {'IP':<40} {'TYPE':<5} TTL")
    for r in records:
        print(f"{r.domain:<40} {r.ip:<40} {r.record_type:<5} {r.ttl}")
    print(f"\n{len(records)} public records "
          f"({len({r.ip for r in records})} unique IPs, "
          f"{len({r.domain for r in records})} unique domains)")


if __name__ == "__main__":
    main()
