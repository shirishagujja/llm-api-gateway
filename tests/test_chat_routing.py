from __future__ import annotations

from uuid import uuid4

import pytest

from app.models.llm_model import LLMModel
from app.models.provider import Provider, ProviderType
from app.exceptions import ModelNotFoundError
from app.router.model_router import ModelRouter


class _FakeScalars:
    def __init__(self, value):
        self._value = value

    def first(self):
        return self._value

    def all(self):
        return self._value if isinstance(self._value, list) else [self._value]


class _FakeDB:
    def __init__(self, model: LLMModel | None = None, provider: Provider | None = None):
        self.model = model
        self.provider = provider
        self._call = 0

    def scalars(self, statement):
        self._call += 1
        if self._call == 1:
            return _FakeScalars(self.model)
        return _FakeScalars(self.provider)


def _provider() -> Provider:
    return Provider(
        id=uuid4(),
        name="OpenAI",
        provider_type=ProviderType.OPENAI,
        base_url="https://api.openai.com/v1",
        is_active=True,
    )


def _model(provider: Provider, *, active: bool = True) -> LLMModel:
    model = LLMModel(
        id=uuid4(),
        provider_id=provider.id,
        name="gpt-4.1-mini",
        display_name="GPT-4.1 Mini",
        context_window=1048576,
        max_output_tokens=32768,
        is_active=active,
    )
    model.provider = provider
    return model


def test_model_router_uses_database_record():
    provider = _provider()
    model = _model(provider)
    router = ModelRouter(_FakeDB(model=model))  # type: ignore[arg-type]

    decision = router.resolve("gpt-4.1-mini")

    assert decision.provider_type == "openai"
    assert decision.model_name == "gpt-4.1-mini"
    assert decision.model_id == model.id


def test_model_router_heuristic_for_unregistered_gpt_model():
    provider = _provider()
    router = ModelRouter(_FakeDB(model=None, provider=provider))  # type: ignore[arg-type]

    decision = router.resolve("gpt-5-custom")

    assert decision.provider_type == "openai"
    assert decision.model_id is None
    assert decision.model_name == "gpt-5-custom"


def test_model_router_unknown_model():
    router = ModelRouter(_FakeDB(model=None, provider=None))  # type: ignore[arg-type]

    with pytest.raises(ModelNotFoundError):
        router.resolve("totally-unknown-model")


def test_model_router_heuristic_for_claude_model():
    provider = Provider(
        id=uuid4(),
        name="Anthropic",
        provider_type=ProviderType.ANTHROPIC,
        base_url="https://api.anthropic.com",
        is_active=True,
    )
    router = ModelRouter(_FakeDB(model=None, provider=provider))  # type: ignore[arg-type]

    decision = router.resolve("claude-3-opus")

    assert decision.provider_type == "anthropic"
    assert decision.model_id is None
