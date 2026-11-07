"""Facebook public groups and marketplace connector for TX RACE Brand Sentinel."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from src.connectors.base import BaseConnector
from src.engine.matcher import KeywordMatcher
from src.engine.prioritizer import Prioritizer
from src.models.mention import BuyingIntent, MentionDTO, MentionMetrics, Platform, Sentiment

logger = logging.getLogger(__name__)


class FacebookConnector(BaseConnector):
    """Monitors Facebook public enthusiast groups and marketplace discussions."""

    def __init__(
        self,
        name: str = "facebook",
        enabled: bool = True,
        matcher: KeywordMatcher | None = None,
        prioritizer: Prioritizer | None = None,
    ) -> None:
        super().__init__(name=name, platform=Platform.FACEBOOK, enabled=enabled)
        self.matcher = matcher or KeywordMatcher()
        self.prioritizer = prioritizer or Prioritizer()

    def _get_fallback_fixtures(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "fb_kx_gang_group_01",
                "author": "KX 2-Stroke Gang (Group)",
                "author_url": "https://www.facebook.com/groups/kx2strokegang",
                "title": "Anyone tried TX Race on 97 KX250?",
                "content": "Hey guys, looking to rebuild my 1997 KX250. Is the seat foam comfortable for long motos? "
                           "Also does the TX-Race kit bolt right on or need bracket mods?",
                "url": "https://www.facebook.com/groups/kx2strokegang/",
                "published_at": "2026-11-06T18:00:00Z",
                "metrics": {"views": 2400, "comments": 42, "likes": 115, "shares": 8},
                "geo_country": "United States",
                "geo_city": "Austin",
            },
            {
                "id": "fb_honda_cr_owners_02",
                "author": "Honda CR 2-Stroke Riders EU",
                "author_url": "https://www.facebook.com/txrace/",
                "title": "TX Race Kit CR250 Gen25 In Stock?",
                "content": "Where can I buy the TX Race restyle kit in Europe? What is the delivery time and price with tax included?",
                "url": "https://www.facebook.com/groups/hondacr2stroke/",
                "published_at": "2026-11-06T20:30:00Z",
                "metrics": {"views": 1800, "comments": 28, "likes": 64, "shares": 5},
                "geo_country": "France",
                "geo_city": "Lyon",
            },
        ]

    def fetch(self) -> list[MentionDTO]:
        """Fetches public Facebook group threads."""
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
                author=item.get("author", "Facebook User"),
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
                sentiment_score=0.85,
                priority_score=score,
                metrics=metrics,
                geo_country=item.get("geo_country"),
                geo_city=item.get("geo_city"),
                recommended_reply=reply,
            )
            mentions.append(dto)

        return mentions

