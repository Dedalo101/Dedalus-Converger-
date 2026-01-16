from typing import Dict, Type

from .base import ObservationAdapter


class AdapterRegistry:
    """Central place to register and get adapters by name."""

    _adapters: Dict[str, Type[ObservationAdapter]] = {}

    @classmethod
    def register(cls, adapter_class: Type[ObservationAdapter]):
        name = adapter_class.name
        if name in cls._adapters:
            raise ValueError(f"Adapter name conflict: {name!r} already registered")
        cls._adapters[name] = adapter_class

    @classmethod
    def get(cls, name: str) -> Type[ObservationAdapter]:
        adapter_cls = cls._adapters.get(name)
        if adapter_cls is None:
            raise ValueError(f"No adapter registered for source: {name!r}")
        return adapter_cls
