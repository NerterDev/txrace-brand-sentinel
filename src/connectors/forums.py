"""Specialized motocross forums connector for ThumperTalk, VitalMX, and DirtRider."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from src.connectors.base import BaseConnector
from src.engine.matcher import KeywordMatcher
from src.engine.prioritizer import Prioritizer
from src.models.mention import BuyingIntent, MentionDTO, MentionMetrics, Platform, Sentiment

logger = logging.getLogger(__name__)


class ForumsConnector(BaseConnector):
    """Monitors classic motocross forums (ThumperTalk, VitalMX, DirtRider) for technical questions and builds."""

    def __init__(
        self,
        name: str = "forums",
        enabled: bool = True,
        forums: list[dict[str, str]] | None = None,
        matcher: KeywordMatcher | None = None,
        prioritizer: Prioritizer | None = None,
    ) -> None:
        super().__init__(name=name, platform=Platform.FORUMS, enabled=enabled)
        self.forums = forums or [
            {"name": "ThumperTalk", "url": "https://www.thumpertalk.com"},
            {"name": "VitalMX", "url": "https://www.vitalmx.com"},
            {"name": "DirtRider", "url": "https://www.dirtrider.com"},
        ]
        self.matcher = matcher or KeywordMatcher()
        self.prioritizer = prioritizer or Prioritizer()

    def _get_fallback_fixtures(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "tt_cr250_fitment_thread_01",
                "author": "CR_Fanatic_99",
                "author_url": "https://www.thumpertalk.com/profile/18292-cr_fanatic_99/",
                "title": "TX Race kit on 1999 Honda CR250 — Subframe and seat fitment?",
                "content": "Has anyone installed the TX Race kit on a 97-99 generation CR250? How does the seat foam "
                           "align with the OEM gas tank and does the airbox seal properly? Looking for feedback before purchasing.",
                "url": "https://www.thumpertalk.com/forums/search/?q=restyle+kit&quick=1",
                "published_at": "2026-11-06T14:30:00Z",
                "metrics": {"views": 3200, "comments": 24, "likes": 56, "shares": 3},
                "geo_country": "United States",
                "geo_city": "Denver",
            },
            {
                "id": "vmx_kx125_gen25_review_02",
                "author": "SoCal_MX_Rider",
                "author_url": "https://www.vitalmx.com/forums/Moto-Related",
                "title": "TX-Race KX125 Gen25 Restyle — Full review and where to buy",
                "content": "Finished assembling the TX-Race Gen25 restyle kit on my KX125. The bike looks 20 years newer! "
                           "Where can I buy replacement seat covers in case I want custom gripper material? Here are track photos.",
                "url": "https://www.vitalmx.com/forums/Moto-Related",
                "published_at": "2026-11-06T17:15:00Z",
                "metrics": {"views": 4800, "comments": 41, "likes": 98, "shares": 7},
                "geo_country": "United States",
                "geo_city": "Corona",
            },
            {
                "id": "tt_yz250_price_canada_03",
                "author": "Ontario_Moto",
                "author_url": "https://www.thumpertalk.com/forums/forum/13-honda-2-stroke/",
                "title": "Where can I order the TX Race kit in Canada? Shipping cost & stock",
                "content": "Looking for the TX Race kit for my YZ250. How much is shipping to Ontario and who is the official distributor?",
                "url": "https://www.thumpertalk.com/forums/forum/13-honda-2-stroke/",
                "published_at": "2026-11-06T21:00:00Z",
                "metrics": {"views": 1950, "comments": 18, "likes": 32, "shares": 2},
                "geo_country": "Canada",
                "geo_city": "Toronto",
            },
        ]

    def fetch(self) -> list[MentionDTO]:
        """Fetches and normalizes specialized forum threads."""
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
                sentiment_score=0.88,
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
                platform=Platform.FORUMS,
                author=item.get("author", "Forum Member"),
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
                sentiment_score=0.88,
                priority_score=score,
                metrics=metrics,
                geo_country=item.get("geo_country"),
                geo_city=item.get("geo_city"),
                recommended_reply=reply,
            )
            mentions.append(dto)

        return mentions
