from __future__ import annotations

from uuid import uuid4

import pytest

from app.cache.memory import MemoryCacheClient
from app.exceptions.gateway import RateLimitError
from app.models.quota import RateLimitPriority, TeamRateLimit
from app.rate_limit.service import RateLimitService


class _FakeScalars:
    def __init__(self, value):
        self._value = value

    def first(self):
        return self._value


class _QuotaFakeDB:
    def __init__(self, *, rate_limit=None, budget=None):
        self.rate_limit = rate_limit
        self.budget = budget

    def scalars(self, statement):
        sql = str(statement)
        if "team_rate_limits" in sql:
            return _FakeScalars(self.rate_limit)
        if "team_budgets" in sql:
            return _FakeScalars(self.budget)
        return _FakeScalars(None)


def test_rate_limit_rejects_burst_requests():
    team_id = uuid4()
    cache = MemoryCacheClient()
    db = _QuotaFakeDB(
        rate_limit=TeamRateLimit(
            team_id=team_id,
            requests_per_minute=2,
            tokens_per_minute=10_000,
            burst_multiplier=1.0,
            priority=RateLimitPriority.NORMAL,
            is_active=True,
        )
    )
    service = RateLimitService(db, cache)  # type: ignore[arg-type]

    service.check_request(team_id)
    service.check_request(team_id)

    with pytest.raises(RateLimitError) as exc_info:
        service.check_request(team_id)

    assert exc_info.value.retry_after is not None
    assert exc_info.value.retry_after >= 1


def test_rate_limit_priority_affects_refill():
    cache = MemoryCacheClient()
    low_team = uuid4()
    high_team = uuid4()
    low = RateLimitService(
        _QuotaFakeDB(
            rate_limit=TeamRateLimit(
                team_id=low_team,
                requests_per_minute=60,
                tokens_per_minute=60,
                burst_multiplier=1.0,
                priority=RateLimitPriority.LOW,
                is_active=True,
            )
        ),
        cache,
    )  # type: ignore[arg-type]
    high = RateLimitService(
        _QuotaFakeDB(
            rate_limit=TeamRateLimit(
                team_id=high_team,
                requests_per_minute=60,
                tokens_per_minute=60,
                burst_multiplier=1.0,
                priority=RateLimitPriority.HIGH,
                is_active=True,
            )
        ),
        cache,
    )  # type: ignore[arg-type]

    low.reserve_tokens(low_team, 30)
    high.reserve_tokens(high_team, 30)

    with pytest.raises(RateLimitError):
        low.reserve_tokens(low_team, 31)

    high.reserve_tokens(high_team, 31)
