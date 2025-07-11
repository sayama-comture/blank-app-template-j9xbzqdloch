import logging

from app.repositories.bot_store import (
    find_bots_by_query,
    find_bots_sorted_by_usage_count,
    find_random_bots,
    find_all_bots_by_query # 新規追加
)
from app.routes.schemas.bot import BotMetaOutput
from app.routes.schemas.bot_guardrails import BedrockGuardrailsOutput
from app.routes.schemas.bot_kb import BedrockKnowledgeBaseOutput
from app.user import User

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 修正 ---
def search_bots(
    user: User,
    query: str,
    limit: int = 20,
) -> list:
    """Search bots by query string."""
    bots = find_bots_by_query(
        query,
        user,
        limit=limit,
    )
    return bots
# 修正 ---

# 新規追加 -----
def search_all_bots(
    query: str,
    limit: int =20,
) -> list[BotMetaOutput]:
    """Search bots by query string."""
    bots = find_all_bots_by_query(
        query,
        limit=limit,
    )
    return bots
# 新規追加 -----

def fetch_popular_bots(
    user: User,
    limit: int = 20,
) -> list[BotMetaOutput]:
    """Search bots sorted by usage count.
    This method is used for bot-store functionality (Popular bots).
    """
    bots = find_bots_sorted_by_usage_count(
        user,
        limit=limit,
    )
    bot_metas = []
    for bot in bots:
        bot_metas.append(bot.to_output())
    return bot_metas


def fetch_pickup_bots(
    user: User,
    limit: int = 20,
) -> list[BotMetaOutput]:
    """Search bots sorted by usage count.
    This method is used for bot-store functionality (Today's pickup bots).
    """
    bots = find_random_bots(
        user,
        limit=limit,
    )
    bot_metas = []
    for bot in bots:
        bot_metas.append(bot.to_output())
    return bot_metas
