"""X / Twitter and Nitter RSS connector for TX RACE Brand Sentinel."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from src.connectors.base import BaseConnector
from src.engine.matcher import KeywordMatcher
from src.engine.prioritizer import Prioritizer
from src.models.mention import BuyingIntent, MentionDTO, MentionMetrics, Platform, Sentiment

logger = logging.getLogger(__name__)


class TwitterConnector(BaseConnector):
    """Monitors X / Twitter micro-posts, retweets, and hashtag chatter."""

    def __init__(
        self,
        name: str = "twitter",
        enabled: bool = True,
        matcher: KeywordMatcher | None = None,
        prioritizer: Prioritizer | None = None,
    ) -> None:
        super().__init__(name=name, platform=Platform.TWITTER, enabled=enabled)
        self.matcher = matcher or KeywordMatcher()
        self.prioritizer = prioritizer or Prioritizer()

    def _get_fallback_fixtures(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "tw_txrace_official_01",
                "author": "@txrace",
                "author_url": "https://x.com/txrace",
                "title": "TX RACE™ Official on X: 2-Stroke Restyle Kits & Releases",
                "content": "Official updates from TX RACE on X. Showcasing our Gen24 and Gen25 bolt-on restyle kits "
                           "for Honda CR125/250 and Kawasaki KX models. 2-strokes will never die! #txrace #cr125 #cr250",
                "url": "https://x.com/txrace",
                "published_at": "2026-11-06T18:45:00Z",
                "metrics": {"views": 16400, "comments": 22, "likes": 540, "shares": 68},
                "geo_country": "Spain",
                "geo_city": "Pontevedra",
            },
        ]

    def fetch(self) -> list[MentionDTO]:
        """Fetches and normalizes tweets."""
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
                sentiment_score=0.90,
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
                platform=Platform.TWITTER,
                author=item.get("author", "X User"),
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
                sentiment_score=0.90,
                priority_score=score,
                metrics=metrics,
                geo_country=item.get("geo_country"),
                geo_city=item.get("geo_city"),
                recommended_reply=reply,
            )
            mentions.append(dto)

        return mentions
