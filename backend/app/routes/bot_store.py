from app.routes.schemas.bot import BotMetaOutput, BotMetaOutputWithOwnerId # 新規追加
from app.usecases.bot_store import fetch_pickup_bots, fetch_popular_bots, search_bots
from app.user import User
from fastapi import APIRouter, Depends, Request

router = APIRouter(tags=["bot_store"])

# 修正 ---
@router.get("/store/search", response_model=list[BotMetaOutputWithOwnerId])
def search_bots_by_query(
    request: Request,
    query: str,
    limit: int = 20,
):
    """Search bots by query string.
    - This method is used for bot-store functionality.
    - Results include private bots if the user is the owner.
    - Only accessible bots are returned.
    - If admin, partial shared bots not accessible by the admin are returned.
    """
    current_user: User = request.state.current_user

    bots = search_bots(current_user, query, limit)
    bot_metas = []
    for bot in bots:
        items = BotMetaOutputWithOwnerId(
            id=bot["BotId"],
            title=bot["Title"],
            description=bot["Description"],
            createTime=bot["CreateTime"],
            last_used_time=bot.get("LastUsedTime", bot["CreateTime"]),
            owner_user_id=bot["PK"],
            is_starred=bot.get("IsStarred", False),
            owned=bot["PK"] == current_user.id,
            available=True,
            syncStatus=bot["SyncStatus"],
            shared_scope=bot.get("SharedScope", None),
            shared_status=bot.get("SharedStatus", None)
        )
        bot_metas.append(items)
        
    return bot_metas
# 修正 ---


@router.get("/store/popular", response_model=list[BotMetaOutput])
def get_popular_bots(
    request: Request,
    limit: int = 20,
):
    """Search bots by query string.
    - This method is used for bot-store functionality (Popular bots).
    - Results do NOT include private bots.
    - Only accessible bots are returned.
    - The order is based on the usage count.
    """
    current_user: User = request.state.current_user

    bots = fetch_popular_bots(current_user, limit)
    return bots


@router.get("/store/pickup", response_model=list[BotMetaOutput])
def get_pickup_bots(
    request: Request,
    limit: int = 20,
):
    """Search bots by query string.
    - This method is used for bot-store functionality (Today's pickup bots).
    - Results do NOT include private bots.
    - Only accessible bots are returned.
    - Random bots are returned.
    """
    current_user: User = request.state.current_user

    bots = fetch_pickup_bots(current_user, limit)
    return bots
