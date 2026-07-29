from __future__ import annotations

from typing import Type

from app.providers.base import BaseProvider
from app.providers.mock.provider import MockProvider

PROVIDER_REGISTRY: dict[str, Type[BaseProvider]] = {
    "mock": MockProvider,
}
