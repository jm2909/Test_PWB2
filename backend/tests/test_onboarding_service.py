from sqlalchemy.orm import Session

from app.seeds.users import user_id
from app.services.onboarding_service import OnboardingService
from tests.factories import ConsentRecord


def test_new_account_is_not_started(seeded: Session) -> None:
    from app.models import User

    user = User(email="new@example.com", password_hash="x")
    seeded.add(user)
    seeded.commit()
    result = OnboardingService(seeded).get(user.id)
    assert result.status == "not_started"
    assert result.remaining_steps == ["profile", "goal", "device", "consent"]


def test_partial_save_then_consent_completes(seeded: Session) -> None:
    from app.models import User

    user = User(email="new@example.com", password_hash="x")
    seeded.add(user)
    seeded.commit()
    service = OnboardingService(seeded)
    partial = service.save(user.id, {"display_name": "N"}, "", "later")
    assert partial.status == "in_progress" and partial.remaining_steps == ["goal", "consent"]
    full = service.save(user.id, {"display_name": "N"}, "sleep_better", "scale")
    assert full.remaining_steps == ["consent"]
    for purpose in ("device_processing", "personalized_insights"):
        seeded.add(ConsentRecord(user_id=user.id, purpose=purpose, version="1", status="declined"))
    seeded.commit()
    assert service.get(user.id).status == "complete"


def test_seeded_states(seeded: Session) -> None:
    service = OnboardingService(seeded)
    assert service.get(user_id(seeded, "asha")).status == "complete"
    assert service.get(user_id(seeded, "meena")).status == "complete"
    rohan = service.get(user_id(seeded, "rohan"))
    assert rohan.status == "in_progress" and rohan.profile and "profile" not in rohan.remaining_steps
