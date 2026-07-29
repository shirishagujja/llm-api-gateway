from __future__ import annotations

from typing import Type

from app.providers.base import BaseProvider

PROVIDER_REGISTRY: dict[str, Type[BaseProvider]] = {}
