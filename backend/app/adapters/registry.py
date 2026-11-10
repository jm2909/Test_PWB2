"""Provider -> adapter strategy registry."""

from app.adapters.base import DeviceAdapter
from app.adapters.sapphire_scale import SapphireScaleAdapter
from app.adapters.wearable_platform_a import WearablePlatformAAdapter
from app.adapters.wearable_platform_b import WearablePlatformBAdapter
from app.adapters.wearable_platform_c import WearablePlatformCAdapter


def build_registry() -> dict[str, DeviceAdapter]:
    adapters: list[DeviceAdapter] = [
        SapphireScaleAdapter(),
        WearablePlatformAAdapter(),
        WearablePlatformBAdapter(),
        WearablePlatformCAdapter(),
    ]
    return {a.provider: a for a in adapters}
