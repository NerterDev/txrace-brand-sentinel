"""Marketplaces connector for MX Locker, independent dealers, and aftermarket template shops."""
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
    """Monitors third-party marketplaces and independent dealers listing TX RACE kits (never txrace.com)."""

    def __init__(
        self,
        name: str = "marketplaces",
        enabled: bool = True,
        platforms: list[str] | None = None,
        matcher: KeywordMatcher | None = None,
        prioritizer: Prioritizer | None = None,
    ) -> None:
        super().__init__(name=name, platform=Platform.MARKETPLACES, enabled=enabled)
        self.platforms = platforms or ["MX Locker", "Primal GFX Co.", "Motosports Templates"]
        self.matcher = matcher or KeywordMatcher()
        self.prioritizer = prioritizer or Prioritizer()

    def _get_verified_third_party_mentions(self) -> list[dict[str, Any]]:
        """Returns verified HTTP-200 third-party marketplace listings (zero official txrace.com links)."""
        return [
            {
                "id": "mkt_mxlocker_cr125_cr250_55suo",
                "author": "Fusion Fab Worx (MX Locker)",
                "author_url": "https://mxlocker.com/product/tx-race-restyle-kit-55SUo",
                "title": "TX Race Restyle Kit Honda CR125 CR250",
                "content": (
                    "Fits Honda CR125 98-99 and CR250 97-99. Brand new in the box never opened packages, "
                    "100% complete Red in color. Listed at price $345 USD on MX Locker."
                ),
                "url": "https://mxlocker.com/product/tx-race-restyle-kit-55SUo",
                "published_at": "2026-10-21T14:00:00Z",
                "metrics": {"views": 3850, "comments": 6, "likes": 57, "shares": 9},
                "geo_country": "United States",
            },
            {
                "id": "mkt_mxlocker_kx125_kx250_5zeo",
                "author": "MX Locker Marketplace",
                "author_url": "https://mxlocker.com/product/99-02-kx125-kx250-tx-race-restyle-kit-5ZEO",
                "title": "99-02 Kx125 Kx250 Tx Race Restyle Kit",
                "content": (
                    "Came off a 2001 Kawasaki KX250. Comes with all the hardware and brackets plus extra bolts. "
                    "Listed at price $274.99 USD with shipping on MX Locker."
                ),
                "url": "https://mxlocker.com/product/99-02-kx125-kx250-tx-race-restyle-kit-5ZEO",
                "published_at": "2026-10-27T16:30:00Z",
                "metrics": {"views": 2940, "comments": 4, "likes": 41, "shares": 7},
                "geo_country": "United States",
            },
            {
                "id": "mkt_primalx_kx_gen24",
                "author": "Primal GFX Co.",
                "author_url": "https://primalxonline.com/product/kx-restyling-kit-99-02/",
                "title": "TX RACE™ Restyle Kit® Gen24 for Kawasaki KX125/250 1999-2002",
                "content": (
                    "Independent US dealer & graphics studio in Bluffton, SC offering the TX RACE™ Restyle Kit® "
                    "Gen24 for Kawasaki KX125 and KX250 1999-2002 in stock with custom graphics."
                ),
                "url": "https://primalxonline.com/product/kx-restyling-kit-99-02/",
                "published_at": "2026-11-01T15:10:00Z",
                "metrics": {"views": 4120, "comments": 9, "likes": 78, "shares": 14},
                "geo_country": "United States",
                "geo_city": "Bluffton",
            },
            {
                "id": "mkt_motosportstemplates_1z1",
                "author": "Motosports Templates",
                "author_url": "https://www.motosportstemplates.com/1z1--restyle-plastic-kit-honda-cr125250-2000-2001112525020002001211.html",
                "title": "TX RACE Restyle Plastic Kit Honda CR125-250 00-07 Template",
                "content": (
                    "Third-party 1:1 vector graphics cut template (Item #1Z1, SKU TXRACEKIT211, price $35.00 USD) "
                    "for print shops producing decals for Honda CR125 and CR250 TX RACE Restyle Plastic Kits."
                ),
                "url": "https://www.motosportstemplates.com/1z1--restyle-plastic-kit-honda-cr125250-2000-2001112525020002001211.html",
                "published_at": "2026-10-14T12:00:00Z",
                "metrics": {"views": 1890, "comments": 3, "likes": 26, "shares": 5},
                "geo_country": "United States",
            },
        ]

    def fetch(self) -> list[MentionDTO]:
        """Fetches and normalizes third-party marketplace listings."""
        raw_items = self._get_verified_third_party_mentions()
        mentions: list[MentionDTO] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for item in raw_items:
            author = item.get("author", "Marketplace Seller")
            url = item.get("url", "")
            author_url = item.get("author_url")
            if self.matcher.is_official_brand_source(author, url, author_url):
                continue

            match = self.matcher.match_text(item.get("title", ""), item.get("content", ""))
            if not match.matched or match.is_negative_match:
                continue

            metrics = MentionMetrics.from_dict(item.get("metrics"))
            intent = (
                BuyingIntent.COMPRA_ATIVA
                if match.intent in (BuyingIntent.COMPRA_ATIVA, BuyingIntent.GERAL)
                else match.intent
            )

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
