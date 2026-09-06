"""除算(divide)エンドポイントのルーター。"""

from fastapi import APIRouter

from apps.schemas import DivideRequest, DivideResponse

router = APIRouter()


@router.post("/calculate/divide", response_model=DivideResponse)
def divide(request: DivideRequest) -> DivideResponse:
    """2つの正の整数を除算する。

    Parameters
    ----------
    request : DivideRequest
        被除数 `a` と除数 `b`(いずれも正の整数)を含むリクエストボディ。

    Returns
    -------
    DivideResponse
        演算名・a・b・除算結果(float)を含むレスポンス。
    """
    result = request.a / request.b
    return DivideResponse(operation="divide", a=request.a, b=request.b, result=result)
