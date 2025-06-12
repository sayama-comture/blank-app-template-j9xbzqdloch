import logging
import random
import time
import boto3 # 新規追加
import os # 新規追加

from app.repositories.common import get_opensearch_client
from app.repositories.models.custom_bot import BotMeta
from app.user import User
from opensearchpy import OpenSearch

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 修正 ---
def find_bots_by_query(
    query: str,
    user: User,
    limit: int = 20,
    client: OpenSearch | None = None,
    index_name: str = "bot",
) -> list[BotMeta]:
    """Search bots by query string.
    This method is used for bot-store functionality.

    Query Structure Explanation:

    1. Main Search (must clause):
    - Uses multi_match for flexible text searching
    - Searches across multiple fields (Description, Title, Instruction)
    - Implements fuzzy matching for typo tolerance
    - Requires 30% of search terms to match

    2. Access Control (filter clause):
    The filter implements three access levels:
    a) Public Bots (`SharedScope = "all"`):
        - Available to all users

    b) Partial Shared Bots (`SharedScope = "partial"`):
        - Admins can see all of them
        - Non-admins can see them if they are listed in `AllowedCognitoUsers`
          or belong to `AllowedCognitoGroups`

    c) Private Bots (no `SharedScope` field):
        - Only accessible to the owner (`PK.keyword = user.id`)
        - Admins can see their own private bots (`PK.keyword = admin-user`)
    """
    client = client or get_opensearch_client()
    logger.info(f"Searching bots with query: {query}")

    # Include only BOT items
    filter_must = [{"prefix": {"SK.keyword": "BOT"}}]
    # Condition for bots that can be acquired
    filter_should = [
        {"term": {"SharedScope.keyword": "all"}},  # Everyone can get
        # Owner AND (no SharedScope i.e. private OR SharedScope = "partial")
        {
            "bool": {
                "must": [
                    {"term": {"PK.keyword": user.id}},
                    {
                        "bool": {
                            "should": [
                                {
                                    "bool": {
                                        "must_not": {"exists": {"field": "SharedScope"}}
                                    }
                                },
                                {"term": {"SharedScope.keyword": "partial"}},
                            ],
                            "minimum_should_match": 1,
                        }
                    },
                ]
            }
        },
    ]

    filter_should.append(
        {
            "bool": {
                "must": [
                    {"term": {"SharedScope.keyword": "partial"}},
                    {
                        "bool": {
                            "should": [
                                {"term": {"AllowedCognitoUsers.keyword": user.id}},
                                {
                                    "script": {
                                        "script": {
                                            "source": (
                                                "for (group in doc['AllowedCognitoGroups.keyword']) { "
                                                "if (params.user_groups.contains(group)) { return true; } } "
                                                "return false;"
                                            ),
                                            "params": {"user_groups": user.groups},
                                            "lang": "painless",
                                        }
                                    }
                                },
                            ],
                            "minimum_should_match": 1,
                        }
                    },
                ]
            }
        }
    )

    search_body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["Description", "Title", "Instruction"],
                            "type": "best_fields",
                            "operator": "or",
                            "minimum_should_match": "30%",
                            "fuzziness": "AUTO",
                        }
                    }
                ],
                "filter": {
                    "bool": {
                        "must": filter_must,
                        "should": filter_should,
                        "minimum_should_match": 1,
                    }
                },
            }
        },
        "size": limit,
    }
    logger.debug(f"Entire search body: {search_body}")

    try:
        response = client.search(index=index_name, body=search_body)
        logger.debug(f"Search response: {response}")
        bots = []
        for hit in response["hits"]["hits"]:
            bots.append(hit["_source"])
        logger.info(f"検索に一致したボット一覧: {bots}")
        return bots

    except Exception as e:
        logger.error(f"Error searching bots: {e}")
        raise
# 修正 ---

# 新規追加 -----
def find_all_bots_by_query(
    query: str | None,
    limit: int = 20,
    client: OpenSearch | None = None,
    index_name: str = "bot",
) -> list:
    """
    クエリに基づいてボット情報を検索する関数
    
    引数:
        query (str): 検索クエリ（メールアドレスまたは検索文字列）
        limit (int, optional): 検索結果の上限数. デフォルト: 20.
        client (OpenSearch | None, optional): OpenSearchクライアント. デフォルト: None.
        index_name (str, optional): 検索対象のインデックス名. デフォルト: "bot".
    
    戻り値:
        list: 検索条件に一致するボット情報のリスト
    
    処理概要:
        1. メールアドレスでのクエリの場合、Cognitoからユーザー名を取得
        2. OpenSearchでボット情報を検索
        3. 検索結果をリストで返却
    
    例外処理:
        - Cognitoのユーザー取得エラー
        - OpenSearch検索エラー
    """
    logger.info("starting find_all_bots_by_query")
    logger.info(f"query: {query}")
    
    # OpenSearchクライアントの初期化
    client = client or get_opensearch_client()
    
    # Cognitoクライアントの初期化とユーザープールの設定
    cognito = boto3.client("cognito-idp")
    USER_POOL_ID = os.environ.get("USER_POOL_ID")
    
    # メールアドレスでCognitoからユーザー情報を検索
    try:
        response = cognito.list_users(
                UserPoolId=USER_POOL_ID, Filter=f'email = "{query}"', Limit=1
            )
        users = response.get('Users', [])
    except Exception as e:
        logger.error(f"ユーザー検索中にエラーが発生しました。: {e}")
        raise
    
    search_body = {}
    # 検索クエリが無しの場合、全件取得
    if not query:
        query_params = {
            "bool": {
                "filter": [
                    {"prefix": {"SK.keyword": "BOT"}}
                ]
            }
        }

    # ユーザーが見つかった場合、ユーザーIDをクエリとして使用
    elif users:
        query = users[0]["Username"]
        logger.info(f"ユーザーで検索: {query}")
        query_params = {
            "bool": {
                "must": [
                    {
                        "bool": {
                            "should": [
                                {"wildcard": {"PK.keyword": f"*{query}*"}}
                            ],
                            "minimum_should_match": 1
                        }
                    }
                ],
                "filter": [
                    {"prefix": {"SK.keyword": "BOT"}}
                ]
            }
        }

    # その他の場合の検索用のクエリボディを構築
    else:
        query_params = {
            "bool": {
                "must": [
                    {
                        "bool": {
                            "should": [
                                {"wildcard": {"Title.keyword": f"*{query}*"}}
                            ],
                            "minimum_should_match": 1
                        }
                    }
                ],
                "filter": [
                    {"prefix": {"SK.keyword": "BOT"}}
                ]
            }
        }
    search_body["query"] = query_params
    search_body["size"] = limit
    
    logger.debug(f"Entire search body: {search_body}")

    # OpenSearchでボット検索を実行
    try:
        response = client.search(index=index_name, body=search_body)
    except Exception as e:
        logger.error(f"ボット検索中にエラーが発生しました。: {e}")
        raise
    
    # 検索結果を処理
    bots = []
    for hit in response["hits"]["hits"]:
        bots.append(hit["_source"])
        
    logger.info(f"ヒットしたボットの一覧: {bots}")
    logger.info("end find_all_bots_by_query")
    return bots

# 新規追加 -----

def find_bots_sorted_by_usage_count(
    user: User,
    limit: int = 20,
    client: OpenSearch | None = None,
    index_name: str = "bot",
) -> list[BotMeta]:
    """Search bots sorted by usage count while considering access control."""
    client = client or get_opensearch_client()
    logger.info(f"Searching bots sorted by usage count")

    filter_must = [{"prefix": {"SK.keyword": "BOT"}}]
    filter_should = [
        {"term": {"SharedScope.keyword": "all"}},  # Public bots
        # Owner's bots (private or partial)
        {
            "bool": {
                "must": [
                    {"term": {"PK.keyword": user.id}},
                    {
                        "bool": {
                            "should": [
                                {
                                    "bool": {
                                        "must_not": {"exists": {"field": "SharedScope"}}
                                    }
                                },
                                {"term": {"SharedScope.keyword": "partial"}},
                            ],
                            "minimum_should_match": 1,
                        }
                    },
                ]
            }
        },
        # Partial shared bots with access permission
        {
            "bool": {
                "must": [
                    {"term": {"SharedScope.keyword": "partial"}},
                    {
                        "bool": {
                            "should": [
                                {"term": {"AllowedCognitoUsers.keyword": user.id}},
                                {
                                    "script": {
                                        "script": {
                                            "source": (
                                                "for (group in doc['AllowedCognitoGroups.keyword']) { "
                                                "if (params.user_groups.contains(group)) { return true; } } "
                                                "return false;"
                                            ),
                                            "params": {"user_groups": user.groups},
                                            "lang": "painless",
                                        }
                                    }
                                },
                            ],
                            "minimum_should_match": 1,
                        }
                    },
                ]
            }
        },
    ]

    search_body = {
        "query": {
            "bool": {
                "filter": {
                    "bool": {
                        "must": filter_must,
                        "should": filter_should,
                        "minimum_should_match": 1,
                    }
                }
            }
        },
        "sort": [{"UsageStats.usage_count": {"order": "desc"}}],
        "size": limit,
    }

    logger.debug(f"Search body: {search_body}")

    try:
        response = client.search(index=index_name, body=search_body)
        logger.debug(f"Search response: {response}")

        bots = [
            BotMeta.from_opensearch_response(hit, user.id)
            for hit in response["hits"]["hits"]
        ]
        logger.info(f"Found {len(bots)} bots sorted by usage count")
        return bots

    except Exception as e:
        logger.error(f"Error searching bots: {e}")
        raise


def find_random_bots(
    user: User,
    limit: int = 20,
    client: OpenSearch | None = None,
    index_name: str = "bot",
) -> list[BotMeta]:
    """Find random bots while considering access control."""
    client = client or get_opensearch_client()
    logger.info(f"Searching random bots")

    filter_must = [{"prefix": {"SK.keyword": "BOT"}}]
    filter_should = [
        {"term": {"SharedScope.keyword": "all"}},  # Public bots
        # Owner's bots (private or partial)
        {
            "bool": {
                "must": [
                    {"term": {"PK.keyword": user.id}},
                    {
                        "bool": {
                            "should": [
                                {
                                    "bool": {
                                        "must_not": {"exists": {"field": "SharedScope"}}
                                    }
                                },
                                {"term": {"SharedScope.keyword": "partial"}},
                            ],
                            "minimum_should_match": 1,
                        }
                    },
                ]
            }
        },
        # Partial shared bots with access permission
        {
            "bool": {
                "must": [
                    {"term": {"SharedScope.keyword": "partial"}},
                    {
                        "bool": {
                            "should": [
                                {"term": {"AllowedCognitoUsers.keyword": user.id}},
                                {
                                    "script": {
                                        "script": {
                                            "source": (
                                                "for (group in doc['AllowedCognitoGroups.keyword']) { "
                                                "if (params.user_groups.contains(group)) { return true; } } "
                                                "return false;"
                                            ),
                                            "params": {"user_groups": user.groups},
                                            "lang": "painless",
                                        }
                                    }
                                },
                            ],
                            "minimum_should_match": 1,
                        }
                    },
                ]
            }
        },
    ]

    seed = int(time.time()) + random.randint(0, 10000)
    search_body = {
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "filter": {
                            "bool": {
                                "must": filter_must,
                                "should": filter_should,
                                "minimum_should_match": 1,
                            }
                        }
                    }
                },
                "random_score": {"seed": seed},
            }
        },
        "size": limit,
    }

    logger.debug(f"Search body: {search_body}")

    try:
        response = client.search(index=index_name, body=search_body)
        logger.debug(f"Search response: {response}")

        bots = [
            BotMeta.from_opensearch_response(hit, user.id)
            for hit in response["hits"]["hits"]
        ]
        logger.info(f"Found {len(bots)} random bots")
        return bots

    except Exception as e:
        logger.error(f"Error searching bots: {e}")
        raise
