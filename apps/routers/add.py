"""加算(add)エンドポイントのルーター。"""

from fastapi import APIRouter

from apps.schemas import AddRequest, CalculationResponse

router = APIRouter()


@router.post("/calculate/add", response_model=CalculationResponse)
def add(request: AddRequest) -> CalculationResponse:
    """2つの正の整数を加算する。

    Parameters
    ----------
    request : AddRequest
        被加数 `a` と加数 `b`(いずれも正の整数)を含むリクエストボディ。

    Returns
    -------
    CalculationResponse
        演算名・a・b・加算結果を含むレスポンス。
    """
    result = request.a + request.b
    return CalculationResponse(operation="add", a=request.a, b=request.b, result=result)
