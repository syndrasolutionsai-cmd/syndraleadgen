import asyncio
import smtplib
import dns.resolver


async def check_smtp(email: str) -> bool:
    """
    Perform an SMTP RCPT TO handshake without sending an email.
    Returns True if the server accepts the recipient.
    This is a best-effort check — catch-all servers always return True.
    """
    domain = email.split("@")[1]
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _smtp_check_sync, email, domain)
    except Exception:
        return True  # If SMTP check fails, don't block — let downstream verify


def _smtp_check_sync(email: str, domain: str) -> bool:
    try:
        mx_records = dns.resolver.resolve(domain, "MX", lifetime=5.0)
        mx_host = str(sorted(mx_records, key=lambda r: r.preference)[0].exchange)
        with smtplib.SMTP(timeout=10) as smtp:
            smtp.connect(mx_host, 25)
            smtp.helo("leadforge.io")
            smtp.mail("verify@leadforge.io")
            code, _ = smtp.rcpt(email)
            return code == 250
    except Exception:
        return True  # uncertain = don't reject
