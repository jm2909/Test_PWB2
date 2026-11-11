"""Canonical demo credentials: the single source of truth (mirrored by the frontend and README)."""

DEMO_PASSWORD = "Wellness-Demo-2026!"  # noqa: S105 - published demo credential

ASHA_EMAIL = "asha@sapphire.example"
ROHAN_EMAIL = "rohan@sapphire.example"

DEMO_ACCOUNTS: dict[str, dict[str, str]] = {
    "asha": {"email": ASHA_EMAIL, "password": DEMO_PASSWORD, "display_name": "Asha"},
    "rohan": {"email": ROHAN_EMAIL, "password": DEMO_PASSWORD, "display_name": "Rohan"},
}
