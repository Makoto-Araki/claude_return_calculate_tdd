# calculator-api

2個の**正の整数**パラメータに対して四則演算(加算・減算・乗算・除算)を行うシンプルなAPIサーバーです。

## 現在の実装状況

- 実装済み: `add`(加算、`POST /calculate/add`)・`subtract`(減算、`POST /calculate/subtract`)
- 未実装: `multiply`(乗算)・`divide`(除算)

## 技術スタック

- Python 3.12+
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)(バリデーション)
- [pytest](https://docs.pytest.org/) + [httpx](https://www.python-httpx.org/)(テスト)
- [uv](https://docs.astral.sh/uv/)(依存関係管理)
- [ruff](https://docs.astral.sh/ruff/)(lint・フォーマット)+ [mypy](https://mypy-lang.org/)(型チェック)

## セットアップ

```bash
uv sync
```

## コマンド

```bash
uv run uvicorn apps.main:app --reload      # 開発サーバー起動(http://localhost:8000)
uv run pytest tests/unit/ -v               # ユニットテスト実行
uv run ruff check .                        # lint実行
uv run ruff format --check .               # フォーマット差分チェック(適用しない)
uv run mypy apps/                          # 型チェック(appsディレクトリのみ対象)
```

## APIエンドポイント

全エンドポイント共通で `POST /calculate/<operation>` に `{"a": integer, "b": integer}` を送信する(`a`・`b`は1以上の正の整数のみ)。成功時は `{"operation", "a", "b", "result"}` を返し、`a`・`b`が正の整数でない場合(`0`・負数・小数・非数値・欠落)は `422 Unprocessable Entity` を返す。

| 演算 | エンドポイント | 状態 |
|---|---|---|
| 加算 | `POST /calculate/add` | 実装済み |
| 減算 | `POST /calculate/subtract` | 実装済み |
| 乗算 | `POST /calculate/multiply` | 未実装 |
| 除算 | `POST /calculate/divide` | 未実装 |

リクエスト例(`add`):

```bash
curl -X POST http://localhost:8000/calculate/add \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 3}'
# => {"operation":"add","a":10,"b":3,"result":13}
```

## ローカルKubernetesへのデプロイ

Docker Desktopで有効化したKubernetes上に、専用Namespace `calculator-api` でデプロイする。

```bash
docker build -t calculator-api:local .
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl get pods -n calculator-api
kubectl port-forward -n calculator-api deployment/calculator-api 8000:8000
```

詳細な設計判断は[`specs/deployment/`](specs/deployment/)を参照。

## ドキュメント

- 各演算・機能の要件定義・設計は [`specs/`](specs/) 配下(`requirements.md`・`design.md`・`tasks.md`)を参照
- 開発方針(TDDでの進め方、ディレクトリ構成、コーディング規約など)は [`CLAUDE.md`](CLAUDE.md) を参照
