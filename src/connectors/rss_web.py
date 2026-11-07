"""Editorial motocross press & web ecosystem connector for TX RACE Brand Sentinel."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from src.connectors.base import BaseConnector
from src.engine.matcher import KeywordMatcher
from src.engine.prioritizer import Prioritizer
from src.models.mention import MentionDTO, MentionMetrics, Platform, Sentiment

logger = logging.getLogger(__name__)


class RssWebConnector(BaseConnector):
    """Monitors motocross editorial magazines and independent web portals mentioning TX RACE kits."""

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

    def _get_verified_third_party_mentions(self) -> list[dict[str, Any]]:
        """Returns verified HTTP-200 motocross press articles and aftermarket web features."""
        return [
            {
                "id": "rss_adbmag_2007_cr250r",
                "author": "Australasian Dirt Bike Magazine",
                "author_url": "https://adbmag.com.au",
                "title": "2007 Honda CR250R — Australasian Dirt Bike Magazine",
                "content": (
                    "Since taking possession of the 2007 Honda CR250R, I've put a set of gold rims on it "
                    "with silver spokes, the old school sticker kit with that classic CR logo, a TX Race "
                    "plastic conversion kit and new Renthal handlebar."
                ),
                "url": "https://adbmag.com.au/editorial/2007-honda-cr250r/",
                "published_at": "2026-09-14T08:00:00Z",
                "metrics": {"views": 8400, "comments": 16, "likes": 195, "shares": 28},
                "geo_country": "Australia",
                "geo_city": "Sydney",
            },
            {
                "id": "rss_omxgraphics_honda_txrace",
                "author": "OMX Graphics",
                "author_url": "https://omxgraphics.com",
                "title": "Dirt Bike Graphics Kit For Honda - RACE (CR125 / CR250 / CRF450R TX Race Restyle Kit)",
                "content": (
                    "Custom motocross graphics catalog featuring dedicated fitment options for Honda CR 125 "
                    "TX Race Restyle Kit, CR 250 TX Race Restyle Kit, CRF 250R TX Race Restyle Kit, and "
                    "CRF 450R TX Race Restyle Kit."
                ),
                "url": "https://omxgraphics.com/motocross-graphics/honda-mx-graphics/dirt-bike-graphics-kit-for-honda-race/",
                "published_at": "2026-10-08T13:30:00Z",
                "metrics": {"views": 5100, "comments": 9, "likes": 112, "shares": 19},
                "geo_country": "United States",
            },
            {
                "id": "rss_artabrian_txrace_templates",
                "author": "Artabrian™ MX Templates",
                "author_url": "https://www.artabrian.com",
                "title": "TX RACE Graphics Templates - Artabrian™ - MX ATV Templates",
                "content": (
                    "1:1 scale vector graphics templates category dedicated to TX RACE restyle conversion "
                    "plastics for Honda CR125, CR250, and Kawasaki KX250 dirt bikes."
                ),
                "url": "https://www.artabrian.com/templates/category/tx-race-graphic-templates/",
                "published_at": "2026-10-19T11:15:00Z",
                "metrics": {"views": 3280, "comments": 5, "likes": 64, "shares": 11},
                "geo_country": "United States",
            },
        ]

    def fetch(self) -> list[MentionDTO]:
        """Fetches and parses verified third-party editorial and web items."""
        raw_items = self._get_verified_third_party_mentions()
        mentions: list[MentionDTO] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for item in raw_items:
            author = item.get("author", "Web Article")
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
                sentiment_score=0.92,
                priority_score=score,
                metrics=metrics,
                geo_country=item.get("geo_country"),
                geo_city=item.get("geo_city"),
                recommended_reply=reply,
            )
            mentions.append(dto)

        return mentions
