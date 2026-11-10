from app.adapters.wearable_base import WearableAdapter


class WearablePlatformAAdapter(WearableAdapter):
    provider = "wearable_platform_a"
    categories = ("sleep", "heart_rate", "activity")
