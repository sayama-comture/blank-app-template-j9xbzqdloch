from datetime import date

from app.dependencies import check_admin
from app.repositories.custom_bot import find_all_published_bots, find_bot_by_id, change_bot_owner, get_all_registered_bots # 新規追加
from app.repositories.usage_analysis import (
    find_bots_sorted_by_price,
    find_users_sorted_by_price,
)
from app.routes.schemas.admin import (
    PublicBotOutput,
    PublishedBotOutput,
    PublishedBotOutputsWithNextToken,
    PushBotInput,
    UsagePerBotOutput,
    UsagePerUserOutput,
)
from app.routes.schemas.bot import Knowledge
from app.usecases.bot import modify_pinning_status
from app.user import User
from fastapi import APIRouter, Depends, Request

# 新規追加 -----
from app.usecases.bot_store import search_all_bots 
from pydantic import BaseModel
# 新規追加 -----

router = APIRouter(tags=["admin"])

# 新規追加 -----
@router.get("/admin/store/search")
def store_search(
    request: Request,
    limit: int = 100,
    admin_check=Depends(check_admin),
    query: str | None = None,
    filter: str | None = None
):
    """
    管理者向けbot検索
    
    引数:
        request (Request): FastAPIのリクエストオブジェクト
        limit (int): 検索結果の最大件数。デフォルトは100件
        admin_check: 管理者権限チェック関数
        query (str): 検索クエリ文字列（デフォルト: 空文字）
        filter (str | None): フィルター条件（カンマ区切り、デフォルト: None）
    
    戻り値:
        list: botメタデータのリスト
    
    処理概要:
        管理者権限を持つユーザーがbotを検索し、フィルター条件に従って結果を返す
    """
    # 現在のユーザー情報を取得
    current_user = request.state.current_user
    if current_user:
        user_id = current_user.id
    else:
        user_id = None

    # フィルター条件をリストに変換
    if filter:
        filter_items = filter.split(",")
    
    # botの検索を実行
    bots = search_all_bots(query, limit)
    
    # bot情報を整形
    bot_metas = []
    for bot in bots:
        # フィルター条件をチェック
        if filter and bot.get("SharedStatus") not in filter_items:
            if bot.get("SharedScope") not in filter_items:
                # SharedStatusまたはSharedScopeがフィルター条件に一致しない場合はスキップ
                continue
        
        # botメタデータを構築
        items = {
            "id": bot["BotId"],
            "title": bot["Title"],
            "description": bot["Description"],
            "createTime": bot["CreateTime"],
            "lastUsedTime": bot.get("LastUsedTime", None),
            "owner_user_id": bot["PK"],
            "is_starred": bot.get("IsStarred", False),
            "owned": bot["PK"] == user_id,
            "available": True,
            "syncStatus": bot["SyncStatus"],
            "shared_scope": bot.get("SharedScope", None),
            "shared_status": bot.get("SharedStatus", None)
        }
        bot_metas.append(items)

    return bot_metas
# 新規追加 -----

@router.get("/admin/published-bots", response_model=PublishedBotOutputsWithNextToken)
def get_all_published_bots(
    next_token: str | None = None,
    limit: int = 1000,
    admin_check=Depends(check_admin),
):
    """Get all published bots. This is intended to be used by admin."""
    bots, next_token = find_all_published_bots(next_token=next_token, limit=limit)

    bot_outputs = [
        PublishedBotOutput(
            id=bot.id,
            title=bot.title,
            description=bot.description,
            published_stack_name=bot.published_api_stack_name,
            published_datetime=bot.published_api_datetime,
            owner_user_id=bot.owner_user_id,
            shared_scope=bot.shared_scope,
            shared_status=bot.shared_status,
        )
        for bot in bots
    ]

    return PublishedBotOutputsWithNextToken(bots=bot_outputs, next_token=next_token)


@router.get("/admin/public-bots", response_model=list[UsagePerBotOutput])
async def get_all_public_bots(
    limit: int = 100,
    start: str | None = None,
    end: str | None = None,
    admin_check=Depends(check_admin),
):
    """Get all public bots. This is intended to be used by admin.
    NOTE:
    - limit: must be lower than 1000.
    - start: start date of the period to be analyzed. The format is `YYYYMMDDHH`.
    - end: end date of the period to be analyzed. The format is `YYYYMMDDHH`.
    - If start and end are not specified, start is set to today's 00:00 and end is set to 23:00.
    - The result is sorted by the total price in descending order.
    """
    bots = await find_bots_sorted_by_price(limit=limit, from_=start, to_=end)

    return [
        UsagePerBotOutput(
            id=bot.id,
            title=bot.title,
            description=bot.description,
            is_published=True if bot.published_api_stack_name else False,
            published_datetime=bot.published_api_datetime,
            shared_scope=bot.shared_scope,
            shared_status=bot.shared_status,
            owner_user_id=bot.owner_user_id,
            total_price=bot.total_price,
        )
        for bot in bots
    ]


@router.get("/admin/users", response_model=list[UsagePerUserOutput])
async def get_users(
    limit: int = 100,
    start: str | None = None,
    end: str | None = None,
    admin_check=Depends(check_admin),
):
    """Get all users. This is intended to be used by admin.
    NOTE:
    - limit: must be lower than 1000.
    - start: start date of the period to be analyzed. The format is `YYYYMMDDHH`.
    - end: end date of the period to be analyzed. The format is `YYYYMMDDHH`.
    - If start and end are not specified, start is set to today's 00:00 and end is set to 23:00.
    - The result is sorted by the total price in descending order.
    """
    users = await find_users_sorted_by_price(limit=limit, from_=start, to_=end)

    return [
        UsagePerUserOutput(
            id=user.id,
            email=user.email,
            total_price=user.total_price,
        )
        for user in users
    ]


@router.get("/admin/bot/public/{bot_id}", response_model=PublicBotOutput)
def get_public_bot(request: Request, bot_id: str, admin_check=Depends(check_admin)):
    """Get public (shared) bot by id."""
    bot = find_bot_by_id(bot_id)  # Note that permission check is done in `check_admin`.
    output = PublicBotOutput(
        id=bot.id,
        title=bot.title,
        instruction=bot.instruction,
        description=bot.description,
        create_time=bot.create_time,
        last_used_time=bot.last_used_time or bot.create_time,
        owner_user_id=bot.owner_user_id,
        knowledge=Knowledge(
            source_urls=bot.knowledge.source_urls,
            sitemap_urls=bot.knowledge.sitemap_urls,
            filenames=bot.knowledge.filenames,
            s3_urls=bot.knowledge.s3_urls,
        ),
        sync_status=bot.sync_status,
        sync_status_reason=bot.sync_status_reason,
        sync_last_exec_id=bot.sync_last_exec_id,
        shared_scope=bot.shared_scope,
        shared_status=bot.shared_status,
        allowed_cognito_groups=bot.allowed_cognito_groups,
        allowed_cognito_users=bot.allowed_cognito_users,
    )
    return output

# 新規追加 -----
@router.get("/admin/bots")
def get_all_bots(
    request: Request,
    admin_check=Depends(check_admin),
    start: str | None = None,
    end: str | None = None
):
    current_user = request.state.current_user
    bots = get_all_registered_bots(current_user.id, start, end)
    return bots
# 新規追加 -----

@router.patch("/admin/bot/{bot_id}/pushed")
def pin_bot(
    request: Request,
    bot_id: str,
    push_input: PushBotInput,
    admin_check=Depends(check_admin),
):
    """Push / Un-push the bot."""
    modify_pinning_status(bot_id, push_input)

# 新規追加 -----
class userIdBody(BaseModel):
    userId: str

@router.patch("/admin/bot/{bot_id}/owner")
def change_owner(
    request: Request,
    bot_id: str,
    body: userIdBody,
    admin_check=Depends(check_admin),
):  
    print(f"start change owner bot_id: {bot_id}, user_id: {body.userId}")
    change_bot_owner(bot_id, body.userId)
    return {"message": "Owner changed successfully."}
# 新規追加 -----