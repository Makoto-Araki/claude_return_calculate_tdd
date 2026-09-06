"""除算(divide)エンドポイント `POST /calculate/divide` のユニットテスト。"""

import pytest
from fastapi.testclient import TestClient

from apps.main import app

client = TestClient(app)


def test_divide_positive_integers() -> None:
    """割り切れる正の整数同士の除算が正しく計算されることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
    """
    response = client.post("/calculate/divide", json={"a": 10, "b": 2})

    assert response.status_code == 200
    assert response.json() == {"operation": "divide", "a": 10, "b": 2, "result": 5.0}


def test_divide_not_evenly_divisible() -> None:
    """割り切れず結果が小数になるケースが正しく計算されることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
    """
    response = client.post("/calculate/divide", json={"a": 10, "b": 3})

    assert response.status_code == 200
    assert response.json() == {
        "operation": "divide",
        "a": 10,
        "b": 3,
        "result": pytest.approx(10 / 3),
    }


def test_divide_minimum_positive_integers() -> None:
    """許容される最小値(a=1, b=1)同士の除算が正しく計算されることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
    """
    response = client.post("/calculate/divide", json={"a": 1, "b": 1})

    assert response.status_code == 200
    assert response.json() == {"operation": "divide", "a": 1, "b": 1, "result": 1.0}


def test_divide_by_one() -> None:
    """bが1の場合、結果がaと一致する(恒等元)ことを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
    """
    response = client.post("/calculate/divide", json={"a": 42, "b": 1})

    assert response.status_code == 200
    assert response.json() == {"operation": "divide", "a": 42, "b": 1, "result": 42.0}


def test_divide_large_integers() -> None:
    """大きい正の整数同士の除算が正しく計算されることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
    """
    response = client.post("/calculate/divide", json={"a": 2_000_000, "b": 1_000_000})

    assert response.status_code == 200
    assert response.json() == {
        "operation": "divide",
        "a": 2_000_000,
        "b": 1_000_000,
        "result": 2.0,
    }


def test_divide_ignores_extra_fields() -> None:
    """リクエストボディに未定義フィールドが含まれても無視され、正常に計算されることを確認する。

    Parameters
    ----------
    なし

    Returns
    -------
    None
    """
    response = client.post("/calculate/divide", json={"a": 6, "b": 3, "c": 1})

    assert response.status_code == 200
    assert response.json() == {"operation": "divide", "a": 6, "b": 3, "result": 2.0}


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
def test_divide_invalid_input_returns_422(payload: dict[str, object]) -> None:
    """a・bが正の整数でない場合(0・負数・小数・非数値・空文字・欠落)に422が返ることを確認する。

    `b` が `0` の場合もゼロ除算専用エラーではなく、この正の整数バリデーションにより422が返る。

    Parameters
    ----------
    payload : dict[str, object]
        リクエストボディ(不正な値を含む)。

    Returns
    -------
    None
    """
    response = client.post("/calculate/divide", json=payload)

    assert response.status_code == 422
