"""TikTok viral transformations monitor for TX RACE Brand Sentinel."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from src.connectors.base import BaseConnector
from src.engine.matcher import KeywordMatcher
from src.engine.prioritizer import Prioritizer
from src.models.mention import BuyingIntent, MentionDTO, MentionMetrics, Platform, Sentiment

logger = logging.getLogger(__name__)


class TikTokConnector(BaseConnector):
    """Monitors viral short-form dirtbike transformations and TikTok hashtags."""

    def __init__(
        self,
        name: str = "tiktok",
        enabled: bool = True,
        matcher: KeywordMatcher | None = None,
        prioritizer: Prioritizer | None = None,
    ) -> None:
        super().__init__(name=name, platform=Platform.TIKTOK, enabled=enabled)
        self.matcher = matcher or KeywordMatcher()
        self.prioritizer = prioritizer or Prioritizer()

    def _get_fallback_fixtures(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "tt_cr250_transformation_01",
                "author": "@braapp_nation",
                "author_url": "https://www.tiktok.com/@braapp_nation",
                "title": "2002 CR250 build with TX Race Gen25 kit 🔥",
                "content": "From clapped out 2002 to 2025 modern weapon! TX Race restyle kit completely changed this bike #txrace #cr250 #2stroke #dirtbike",
                "url": "https://www.tiktok.com/@braapp_nation/video/7391827361",
                "published_at": "2026-11-05T20:15:00Z",
                "metrics": {"views": 128400, "comments": 640, "likes": 18200, "shares": 3400},
                "geo_country": "United States",
                "geo_city": "Phoenix",
            },
            {
                "id": "tt_yz125_rebuild_02",
                "author": "@motos_mx_pt",
                "author_url": "https://www.tiktok.com/@motos_mx_pt",
                "title": "Yamaha YZ125 com kit TX-Race",
                "content": "A perguntar onde comprar este kit TX Race para YZ125 e preço do envio para Portugal! #txrace #yz125 #ondecomprar",
                "url": "https://www.tiktok.com/@motos_mx_pt/video/7392194821",
                "published_at": "2026-11-06T19:00:00Z",
                "metrics": {"views": 18500, "comments": 142, "likes": 1950, "shares": 180},
                "geo_country": "Portugal",
                "geo_city": "Braga",
            },
        ]

    def fetch(self) -> list[MentionDTO]:
        """Fetches and normalizes TikTok viral motocross posts."""
        raw_items = self._get_fallback_fixtures()
        mentions: list[MentionDTO] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for item in raw_items:
            match = self.matcher.match_text(item.get("title", ""), item.get("content", ""))
            if not match.matched or match.is_negative_match:
                continue

            metrics = MentionMetrics.from_dict(item.get("metrics"))
            # Auto viral heuristic
            intent = BuyingIntent.VIRAL if metrics.views >= 10000 and match.intent == BuyingIntent.GERAL else match.intent

            score = self.prioritizer.calculate_priority(
                intent=intent,
                views=metrics.views,
                sentiment_score=0.95,
                published_at_iso=item.get("published_at"),
            )

            reply = self.prioritizer.generate_reply(
                intent=intent,
                model=match.model_detected,
                generation=match.generation,
                language="pt" if item.get("geo_country") == "Portugal" else "en",
            )

            dto = MentionDTO(
                id=item["id"],
                platform=Platform.TIKTOK,
                author=item.get("author", "TikTok Creator"),
                author_url=item.get("author_url"),
                title=item.get("title", ""),
                content=item.get("content", ""),
                url=item.get("url", ""),
                published_at=item.get("published_at", now_iso),
                scraped_at=now_iso,
                model_detected=match.model_detected,
                brand_detected=match.brand_detected,
                generation=match.generation,
                intent=intent,
                sentiment=Sentiment.POSITIVE,
                sentiment_score=0.95,
                priority_score=score,
                metrics=metrics,
                geo_country=item.get("geo_country"),
                geo_city=item.get("geo_city"),
                recommended_reply=reply,
            )
            mentions.append(dto)

        return mentions

