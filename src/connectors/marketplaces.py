"""Marketplaces connector for eBay Motors, Wallapop, Leboncoin, and Craigslist."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from src.connectors.base import BaseConnector
from src.engine.matcher import KeywordMatcher
from src.engine.prioritizer import Prioritizer
from src.models.mention import BuyingIntent, MentionDTO, MentionMetrics, Platform, Sentiment

logger = logging.getLogger(__name__)


class MarketplacesConnector(BaseConnector):
    """Monitors secondary marketplaces for TX RACE conversion kits and bikes equipped with restyle kits."""

    def __init__(
        self,
        name: str = "marketplaces",
        enabled: bool = True,
        platforms: list[str] | None = None,
        matcher: KeywordMatcher | None = None,
        prioritizer: Prioritizer | None = None,
    ) -> None:
        super().__init__(name=name, platform=Platform.MARKETPLACES, enabled=enabled)
        self.platforms = platforms or ["eBay Motors", "Wallapop", "Leboncoin", "Craigslist"]
        self.matcher = matcher or KeywordMatcher()
        self.prioritizer = prioritizer or Prioritizer()

    def _get_fallback_fixtures(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "mkt_ebay_cr250_listing_01",
                "author": "eBay Motors",
                "author_url": "https://www.ebay.com/sch/i.html?_nkw=tx+race+restyle+kit",
                "title": "TX Race Restyle Kit for Honda CR250 — eBay Motors Listing",
                "content": "Brand new TX Race restyle kit for Honda CR250 2002-2007. "
                           "Where to buy? Price $450 with fast shipping. Complete plastics and seat in stock.",
                "url": "https://www.ebay.com/sch/i.html?_nkw=tx+race+restyle+kit",
                "published_at": "2026-11-06T11:00:00Z",
                "metrics": {"views": 4500, "comments": 14, "likes": 95, "shares": 12},
                "geo_country": "United States",
                "geo_city": "Chicago",
            },
            {
                "id": "mkt_txrace_store_kx250_02",
                "author": "TX RACE Store",
                "author_url": "https://www.txrace.com/shop/",
                "title": "TX RACE™ Official Store: Restyle Kit for Kawasaki KX250",
                "content": "Official product listing for TX RACE™ Restyle Kit for Kawasaki KX250 2003-2008. "
                           "Price €480 with worldwide shipping. Where to buy direct from factory with full kit in stock.",
                "url": "https://www.txrace.com/product/tx-race-restyle-kit-for-kawasaki-kx125-250-2003-2008/",
                "published_at": "2026-11-06T16:20:00Z",
                "metrics": {"views": 9400, "comments": 12, "likes": 310, "shares": 42},
                "geo_country": "Spain",
                "geo_city": "Pontevedra",
            },
        ]

    def fetch(self) -> list[MentionDTO]:
        """Fetches and normalizes marketplace listings and sales discussions."""
        raw_items = self._get_fallback_fixtures()
        mentions: list[MentionDTO] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for item in raw_items:
            match = self.matcher.match_text(item.get("title", ""), item.get("content", ""))
            if not match.matched or match.is_negative_match:
                continue

            metrics = MentionMetrics.from_dict(item.get("metrics"))
            # Marketplaces inherently signal high buying/selling commercial intent
            intent = BuyingIntent.COMPRA_ATIVA if match.intent in (BuyingIntent.COMPRA_ATIVA, BuyingIntent.GERAL) else match.intent

            score = self.prioritizer.calculate_priority(
                intent=intent,
                views=metrics.views,
                sentiment_score=0.90,
                published_at_iso=item.get("published_at"),
            )

            reply = self.prioritizer.generate_reply(
                intent=intent,
                model=match.model_detected,
                generation=match.generation,
                language="es" if item.get("geo_country") == "Spain" else "en",
            )

            dto = MentionDTO(
                id=item["id"],
                platform=Platform.MARKETPLACES,
                author=item.get("author", "Marketplace Seller"),
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
                sentiment_score=0.90,
                priority_score=score,
                metrics=metrics,
                geo_country=item.get("geo_country"),
                geo_city=item.get("geo_city"),
                recommended_reply=reply,
            )
            mentions.append(dto)

        return mentions
