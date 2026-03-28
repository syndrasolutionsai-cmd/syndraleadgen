from leadforge.models.client import Client
from leadforge.models.campaign import Campaign
from leadforge.models.prospect import Prospect
from leadforge.models.email import Email, EmailStatus


def test_client_table_name():
    assert Client.__tablename__ == "clients"


def test_campaign_has_client_fk():
    assert any("clients" in str(fk) for fk in Campaign.__table__.foreign_keys)


def test_prospect_has_campaign_fk():
    assert any("campaigns" in str(fk) for fk in Prospect.__table__.foreign_keys)


def test_email_status_enum():
    assert EmailStatus.PENDING == "pending"
    assert EmailStatus.APPROVED == "approved"
    assert EmailStatus.REJECTED == "rejected"
    assert EmailStatus.SENT == "sent"
