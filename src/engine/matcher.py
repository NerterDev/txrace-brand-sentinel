"""Keyword matching, brand detection, motorcycle model extraction and negative filtering."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from src.models.mention import BuyingIntent, MentionDTO


@dataclass(frozen=True)
class MatchResult:
    """Result of evaluating text against TX RACE brand sentinel keywords."""
    matched: bool
    brand_detected: str = "TX RACE"
    model_detected: str = "UNKNOWN"
    generation: str | None = None
    intent: BuyingIntent = BuyingIntent.GERAL
    is_negative_match: bool = False
    matched_keywords: list[str] = field(default_factory=list)


class KeywordMatcher:
    """High-performance keyword matcher and semantic classifier."""

    def __init__(self, config_dict: dict[str, Any] | None = None, config_path: str = "config/keywords.yaml") -> None:
        if config_dict:
            self.config = config_dict
        else:
            cfg_file = Path(config_path)
            if cfg_file.exists():
                self.config = yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
            else:
                self.config = {}

        self._compile_patterns()

    def _compile_patterns(self) -> None:
        # 1. Negative filters
        self.negative_filters = [
            phrase.strip().lower() for phrase in self.config.get("negative_filters", []) if phrase
        ]

        # 2. Primary brand queries
        brand_queries = self.config.get("brand_queries", {}).get("primary", ["txrace", "tx race", "tx-race"])
        self.brand_regexes = [
            re.compile(r"\b" + re.escape(q.lower()) + r"\b", re.IGNORECASE) for q in brand_queries
        ]

        # 3. Models
        # Structure: [(brand_name, model_id, [compiled_regexes])]
        self.model_matchers: list[tuple[str, str, list[re.Pattern[str]]]] = []
        models_data = self.config.get("models", {})
        for brand_key, brand_info in models_data.items():
            brand_name = brand_info.get("brand", brand_key.capitalize())
            for target in brand_info.get("targets", []):
                model_id = target.get("id")
                aliases = target.get("aliases", []) + [model_id]
                patterns = []
                for alias in aliases:
                    # Clean alias into regex with word boundary
                    pattern_str = r"\b" + re.escape(alias.lower()) + r"\b"
                    patterns.append(re.compile(pattern_str, re.IGNORECASE))
                self.model_matchers.append((brand_name, model_id, patterns))

        # 4. Generations
        self.generation_matchers: list[tuple[str, list[re.Pattern[str]]]] = []
        for gen in self.config.get("generations", []):
            gen_id = gen.get("id")
            aliases = gen.get("aliases", []) + [gen_id]
            patterns = [re.compile(r"\b" + re.escape(a.lower()) + r"\b", re.IGNORECASE) for a in aliases]
            self.generation_matchers.append((gen_id, patterns))

        # 5. Intents
        self.intent_matchers: list[tuple[BuyingIntent, list[str]]] = []
        intents_data = self.config.get("intents", {})
        for intent_name, intent_info in intents_data.items():
            try:
                intent_enum = BuyingIntent(intent_name)
                keywords = [kw.lower() for kw in intent_info.get("keywords", [])]
                self.intent_matchers.append((intent_enum, keywords))
            except ValueError:
                continue

        # 6. Official brand source exclusions (strictly third-party listening)
        default_excluded_authors = [
            "tx race",
            "txrace",
            "tx-race",
            "@txrace",
            "@txracecom",
            "txracecom",
            "tx race official",
            "tx race official (@txracecom)",
            "tx race store",
            "tx race technical guide",
            "baudea global",
        ]
        raw_excluded_authors = self.config.get("excluded_authors", default_excluded_authors)
        self.excluded_authors: set[str] = {
            str(a).strip().lower() for a in raw_excluded_authors if a
        }

        default_excluded_domains = ["txrace.com", "www.txrace.com"]
        raw_excluded_domains = self.config.get("excluded_domains", default_excluded_domains)
        self.excluded_domains: set[str] = {
            str(d).strip().lower() for d in raw_excluded_domains if d
        }

    def is_official_brand_source(
        self,
        author: str,
        url: str,
        author_url: str | None = None,
    ) -> bool:
        """Returns True if a mention originates from TX RACE's own official channels or website."""
        norm_author = (author or "").strip().lower()
        norm_handle = norm_author.lstrip("@").strip()

        if norm_author in self.excluded_authors or norm_handle in self.excluded_authors:
            return True

        # Catch composite official labels like "TX RACE Official (@txracecom)"
        if "txracecom" in norm_author or norm_author.startswith("tx race official") or norm_author.startswith("tx race store"):
            return True

        for candidate_url in (url, author_url):
            if not candidate_url:
                continue
            try:
                parsed = urlparse(candidate_url.strip())
                host = (parsed.hostname or "").lower()
                path_lower = (parsed.path or "").lower()
            except ValueError:
                continue

            if host in self.excluded_domains or host.endswith(".txrace.com"):
                return True

            # Catch official social profile URLs
            for official_slug in ("/@txracecom", "/txracecom", "/@txrace", "/txrace"):
                if path_lower == official_slug or path_lower.startswith(official_slug + "/"):
                    return True

        return False

    def match_text(self, title: str, content: str) -> MatchResult:
        """Evaluates combined title and content against rules and filters."""
        combined_text = f"{title} {content}".lower()

        # Step 1: Check negative filters (instant rejection)
        matched_negatives = [neg for neg in self.negative_filters if neg in combined_text]
        if matched_negatives:
            return MatchResult(
                matched=False,
                is_negative_match=True,
                matched_keywords=matched_negatives,
            )

        # Step 2: Check brand presence
        brand_matched = False
        matched_brand_terms = []
        for rgx in self.brand_regexes:
            found = rgx.findall(combined_text)
            if found:
                brand_matched = True
                matched_brand_terms.extend(found)

        if not brand_matched:
            return MatchResult(matched=False)

        # Step 3: Extract Model and Motorcycle Brand
        detected_bike_brand = "TX RACE"
        detected_model = "UNKNOWN"
        for brand_name, model_id, patterns in self.model_matchers:
            for pat in patterns:
                if pat.search(combined_text):
                    detected_bike_brand = brand_name
                    detected_model = model_id
                    break
            if detected_model != "UNKNOWN":
                break

        # Step 4: Extract Generation
        detected_gen = None
        for gen_id, patterns in self.generation_matchers:
            for pat in patterns:
                if pat.search(combined_text):
                    detected_gen = gen_id
                    break
            if detected_gen:
                break

        # Step 5: Classify Intent
        detected_intent = BuyingIntent.GERAL
        for intent_enum, kw_list in self.intent_matchers:
            for kw in kw_list:
                if kw in combined_text:
                    detected_intent = intent_enum
                    break
            if detected_intent != BuyingIntent.GERAL:
                break

        return MatchResult(
            matched=True,
            brand_detected=detected_bike_brand,
            model_detected=detected_model,
            generation=detected_gen,
            intent=detected_intent,
            is_negative_match=False,
            matched_keywords=list(set(matched_brand_terms)),
        )

    def enrich_mention(self, mention: MentionDTO) -> MentionDTO | None:
        """Enriches an existing MentionDTO with semantic extracted metadata or drops if invalid."""
        if self.is_official_brand_source(mention.author, mention.url, mention.author_url):
            return None

        res = self.match_text(mention.title, mention.content)
        if not res.matched or res.is_negative_match:
            return None

        # Return updated immutable MentionDTO
        raw_dict = mention.to_dict()
        raw_dict["brand_detected"] = res.brand_detected
        raw_dict["model_detected"] = res.model_detected
        raw_dict["generation"] = res.generation
        raw_dict["intent"] = res.intent.value

        return MentionDTO.from_dict(raw_dict)
