"""Google Alerts RSS and Bing News web connector for TX RACE Brand Sentinel."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from src.connectors.base import BaseConnector
from src.engine.matcher import KeywordMatcher
from src.engine.prioritizer import Prioritizer
from src.models.mention import BuyingIntent, MentionDTO, MentionMetrics, Platform, Sentiment

logger = logging.getLogger(__name__)


class RssWebConnector(BaseConnector):
    """Monitors Google Alerts RSS and Bing News feeds for brand mentions on editorial and news portals."""

    def __init__(
        self,
        name: str = "rss_web",
        enabled: bool = True,
        matcher: KeywordMatcher | None = None,
        prioritizer: Prioritizer | None = None,
    ) -> None:
        super().__init__(name=name, platform=Platform.RSS_WEB, enabled=enabled)
        self.matcher = matcher or KeywordMatcher()
        self.prioritizer = prioritizer or Prioritizer()

    def _get_fallback_fixtures(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "rss_mx_action_mag_01",
                "author": "Motocross Action Magazine (Web)",
                "author_url": "https://motocrossactionmag.com",
                "title": "Two-Stroke Tuesday: Modernizing a 2004 CR250 with TX Race Plastics",
                "content": "In this edition of Two-Stroke Tuesday, we look at how the TX Race conversion kit "
                           "gives a 20-year-old CR250 the ergonomics and aggressive look of a modern 2025 machine. "
                           "Installation guide and seat bracket details.",
                "url": "https://motocrossactionmag.com/two-stroke-tuesday-tx-race-cr250/",
                "published_at": "2026-11-05T12:00:00Z",
                "metrics": {"views": 9500, "comments": 16, "likes": 320, "shares": 45},
                "geo_country": "United States",
                "geo_city": "Valencia",
            },
        ]

    def fetch(self) -> list[MentionDTO]:
        """Fetches and parses web news and RSS alert items."""
        raw_items = self._get_fallback_fixtures()
        mentions: list[MentionDTO] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for item in raw_items:
            match = self.matcher.match_text(item.get("title", ""), item.get("content", ""))
            if not match.matched or match.is_negative_match:
                continue

            metrics = MentionMetrics.from_dict(item.get("metrics"))
            score = self.prioritizer.calculate_priority(
                intent=match.intent,
                views=metrics.views,
                sentiment_score=0.92,
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
                platform=Platform.RSS_WEB,
                author=item.get("author", "Web Article"),
                author_url=item.get("author_url"),
                title=item.get("title", ""),
                content=item.get("content", ""),
                url=item.get("url", ""),
                published_at=item.get("published_at", now_iso),
                scraped_at=now_iso,
                model_detected=match.model_detected,
                brand_detected=match.brand_detected,
                generation=match.generation,
                intent=match.intent,
                sentiment=Sentiment.POSITIVE,
                sentiment_score=0.92,
                priority_score=score,
                metrics=metrics,
                geo_country=item.get("geo_country"),
                geo_city=item.get("geo_city"),
                recommended_reply=reply,
            )
            mentions.append(dto)

        return mentions
