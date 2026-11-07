"""Canonical MentionDTO and enumeration models for TX RACE Brand Sentinel."""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Platform(str, Enum):
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    REDDIT = "reddit"
    TWITTER = "twitter"
    FORUMS = "forums"
    MARKETPLACES = "marketplaces"
    RSS_WEB = "rss_web"
    OTHER = "other"


class BuyingIntent(str, Enum):
    COMPRA_ATIVA = "COMPRA_ATIVA"
    VIRAL = "VIRAL"
    PROJETO_BUILD = "PROJETO_BUILD"
    DUVIDA_TECNICA = "DUVIDA_TECNICA"
    GERAL = "GERAL"


class Sentiment(str, Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


@dataclass(frozen=True)
class MentionMetrics:
    views: int = 0
    comments: int = 0
    likes: int = 0
    shares: int = 0

    def __post_init__(self) -> None:
        if self.views < 0 or self.comments < 0 or self.likes < 0 or self.shares < 0:
            raise ValueError("Metrics values must be non-negative integers.")

    def to_dict(self) -> dict[str, int]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> MentionMetrics:
        if not data:
            return cls()
        return cls(
            views=max(0, int(data.get("views", 0))),
            comments=max(0, int(data.get("comments", 0))),
            likes=max(0, int(data.get("likes", 0))),
            shares=max(0, int(data.get("shares", 0))),
        )


@dataclass(frozen=True)
class MentionDTO:
    """Immutable data transfer object representing a verified brand mention."""
    id: str
    platform: Platform
    author: str
    title: str
    content: str
    url: str
    published_at: str
    scraped_at: str
    model_detected: str
    brand_detected: str
    intent: BuyingIntent
    sentiment: Sentiment
    sentiment_score: float
    priority_score: float
    metrics: MentionMetrics
    author_url: str | None = None
    generation: str | None = None
    geo_country: str | None = None
    geo_city: str | None = None
    is_viral: bool = False
    recommended_reply: str | None = None
    raw_data: dict[str, Any] | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        # Validate ID
        if not self.id or not isinstance(self.id, str):
            raise ValueError("MentionDTO id must be a non-empty string.")

        # Validate Platform
        if isinstance(self.platform, str) and not isinstance(self.platform, Platform):
            try:
                object.__setattr__(self, "platform", Platform(self.platform.lower()))
            except ValueError:
                object.__setattr__(self, "platform", Platform.OTHER)

        # Validate Intent
        if isinstance(self.intent, str) and not isinstance(self.intent, BuyingIntent):
            try:
                object.__setattr__(self, "intent", BuyingIntent(self.intent.upper()))
            except ValueError:
                object.__setattr__(self, "intent", BuyingIntent.GERAL)

        # Validate Sentiment
        if isinstance(self.sentiment, str) and not isinstance(self.sentiment, Sentiment):
            try:
                object.__setattr__(self, "sentiment", Sentiment(self.sentiment.upper()))
            except ValueError:
                object.__setattr__(self, "sentiment", Sentiment.NEUTRAL)

        # Validate sentiment_score range [0.0, 1.0]
        score = float(self.sentiment_score)
        if not (0.0 <= score <= 1.0):
            score = max(0.0, min(1.0, score))
        object.__setattr__(self, "sentiment_score", score)

        # Validate priority_score range [0.0, 100.0]
        p_score = float(self.priority_score)
        if not (0.0 <= p_score <= 100.0):
            p_score = max(0.0, min(100.0, p_score))
        object.__setattr__(self, "priority_score", p_score)

        # Auto-compute viral if views >= 10,000
        if self.metrics and self.metrics.views >= 10000 and not self.is_viral:
            object.__setattr__(self, "is_viral", True)

    @staticmethod
    def generate_id(platform: str, url: str, content: str) -> str:
        """Deterministically generates a SHA-256 hex digest for a mention."""
        norm = f"{platform.strip().lower()}|{url.strip().lower()}|{content.strip()}"
        return hashlib.sha256(norm.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Serializes MentionDTO to a clean dictionary ready for JSON output."""
        return {
            "id": self.id,
            "platform": self.platform.value if isinstance(self.platform, Platform) else str(self.platform),
            "author": self.author,
            "author_url": self.author_url,
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "published_at": self.published_at,
            "scraped_at": self.scraped_at,
            "model_detected": self.model_detected,
            "brand_detected": self.brand_detected,
            "generation": self.generation,
            "intent": self.intent.value if isinstance(self.intent, BuyingIntent) else str(self.intent),
            "sentiment": self.sentiment.value if isinstance(self.sentiment, Sentiment) else str(self.sentiment),
            "sentiment_score": round(self.sentiment_score, 3),
            "priority_score": round(self.priority_score, 1),
            "metrics": self.metrics.to_dict(),
            "geo_country": self.geo_country,
            "geo_city": self.geo_city,
            "is_viral": self.is_viral,
            "recommended_reply": self.recommended_reply,
            "raw_data": self.raw_data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MentionDTO:
        """Parses a dictionary into a validated MentionDTO."""
        if not isinstance(data, dict):
            raise TypeError("Expected dictionary for MentionDTO parsing.")

        raw_id = data.get("id")
        platform = data.get("platform", "other")
        url = data.get("url", "")
        content = data.get("content", "")

        if not raw_id:
            raw_id = cls.generate_id(str(platform), str(url), str(content))

        now_iso = datetime.now(timezone.utc).isoformat()

        metrics_data = data.get("metrics")
        if isinstance(metrics_data, dict):
            metrics = MentionMetrics.from_dict(metrics_data)
        elif isinstance(metrics_data, MentionMetrics):
            metrics = metrics_data
        else:
            metrics = MentionMetrics()

        return cls(
            id=str(raw_id),
            platform=Platform(platform.lower()) if platform.lower() in [p.value for p in Platform] else Platform.OTHER,
            author=str(data.get("author", "Unknown")),
            author_url=data.get("author_url"),
            title=str(data.get("title", "")),
            content=str(content),
            url=str(url),
            published_at=str(data.get("published_at", now_iso)),
            scraped_at=str(data.get("scraped_at", now_iso)),
            model_detected=str(data.get("model_detected", "UNKNOWN")),
            brand_detected=str(data.get("brand_detected", "TX RACE")),
            generation=data.get("generation"),
            intent=BuyingIntent(data.get("intent", "GERAL")) if data.get("intent") in [i.value for i in BuyingIntent] else BuyingIntent.GERAL,
            sentiment=Sentiment(data.get("sentiment", "NEUTRAL")) if data.get("sentiment") in [s.value for s in Sentiment] else Sentiment.NEUTRAL,
            sentiment_score=float(data.get("sentiment_score", 0.5)),
            priority_score=float(data.get("priority_score", 50.0)),
            metrics=metrics,
            geo_country=data.get("geo_country"),
            geo_city=data.get("geo_city"),
            is_viral=bool(data.get("is_viral", False)),
            recommended_reply=data.get("recommended_reply"),
            raw_data=data.get("raw_data"),
        )

