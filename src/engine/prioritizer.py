"""Scoring algorithm for brand mention priority and automated recommended response generation."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from src.models.mention import BuyingIntent, MentionDTO


class Prioritizer:
    """Calculates engagement and commercial priority scores and generates recommended replies."""

    def __init__(self, settings_dict: dict[str, Any] | None = None, settings_path: str = "config/settings.yaml") -> None:
        if settings_dict:
            self.settings = settings_dict
        else:
            cfg_file = Path(settings_path)
            if cfg_file.exists():
                self.settings = yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
            else:
                self.settings = {}

        weights = self.settings.get("engine", {}).get("priority_weights", {})
        self.w_intent = float(weights.get("buying_intent", 40.0))
        self.w_engagement = float(weights.get("viral_engagement", 30.0))
        self.w_sentiment = float(weights.get("sentiment_bonus", 15.0))
        self.w_freshness = float(weights.get("freshness", 15.0))

    def calculate_priority(
        self,
        intent: BuyingIntent,
        views: int = 0,
        sentiment_score: float = 0.5,
        published_at_iso: str | None = None,
    ) -> float:
        """Calculates a normalized priority score between 0.0 and 100.0."""
        # 1. Intent score (max 40 pts)
        intent_factors = {
            BuyingIntent.COMPRA_ATIVA: 1.0,    # 40 pts
            BuyingIntent.VIRAL: 0.9,           # 36 pts
            BuyingIntent.DUVIDA_TECNICA: 0.7,   # 28 pts
            BuyingIntent.PROJETO_BUILD: 0.65,  # 26 pts
            BuyingIntent.GERAL: 0.25,          # 10 pts
        }
        intent_pts = self.w_intent * intent_factors.get(intent, 0.25)

        # 2. Viral engagement score (max 30 pts)
        if views >= 50000:
            eng_factor = 1.0
        elif views >= 10000:
            eng_factor = 0.85
        elif views >= 2500:
            eng_factor = 0.6
        elif views >= 500:
            eng_factor = 0.35
        elif views >= 50:
            eng_factor = 0.15
        else:
            eng_factor = 0.05
        eng_pts = self.w_engagement * eng_factor

        # 3. Sentiment score (max 15 pts)
        clamped_sentiment = max(0.0, min(1.0, float(sentiment_score)))
        sent_pts = self.w_sentiment * clamped_sentiment

        # 4. Freshness score (max 15 pts)
        fresh_factor = 0.5  # default
        if published_at_iso:
            try:
                # Handle ISO 8601 parsing
                clean_iso = published_at_iso.replace("Z", "+00:00")
                pub_dt = datetime.fromisoformat(clean_iso)
                if pub_dt.tzinfo is None:
                    pub_dt = pub_dt.replace(tzinfo=timezone.utc)
                now_dt = datetime.now(timezone.utc)
                age_days = (now_dt - pub_dt).total_seconds() / 86400.0

                if age_days <= 1.0:
                    fresh_factor = 1.0
                elif age_days <= 3.0:
                    fresh_factor = 0.8
                elif age_days <= 7.0:
                    fresh_factor = 0.6
                elif age_days <= 14.0:
                    fresh_factor = 0.35
                elif age_days <= 30.0:
                    fresh_factor = 0.2
                else:
                    fresh_factor = 0.05
            except Exception:
                fresh_factor = 0.5

        fresh_pts = self.w_freshness * fresh_factor

        total = round(intent_pts + eng_pts + sent_pts + fresh_pts, 1)
        return max(0.0, min(100.0, total))

    def generate_reply(
        self,
        intent: BuyingIntent,
        model: str = "your bike",
        generation: str | None = None,
        language: str = "en",
    ) -> str:
        """Generates tailored copy-paste official responses in EN, PT, or ES."""
        lang = language.lower()[:2]
        gen_str = f" {generation}" if generation else ""
        bike_str = model if model != "UNKNOWN" else "your bike"

        if lang == "pt":
            if intent == BuyingIntent.COMPRA_ATIVA:
                return (
                    f"Olá! O kit TX RACE Restyle para {bike_str}{gen_str} está disponível com envio mundial direto na nossa loja oficial: "
                    f"https://txrace.com — Se tiveres dúvidas sobre compatibilidade de ano ou peças incluídas, envia-nos mensagem privada!"
                )
            elif intent == BuyingIntent.DUVIDA_TECNICA:
                return (
                    f"Olá! Os kits TX RACE para {bike_str} foram concebidos com montagem 'bolt-on' no subquadro original. "
                    f"Podes consultar o guia passo a passo em https://txrace.com/manuals ou falar com o nosso suporte técnico!"
                )
            elif intent == BuyingIntent.PROJETO_BUILD:
                return (
                    f"Grande projeto de transformação na {bike_str}! Excelente trabalho. "
                    f"Identifica @txrace no Instagram ou TikTok para partilharmos a tua moto na nossa página oficial!"
                )
            else:
                return f"Obrigado por mencionares a TX RACE! Sabe mais sobre kits de restyle para {bike_str} em https://txrace.com"

        elif lang == "es":
            if intent == BuyingIntent.COMPRA_ATIVA:
                return (
                    f"¡Hola! El kit TX RACE Restyle para {bike_str}{gen_str} está disponible con envío internacional directo en nuestra tienda oficial: "
                    f"https://txrace.com — ¡Cualquier duda con el año o el montaje, estamos a tu disposición!"
                )
            elif intent == BuyingIntent.DUVIDA_TECNICA:
                return (
                    f"¡Hola! Los kits TX RACE para {bike_str} están diseñados para encaje directo 'bolt-on'. "
                    f"Puedes ver las instrucciones detalladas de montaje en https://txrace.com/manuals"
                )
            elif intent == BuyingIntent.PROJETO_BUILD:
                return (
                    f"¡Increíble transformación en esa {bike_str}! Gran trabajo. "
                    f"¡Etiquétanos en @txrace para compartir tu proyecto en nuestras redes!"
                )
            else:
                return f"¡Gracias por mencionar a TX RACE! Descubre más kits para {bike_str} en https://txrace.com"

        else:  # Default: English
            if intent == BuyingIntent.COMPRA_ATIVA:
                return (
                    f"Hey there! The official TX RACE Restyle kit for {bike_str}{gen_str} is available with worldwide shipping at "
                    f"https://txrace.com — Feel free to check fitment guides or drop us a DM if you need help with your year/model!"
                )
            elif intent == BuyingIntent.DUVIDA_TECNICA:
                return (
                    f"Hey! TX RACE restyle kits for {bike_str} are engineered as a bolt-on conversion using the OEM subframe. "
                    f"You can check our step-by-step install manual at https://txrace.com/manuals or contact support directly!"
                )
            elif intent == BuyingIntent.PROJETO_BUILD:
                return (
                    f"Awesome transformation on that {bike_str}! Looks super clean. "
                    f"Tag @txrace on Instagram or TikTok so we can feature your build!"
                )
            else:
                return f"Thanks for shouting out TX RACE! Check out all restyle kits for {bike_str} at https://txrace.com"

    def enrich(self, mention: MentionDTO, language: str = "en") -> MentionDTO:
        """Enriches mention with computed priority score and recommended reply."""
        views = mention.metrics.views if mention.metrics else 0
        score = self.calculate_priority(
            intent=mention.intent,
            views=views,
            sentiment_score=mention.sentiment_score,
            published_at_iso=mention.published_at,
        )
        reply = self.generate_reply(
            intent=mention.intent,
            model=mention.model_detected,
            generation=mention.generation,
            language=language,
        )

        data = mention.to_dict()
        data["priority_score"] = score
        data["recommended_reply"] = reply
        return MentionDTO.from_dict(data)

