"""Connectors module for TX RACE Brand Sentinel (Full 10-Connector Suite)."""
from src.connectors.base import BaseConnector, ConnectorResult, ConnectorStatus
from src.connectors.facebook import FacebookConnector
from src.connectors.forums import ForumsConnector
from src.connectors.instagram import InstagramConnector
from src.connectors.marketplaces import MarketplacesConnector
from src.connectors.reddit import RedditConnector
from src.connectors.registry import ConnectorRegistry, default_registry
from src.connectors.rss_web import RssWebConnector
from src.connectors.tiktok import TikTokConnector
from src.connectors.twitter import TwitterConnector
from src.connectors.youtube import YouTubeConnector

__all__ = [
    "BaseConnector",
    "ConnectorResult",
    "ConnectorStatus",
    "ConnectorRegistry",
    "default_registry",
    "YouTubeConnector",
    "TikTokConnector",
    "InstagramConnector",
    "FacebookConnector",
    "RedditConnector",
    "ForumsConnector",
    "MarketplacesConnector",
    "TwitterConnector",
    "RssWebConnector",
]
