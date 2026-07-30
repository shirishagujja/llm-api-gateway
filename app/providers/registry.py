from __future__ import annotations

from typing import Type

from app.providers.base import BaseProvider
from app.providers.mock.provider import MockProvider
from app.providers.openai.provider import OpenAIProvider

PROVIDER_REGISTRY: dict[str, Type[BaseProvider]] = {
    "openai": OpenAIProvider,
    "mock": MockProvider,
}
