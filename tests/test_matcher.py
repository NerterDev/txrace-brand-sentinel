"""Deterministic unit tests for KeywordMatcher, official brand exclusion, and entity extraction."""
import unittest

from src.engine.matcher import KeywordMatcher
from src.models.mention import BuyingIntent, MentionDTO, MentionMetrics, Platform, Sentiment


class TestKeywordMatcher(unittest.TestCase):
    def setUp(self) -> None:
        self.matcher = KeywordMatcher()

    def test_direct_brand_and_honda_cr125_gen25_match(self) -> None:
        title = "CR125 Transformation with TXRACE!"
        content = "Fitment on the 2003 CR was dead simple, seat is amazing. New Gen25 kit looks killer."
        result = self.matcher.match_text(title, content)

        self.assertTrue(result.matched)
        self.assertFalse(result.is_negative_match)
        self.assertEqual(result.brand_detected, "Honda")
        self.assertEqual(result.model_detected, "CR125")
        self.assertEqual(result.generation, "Gen25")
        self.assertEqual(result.intent, BuyingIntent.PROJETO_BUILD)

    def test_honda_crf250r_alias_detection(self) -> None:
        title = "TX Race Plastics Kit on a 2004 CRF250 Build"
        content = "Installing the TX Race restyle kit on a 2004 Honda CRF250R in Southern California."
        result = self.matcher.match_text(title, content)

        self.assertTrue(result.matched)
        self.assertEqual(result.brand_detected, "Honda")
        self.assertEqual(result.model_detected, "CRF250R")
        self.assertEqual(result.intent, BuyingIntent.PROJETO_BUILD)

    def test_buying_intent_detection(self) -> None:
        title = "New TX Race Restyle Kit for CRF250X"
        content = "Where can I order the restyle kit in Canada? Is shipping fast and how much does it cost?"
        result = self.matcher.match_text(title, content)

        self.assertTrue(result.matched)
        self.assertEqual(result.brand_detected, "Honda")
        self.assertEqual(result.model_detected, "CRF250X")
        self.assertEqual(result.intent, BuyingIntent.COMPRA_ATIVA)

    def test_technical_question_intent_and_kawasaki(self) -> None:
        title = "Anyone tried TX Race on 97 KX?"
        content = "Is the seat foam comfortable for long motos? How is the subframe fitment on KX250?"
        result = self.matcher.match_text(title, content)

        self.assertTrue(result.matched)
        self.assertEqual(result.brand_detected, "Kawasaki")
        self.assertEqual(result.model_detected, "KX250")
        self.assertEqual(result.intent, BuyingIntent.DUVIDA_TECNICA)

    def test_negative_filters_rejection(self) -> None:
        title = "Awesome results from the NASCAR TX Race today!"
        content = "The texas race track was wild during the 500 race."
        result = self.matcher.match_text(title, content)

        self.assertFalse(result.matched)
        self.assertTrue(result.is_negative_match)
        self.assertIn("nascar tx race", result.matched_keywords)

    def test_generic_text_without_brand_rejected(self) -> None:
        title = "Riding my 2004 CR250 in the dunes"
        content = "Just stock plastics, no aftermarket conversions today."
        result = self.matcher.match_text(title, content)

        self.assertFalse(result.matched)
        self.assertFalse(result.is_negative_match)

    def test_official_brand_sources_are_rejected(self) -> None:
        self.assertTrue(
            self.matcher.is_official_brand_source(
                "TX RACE", "https://www.youtube.com/watch?v=Egi65jNdJt8", "https://www.youtube.com/@txracecom"
            )
        )
        self.assertTrue(
            self.matcher.is_official_brand_source(
                "@txrace", "https://www.tiktok.com/@txrace", "https://www.tiktok.com/@txrace"
            )
        )
        self.assertTrue(
            self.matcher.is_official_brand_source(
                "TX RACE Store", "https://www.txrace.com/product/kx250/", "https://www.txrace.com/shop/"
            )
        )
        self.assertFalse(
            self.matcher.is_official_brand_source(
                "Chase Builds Bikes",
                "https://www.youtube.com/watch?v=4GT4yEOszmE",
                "https://www.youtube.com/@ChaseBuiltBikes",
            )
        )

        official_mention = MentionDTO(
            id="official-1",
            platform=Platform.YOUTUBE,
            author="TX RACE",
            author_url="https://www.youtube.com/@txracecom",
            title="TX RACE Restyle Kit Gen24 for Kawasaki KX250",
            content="Official factory release video from TX RACE.",
            url="https://www.youtube.com/watch?v=Egi65jNdJt8",
            published_at="2026-11-06T10:00:00Z",
            scraped_at="2026-11-06T10:05:00Z",
            model_detected="KX250",
            brand_detected="Kawasaki",
            intent=BuyingIntent.GERAL,
            sentiment=Sentiment.POSITIVE,
            sentiment_score=0.9,
            priority_score=80.0,
            metrics=MentionMetrics(views=3350),
        )
        self.assertIsNone(self.matcher.enrich_mention(official_mention))

    def test_enrich_mention_lifecycle(self) -> None:
        raw_mention = MentionDTO(
            id="raw-1",
            platform=Platform.REDDIT,
            author="MotocrossGuy",
            title="Installed the TX-Race Gen2 kit on my YZ250",
            content="Check out the transformation, before and after build photos inside!",
            url="https://www.reddit.com/r/Dirtbikes/comments/123",
            published_at="2026-11-06T10:00:00Z",
            scraped_at="2026-11-06T10:05:00Z",
            model_detected="UNKNOWN",
            brand_detected="TX RACE",
            intent=BuyingIntent.GERAL,
            sentiment=Sentiment.POSITIVE,
            sentiment_score=0.9,
            priority_score=50.0,
            metrics=MentionMetrics(views=350),
        )

        enriched = self.matcher.enrich_mention(raw_mention)
        self.assertIsNotNone(enriched)
        assert enriched is not None
        self.assertEqual(enriched.brand_detected, "Yamaha")
        self.assertEqual(enriched.model_detected, "YZ250")
        self.assertEqual(enriched.generation, "Gen2")
        self.assertEqual(enriched.intent, BuyingIntent.PROJETO_BUILD)


if __name__ == "__main__":
    unittest.main()
