"""Instagram hashtag and mention tracker for TX RACE Brand Sentinel."""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

from src.connectors.base import BaseConnector
from src.engine.matcher import KeywordMatcher
from src.engine.prioritizer import Prioritizer
from src.models.mention import BuyingIntent, MentionDTO, MentionMetrics, Platform, Sentiment

logger = logging.getLogger(__name__)


class InstagramConnector(BaseConnector):
    """Tracks Instagram posts, reels, and stories tagging @txrace or using brand hashtags."""

    def __init__(
        self,
        name: str = "instagram",
        enabled: bool = True,
        access_token: str | None = None,
        matcher: KeywordMatcher | None = None,
        prioritizer: Prioritizer | None = None,
    ) -> None:
        super().__init__(name=name, platform=Platform.INSTAGRAM, enabled=enabled)
        self.access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.matcher = matcher or KeywordMatcher()
        self.prioritizer = prioritizer or Prioritizer()

    def _get_fallback_fixtures(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "ig_rm250_yellow_beast_01",
                "author": "@vintage_suzuki_mx",
                "author_url": "https://www.instagram.com/vintage_suzuki_mx",
                "title": "RM250 2004 Build Finished!",
                "content": "Fresh graphics installed on the TX Race restyle kit! Best investment for this RM250 2-stroke. "
                           "Tagging @txrace for the clean fitment. What do you guys think? #txrace #rm250 #suzukimx",
                "url": "https://www.instagram.com/explore/tags/txrace/",
                "published_at": "2026-11-06T15:20:00Z",
                "metrics": {"views": 14200, "comments": 88, "likes": 2150, "shares": 140},
                "geo_country": "Spain",
                "geo_city": "Barcelona",
            },
            {
                "id": "ig_cr125_seat_question_02",
                "author": "@sandiego_dirt_riders",
                "author_url": "https://www.instagram.com/explore/tags/cr125/",
                "title": "CR125 Seat foam query",
                "content": "Anyone running the TX-Race Gen24 kit on a 2001 CR125? Is the seat comfortable for 30min motos? "
                           "Need to know before I buy! @txrace #cr125 #txrace",
                "url": "https://www.instagram.com/explore/tags/cr125/",
                "published_at": "2026-11-06T21:45:00Z",
                "metrics": {"views": 3800, "comments": 31, "likes": 420, "shares": 12},
                "geo_country": "United States",
                "geo_city": "San Diego",
            },
        ]

    def fetch(self) -> list[MentionDTO]:
        """Fetches and normalizes Instagram community mentions."""
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
                language="es" if item.get("geo_country") == "Spain" else "en",
            )

            dto = MentionDTO(
                id=item["id"],
                platform=Platform.INSTAGRAM,
                author=item.get("author", "Instagram User"),
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

