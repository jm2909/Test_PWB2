from app.adapters.wearable_base import WearableAdapter


class WearablePlatformBAdapter(WearableAdapter):
    provider = "wearable_platform_b"
    categories = ("sleep", "heart_rate", "activity", "weight")
