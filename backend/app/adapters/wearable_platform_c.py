from app.adapters.wearable_base import WearableAdapter


class WearablePlatformCAdapter(WearableAdapter):
    provider = "wearable_platform_c"
    categories = ("sleep", "activity")
