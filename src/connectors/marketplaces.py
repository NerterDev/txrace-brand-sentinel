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
                "author": "VintageMotoParts_USA",
                "author_url": "https://www.ebay.com/usr/vintagemotoparts_usa",
                "title": "TX Race Restyle Conversion Kit for Honda CR250 2002-2007 (New in Box)",
                "content": "Brand new TX Race restyle kit in original packaging. Includes front fender, side panels, "
                           "rear fender, airbox brackets and seat foam. Where can I buy graphics? Template included. Price $450.",
                "url": "https://www.ebay.com/itm/182947192847",
                "published_at": "2026-11-06T11:00:00Z",
                "metrics": {"views": 1850, "comments": 12, "likes": 48, "shares": 5},
                "geo_country": "United States",
                "geo_city": "Chicago",
            },
            {
                "id": "mkt_wallapop_kx250_spain_02",
                "author": "Carlos_MX_BCN",
                "author_url": "https://es.wallapop.com/user/carlosmx-1829",
                "title": "Kawasaki KX250 2003 con kit TX Race Restyle montado",
                "content": "Vendo KX250 2T en perfecto estado con kit TX Race recién instalado. Precio 3.200€. "
                           "Comprado directamente en tienda oficial TX Race. Se puede ver y probar.",
                "url": "https://es.wallapop.com/item/kawasaki-kx250-tx-race-8918274",
                "published_at": "2026-11-06T16:20:00Z",
                "metrics": {"views": 920, "comments": 15, "likes": 34, "shares": 4},
                "geo_country": "Spain",
                "geo_city": "Barcelona",
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
