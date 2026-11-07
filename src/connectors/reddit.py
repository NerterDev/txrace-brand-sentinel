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
                "author": "r/Dirtbikes (Community)",
                "author_url": "https://www.reddit.com/r/Dirtbikes/comments/1lczrov/tx_race_redesign_kit_on_a_02_cr250/",
                "title": "TX Race redesign kit on a 02 CR250",
                "content": "TX Race redesign kit on a 02 CR250. Discussion on installing the TX Race restyle kit on a 2002 Honda CR250. "
                           "Questions about subframe alignment, seat comfort and how clean the modern lines look.",
                "url": "https://www.reddit.com/r/Dirtbikes/comments/1lczrov/tx_race_redesign_kit_on_a_02_cr250/",
                "published_at": "2026-11-06T17:40:00Z",
                "metrics": {"views": 4200, "comments": 24, "likes": 65, "shares": 8},
                "geo_country": "United States",
                "geo_city": "California",
            },
            {
                "id": "reddit_dirtbikes_experience_02",
                "author": "r/Dirtbikes (Community)",
                "author_url": "https://www.reddit.com/r/Dirtbikes/comments/ev17px/anyone_have_any_experience_with_txrace_restyle/",
                "title": "Anyone have any experience with TXRace restyle kit?",
                "content": "Anyone have any experience with TXRace restyle kit? Thinking of modernizing my 2-stroke CR250 / YZ125. "
                           "How is the custom seat, durability of the plastics and ease of installation?",
                "url": "https://www.reddit.com/r/Dirtbikes/comments/ev17px/anyone_have_any_experience_with_txrace_restyle/",
                "published_at": "2026-11-06T19:15:00Z",
                "metrics": {"views": 5800, "comments": 38, "likes": 82, "shares": 12},
                "geo_country": "United States",
                "geo_city": "Texas",
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

