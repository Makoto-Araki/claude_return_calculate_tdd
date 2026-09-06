"""減算(subtract)エンドポイントのルーター。"""

from fastapi import APIRouter

from apps.schemas import CalculationResponse, SubtractRequest

router = APIRouter()


@router.post("/calculate/subtract", response_model=CalculationResponse)
def subtract(request: SubtractRequest) -> CalculationResponse:
    """2つの正の整数を減算する。

    Parameters
    ----------
    request : SubtractRequest
        被減数 `a` と減数 `b`(いずれも正の整数)を含むリクエストボディ。

    Returns
    -------
    CalculationResponse
        演算名・a・b・減算結果を含むレスポンス。
    """
    result = request.a - request.b
    return CalculationResponse(operation="subtract", a=request.a, b=request.b, result=result)
