"""乗算(multiply)エンドポイント `POST /calculate/multiply` のユニットテスト。"""

import pytest
from fastapi.testclient import TestClient

from apps.main import app

client = TestClient(app)


def test_multiply_positive_integers() -> None:
    """正の整数同士の乗算が正しく計算されることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
    """
    response = client.post("/calculate/multiply", json={"a": 10, "b": 3})

    assert response.status_code == 200
    assert response.json() == {"operation": "multiply", "a": 10, "b": 3, "result": 30}


def test_multiply_minimum_positive_integers() -> None:
    """許容される最小値(a=1, b=1)同士の乗算が正しく計算されることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
    """
    response = client.post("/calculate/multiply", json={"a": 1, "b": 1})

    assert response.status_code == 200
    assert response.json() == {"operation": "multiply", "a": 1, "b": 1, "result": 1}


def test_multiply_by_one() -> None:
    """片方が1の場合、結果がもう一方の値と一致する(恒等元)ことを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
    """
    response = client.post("/calculate/multiply", json={"a": 42, "b": 1})

    assert response.status_code == 200
    assert response.json() == {"operation": "multiply", "a": 42, "b": 1, "result": 42}


def test_multiply_large_integers() -> None:
    """大きい正の整数同士の乗算が正しく計算されることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
    """
    response = client.post("/calculate/multiply", json={"a": 1_000_000, "b": 2_000_000})

    assert response.status_code == 200
    assert response.json() == {
        "operation": "multiply",
        "a": 1_000_000,
        "b": 2_000_000,
        "result": 2_000_000_000_000,
    }


def test_multiply_ignores_extra_fields() -> None:
    """リクエストボディに未定義フィールドが含まれても無視され、正常に計算されることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
    """
    response = client.post("/calculate/multiply", json={"a": 5, "b": 3, "c": 1})

    assert response.status_code == 200
    assert response.json() == {"operation": "multiply", "a": 5, "b": 3, "result": 15}


@pytest.mark.parametrize(
    "payload",
    [
        {"a": 0, "b": 5},
        {"a": 5, "b": 0},
        {"a": -1, "b": 5},
        {"a": 5, "b": -1},
        {"a": 1.5, "b": 5},
        {"a": 5, "b": 1.5},
        {"a": "abc", "b": 5},
        {"a": 5, "b": "abc"},
        {"a": "", "b": 5},
        {"a": 5, "b": ""},
        {"b": 5},
        {"a": 5},
        {},
    ],
    ids=[
        "a_zero",
        "b_zero",
        "a_negative",
        "b_negative",
        "a_decimal",
        "b_decimal",
        "a_non_numeric",
        "b_non_numeric",
        "a_empty_string",
        "b_empty_string",
        "a_missing",
        "b_missing",
        "both_missing",
    ],
)
def test_multiply_invalid_input_returns_422(payload: dict[str, object]) -> None:
    """a・bが正の整数でない場合(0・負数・小数・非数値・空文字・欠落)に422が返ることを確認する。

    Parameters
    ----------
    payload : dict[str, object]
        リクエストボディ(不正な値を含む)。

    Returns
    -------
    None
    """
    response = client.post("/calculate/multiply", json=payload)

    assert response.status_code == 422
