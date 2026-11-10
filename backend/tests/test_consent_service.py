import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditLog, ConsentRecord
from app.seeds.users import user_id
from app.services.consent_service import ConsentLedgerService, ProcessingBlockedError


def test_record_is_append_only_and_audited(seeded: Session) -> None:
    uid = user_id(seeded, "asha")
    svc = ConsentLedgerService(seeded)
    before = len(svc.consents.history(uid))
    svc.record(uid, "device_processing", "2024-02", "declined", "c1")
    svc.record(uid, "device_processing", "2024-03", "accepted", "c2")
    history, latest = svc.list_for_user(uid)
    assert len(history) == before + 2
    by_purpose = {r.purpose: r for r in latest}
    assert by_purpose["device_processing"].status == "accepted"
    assert len(latest) == 2
    assert seeded.scalars(select(AuditLog).where(AuditLog.action == "consent.record")).all()


def test_declined_blocks_with_explanation(seeded: Session) -> None:
    uid = user_id(seeded, "asha")
    svc = ConsentLedgerService(seeded)
    svc.assert_permitted(uid, "device_processing")
    svc.record(uid, "device_processing", "2024-02", "declined", "c1")
    with pytest.raises(ProcessingBlockedError) as exc:
        svc.assert_permitted(uid, "device_processing")
    assert exc.value.explanation


def test_seed_gate_personas(seeded: Session) -> None:
    svc = ConsentLedgerService(seeded)
    assert svc.consents.latest(user_id(seeded, "meena"), "device_processing").status == "declined"  # type: ignore[union-attr]
    assert svc.consents.latest(user_id(seeded, "rohan"), "device_processing") is None
    from app.seeds import run_all

    run_all(seeded)
    count = len(
        seeded.scalars(select(ConsentRecord).where(ConsentRecord.user_id == user_id(seeded, "meena"))).all()
    )
    run_all(seeded)
    assert (
        len(
            seeded.scalars(
                select(ConsentRecord).where(ConsentRecord.user_id == user_id(seeded, "meena"))
            ).all()
        )
        == count
    )
