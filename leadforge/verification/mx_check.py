import dns.resolver
import asyncio


async def check_mx(domain: str) -> bool:
    """Return True if the domain has at least one MX record."""
    try:
        loop = asyncio.get_event_loop()
        records = await loop.run_in_executor(
            None,
            lambda: dns.resolver.resolve(domain, "MX", lifetime=5.0)
        )
        return len(records) > 0
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, Exception):
        return False
