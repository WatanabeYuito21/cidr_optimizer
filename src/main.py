"""Simple CIDR optimizer script.

This script takes a source CIDR, removes a set of excluded IPv4 addresses, and
then collapses the remaining individual IP addresses back into the minimal set
of CIDR blocks using ipaddress.collapse_addresses.

Run directly: python src/main.py --source-cidr 192.168.0.0/29 --exclude 192.168.0.2 192.168.0.3
"""
from __future__ import annotations

import argparse
import ipaddress
from typing import Iterable, List


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments including source_cidr and exclude IP list.
    """
    parser = argparse.ArgumentParser(description="CIDR optimizer: exclude IPs and collapse remaining addresses.")
    parser.add_argument(
        "--source-cidr",
        required=True,
        help="Source CIDR block (e.g. 192.168.0.0/24)",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="List of IPv4 addresses to exclude (space separated)",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for the script.

    Steps:
      1. Parse runtime arguments for source CIDR and exclude IP list.
      2. Convert excluded IPs to IPv4Address objects for comparison efficiency.
      3. Enumerate all IPs in the source CIDR.
      4. Filter out the excluded IPs.
      5. Collapse the remaining IPs into the smallest possible CIDR blocks.
      6. Print the resulting CIDR blocks.
    """
    args = parse_args()
    source_cidr: str = args.source_cidr
    execlude_ips_raw: List[str] = args.exclude  # Keep original typo label in code variable (execlude)

    # Convert excluded IP strings to IPv4Address objects for faster membership checks.
    try:
        execlude_ips = [ipaddress.IPv4Address(ip) for ip in execlude_ips_raw]
    except ipaddress.AddressValueError as e:
        raise SystemExit(f"Invalid IP in --exclude list: {e}")

    # Expand the source CIDR into a list of IPv4Address objects.
    try:
        source_network = ipaddress.ip_network(source_cidr, strict=False)
    except ValueError as e:
        raise SystemExit(f"Invalid --source-cidr value: {e}")
    source_ips = list(source_network)

    # Collect IPs that are NOT in the exclude list.
    remaining_ip_strs: List[str] = []
    for ip in source_ips:
        if ip not in execlude_ips:
            remaining_ip_strs.append(str(ip))  # Store as strings for downstream function flexibility.

    if not remaining_ip_strs:
        print("No IPs remain after exclusion. Nothing to collapse.")
        return

    # Collapse the remaining individual IPs into minimal CIDR blocks.
    collapsed_networks = ipv4_address_to_cidr(remaining_ip_strs)
    collapsed_networks_str = [str(net) for net in collapsed_networks]  # Ensure printable string form.

    # Output results.
    print("##### Result #####")
    for cidr in collapsed_networks_str:
        print(cidr)
    print("##### End Result #####")


def ipv4_address_to_cidr(ip_list: Iterable[str | ipaddress.IPv4Address]) -> List[ipaddress.IPv4Network]:
    """Collapse a list of IPv4 addresses (str or IPv4Address) into CIDR blocks.

    Args:
        ip_list (Iterable[str | ipaddress.IPv4Address]): Iterable of IPv4 addresses.
            May be strings or IPv4Address instances.

    Returns:
        list[ipaddress.IPv4Network]: A list of IPv4Network objects representing
        the minimal set of CIDR blocks covering the provided addresses.
    """
    ip_list = list(ip_list)  # Ensure we can index.
    if not ip_list:
        return []
    # Convert any string representations to IPv4Address for uniform processing.
    if isinstance(ip_list[0], str):
        try:
            ip_objects = [ipaddress.IPv4Address(ip) for ip in ip_list]
        except ipaddress.AddressValueError as e:
            raise SystemExit(f"Invalid IP address provided: {e}")
    else:
        ip_objects = ip_list  # already IPv4Address objects

    # collapse_addresses groups sequences of addresses into the smallest possible set of networks.
    cidr_blocks = list(ipaddress.collapse_addresses(ip_objects))
    return cidr_blocks


if __name__ == "__main__":
    main()
