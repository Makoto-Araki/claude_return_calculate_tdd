"""リクエスト/レスポンスのPydanticモデル定義。"""

from pydantic import BaseModel, PositiveInt


class AddRequest(BaseModel):
    """`POST /calculate/add` のリクエストボディ。"""

    a: PositiveInt
    b: PositiveInt


class SubtractRequest(BaseModel):
    """`POST /calculate/subtract` のリクエストボディ。"""

    a: PositiveInt
    b: PositiveInt


class CalculationResponse(BaseModel):
    """四則演算エンドポイントの共通レスポンスボディ。"""

    operation: str
    a: int
    b: int
    result: int
