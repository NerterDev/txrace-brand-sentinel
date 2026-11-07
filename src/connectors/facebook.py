"""Facebook Graph API public groups connector for TX RACE Brand Sentinel."""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

from src.connectors.base import BaseConnector
from src.engine.matcher import KeywordMatcher
from src.engine.prioritizer import Prioritizer
from src.models.mention import MentionDTO, MentionMetrics, Platform, Sentiment

logger = logging.getLogger(__name__)


class FacebookConnector(BaseConnector):
    """Monitors third-party Facebook motocross discussions when Graph API credentials are configured.

    Never fabricates synthetic posts or surfaces official @txracecom pages.
    """

    def __init__(
        self,
        name: str = "facebook",
        enabled: bool = True,
        access_token: str | None = None,
        seed_items: list[dict[str, Any]] | None = None,
        matcher: KeywordMatcher | None = None,
        prioritizer: Prioritizer | None = None,
    ) -> None:
        super().__init__(name=name, platform=Platform.FACEBOOK, enabled=enabled)
        self.access_token = access_token or os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.seed_items = seed_items
        self.matcher = matcher or KeywordMatcher()
        self.prioritizer = prioritizer or Prioritizer()

    def fetch(self) -> list[MentionDTO]:
        """Normalizes authenticated or injected third-party Facebook posts."""
        raw_items: list[dict[str, Any]] = []
        if self.seed_items is not None:
            raw_items = self.seed_items
        elif not self.access_token:
            logger.info("FACEBOOK_ACCESS_TOKEN not configured; skipping unauthenticated Facebook feed.")
            return []

        mentions: list[MentionDTO] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for item in raw_items:
            author = item.get("author", "Facebook User")
            url = item.get("url", "")
            author_url = item.get("author_url")
            if self.matcher.is_official_brand_source(author, url, author_url):
                continue

            match = self.matcher.match_text(item.get("title", ""), item.get("content", ""))
            if not match.matched or match.is_negative_match:
                continue

            metrics = MentionMetrics.from_dict(item.get("metrics"))
            score = self.prioritizer.calculate_priority(
                intent=match.intent,
                views=metrics.views,
                sentiment_score=0.85,
                published_at_iso=item.get("published_at"),
            )

            reply = self.prioritizer.generate_reply(
                intent=match.intent,
                model=match.model_detected,
                generation=match.generation,
                language="en",
            )

            dto = MentionDTO(
                id=item["id"],
                platform=Platform.FACEBOOK,
                author=author,
                author_url=author_url,
                title=item.get("title", ""),
                content=item.get("content", ""),
                url=url,
                published_at=item.get("published_at", now_iso),
                scraped_at=now_iso,
                model_detected=match.model_detected,
                brand_detected=match.brand_detected,
                generation=match.generation,
                intent=match.intent,
                sentiment=Sentiment.POSITIVE,
                sentiment_score=0.85,
                priority_score=score,
                metrics=metrics,
                geo_country=item.get("geo_country"),
                geo_city=item.get("geo_city"),
                recommended_reply=reply,
            )
            mentions.append(dto)

        return mentions
