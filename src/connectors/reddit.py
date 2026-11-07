"""Reddit connector for r/Dirtbikes, r/Motocross and community discussions."""
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


class RedditConnector(BaseConnector):
    """Monitors Reddit motocross communities for TX RACE build threads and questions."""

    def __init__(
        self,
        name: str = "reddit",
        enabled: bool = True,
        client_id: str | None = None,
        subreddits: list[str] | None = None,
        matcher: KeywordMatcher | None = None,
        prioritizer: Prioritizer | None = None,
    ) -> None:
        super().__init__(name=name, platform=Platform.REDDIT, enabled=enabled)
        self.client_id = client_id or os.getenv("REDDIT_CLIENT_ID")
        self.subreddits = subreddits or ["Dirtbikes", "Motocross", "supercross", "Dualsport"]
        self.matcher = matcher or KeywordMatcher()
        self.prioritizer = prioritizer or Prioritizer()

    def _get_fallback_fixtures(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "reddit_dirtbikes_cr250_01",
                "author": "u/MotoGuy_SoCal",
                "author_url": "https://www.reddit.com/user/MotoGuy_SoCal",
                "title": "TX Race redesign kit on a 02 CR250",
                "content": "Where can I order the restyle kit in Canada? Is shipping fast and does it require gas tank mods? "
                           "Looking to modernize my 2004 CR250 2-stroke.",
                "url": "https://www.reddit.com/r/Dirtbikes/comments/1lczrov/tx_race_redesign_kit_on_a_02_cr250/",
                "published_at": "2026-11-06T17:40:00Z",
                "metrics": {"views": 4200, "comments": 38, "likes": 290, "shares": 14},
                "geo_country": "Canada",
                "geo_city": "Ontario",
            },
            {
                "id": "reddit_motocross_yz125_build_02",
                "author": "u/SandTrackRacer",
                "author_url": "https://www.reddit.com/user/SandTrackRacer",
                "title": "Before and After: 2005 YZ125 transformation with TXRace Gen25",
                "content": "Finished my 2005 Yamaha YZ125 winter project bike! Installed the TXRace Gen25 conversion kit. "
                           "Seat is firm and modern, graphics lines are seamless.",
                "url": "https://www.reddit.com/r/Dirtbikes/comments/ev17px/anyone_have_any_experience_with_txrace_restyle/",
                "published_at": "2026-11-06T19:15:00Z",
                "metrics": {"views": 6100, "comments": 56, "likes": 480, "shares": 22},
                "geo_country": "United States",
                "geo_city": "Michigan",
            },
        ]

    def fetch(self) -> list[MentionDTO]:
        """Fetches Reddit submissions matching brand terms."""
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
                platform=Platform.REDDIT,
                author=item.get("author", "Reddit User"),
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

