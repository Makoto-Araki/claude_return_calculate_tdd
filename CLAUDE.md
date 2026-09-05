# CLAUDE.md

このファイルは、このリポジトリで作業するClaude Code (claude.ai/code) に向けたガイダンスを提供します。

## プロジェクトの現状

加算 (`add`)・減算 (`subtract`)・乗算 (`multiply`)・除算 (`divide`) の四則演算エンドポイントはすべて実装済みです。デプロイ関連(Dockerfile、Kubernetesマニフェスト)は、要件・設計の整理段階で作成した `specs/deployment/` ディレクトリのみが存在し、まだ**仕様のみ**の状態です。

- 実装済み: `apps/`(FastAPIアプリ本体)、`pyproject.toml`(uv管理の依存定義)、`tests/unit/test_add.py`・`tests/unit/test_subtract.py`・`tests/unit/test_multiply.py`・`tests/unit/test_divide.py`(pytestユニットテスト)
- 未実装: `Dockerfile`、`k8s/`
- CI(GitHub Actions)は導入済みです。詳細は[実行環境(Kubernetes)に関する設計判断](#実行環境kubernetesに関する設計判断)の後の[CI(GitHub Actions)に関する設計判断](#cigithub-actionsに関する設計判断)を参照してください。

主なコマンド([uv](https://docs.astral.sh/uv/)を使用):

```bash
uv sync                                    # 依存関係のインストール
uv run uvicorn apps.main:app --reload      # 開発サーバー起動
uv run pytest tests/unit/ -v               # ユニットテスト実行
uv run ruff check .                        # lint実行
uv run ruff format --check .               # フォーマット差分チェック(適用しない)
uv run mypy apps/                          # 型チェック(appsディレクトリのみ対象)
```

## プロジェクトの目的

2個の**正の整数**パラメータに対して四則演算(加算・減算・乗算・除算)を行うシンプルなAPIサーバー。想定している技術スタック(design.mdに記載済みだが、まだ実装はされていない)は Python 3.12+、FastAPI、バリデーション用のPydantic v2、テスト用のpytest + httpx。

## スペック駆動のワークフロー

各演算・機能は `specs/` 配下にそれぞれ独立したフィーチャーフォルダを持ち、requirements → design → tasks の3ファイル構成に従う。

```
specs/
├── add/
├── subtract/
├── multiply/
├── divide/
│   ├── requirements.md   # EARS記法(WHEN/THEN/SHALL)による受け入れ基準
│   ├── design.md         # エンドポイント仕様、Pydanticモデル、処理フロー、エラーハンドリング
│   └── tasks.md          # 実装チェックリスト。各項目は対応する要件番号を明記
└── deployment/
    ├── requirements.md   # Kubernetes Deploymentリソースの要件
    ├── design.md          # Deploymentマニフェストの内容と設計判断の理由
    └── tasks.md           # Dockerfile作成〜デプロイ確認までのタスク
```

機能を実装する際は、リクエスト/レスポンスの形式やエラー挙動の詳細をその機能の `design.md` から確認し、実装が完了した `tasks.md` の項目にはチェックを入れること。各タスクは親の `requirements.md` 内のどの要件を満たすものかが番号で紐づいている。新しい演算・機能を追加する場合も、同様に `specs/<feature>/` に同じ3ファイル構成を作成してこの形式を維持すること。

## 4演算に共通する主要な設計判断

- 全エンドポイントは `POST /calculate/<operation>` で、JSONボディ `{"a": integer, "b": integer}` を受け取り、成功時は `{"operation", "a", "b", "result"}` を返す。
- `a`/`b` は**正の整数(> 0)のみ**を許容する(Pydanticの `PositiveInt` を使用)。`0`・負数・小数・非数値・欠落はすべてFastAPI/Pydantic標準の `422` レスポンスに委ねる。独自のバリデーションを実装しないこと。
- `divide` の `b == 0` も上記の正の整数バリデーションで弾かれるため、ゼロ除算専用の `400` エラーハンドリングは実装しない(`ZeroDivisionError` が発生する経路自体が存在しない)。
- 認証・永続化・CORSはスコープ外。

## 実行環境(Kubernetes)に関する設計判断

詳細は [`specs/deployment/`](specs/deployment/) を参照。

- ローカルPCのDocker Desktopで有効化したKubernetes上に、専用Namespace `calculator-api` 配下で `Deployment`リソースとしてデプロイする想定(本番運用は想定しない)。`default` Namespaceは使用しない。
- リソース節約を最優先するため、レプリカ数は `1`、`livenessProbe`/`readinessProbe`は設定しない、CPU/メモリの`requests`/`limits`は最小限、という最小構成を維持すること。
- `Service`/`Ingress`・オートスケーリングなどはスコープ外。追加する場合は要件から見直すこと。

## CI(GitHub Actions)に関する設計判断

詳細は [`specs/ci/`](specs/ci/) を参照。

- `.github/workflows/ci-pull-request.yml`: `main`向けPRの作成・更新時(`pull_request`トリガー)に実行。
- `.github/workflows/ci-main.yml`: `main`へのpush(マージ)時(`push`トリガー)に実行。
- 両ファイルとも`test`ジョブ(`uv run ruff check .`・`uv run ruff format --check .`・`uv run mypy apps/`・`uv run pytest tests/unit/ -v`)と`docker-build`ジョブ(`docker build`のみ、push・デプロイなし)を持つ。
- Kubernetesへの自動デプロイ(CD)・イメージのレジストリpushはスコープ外(`specs/deployment/`に従い手動運用)。

## 実装時のディレクトリ構成

アプリケーションコードは `app/` ではなく **`apps/`** ディレクトリ配下に実装すること(各 `specs/<operation>/tasks.md` のファイルパスもこれに合わせて記載済み)。`apps/routers/` は `tests/unit/` と同様に**演算ごとにファイルを分割**し、1ファイルに複数演算のハンドラをまとめないこと。

```
apps/
├── main.py            # FastAPIアプリ、各ルーターの登録
├── routers/
│   ├── add.py         # POST /calculate/add
│   ├── subtract.py    # POST /calculate/subtract
│   ├── multiply.py    # POST /calculate/multiply
│   └── divide.py      # POST /calculate/divide
└── schemas.py         # Pydanticモデル(リクエスト/レスポンス)
tests/
└── unit/
    ├── test_add.py
    ├── test_subtract.py
    ├── test_multiply.py
    └── test_divide.py
Dockerfile
k8s/
├── namespace.yaml      # 専用Namespace "calculator-api" を定義
└── deployment.yaml     # namespace: calculator-api を指定。specs/deployment/design.md の内容に従う
```

## ユニットテストの方針

各演算の実装には**必ずユニットテストコードを併せて出力する**こと。出力先は `tests/unit/` 配下とし、演算ごとに個別のテストファイル(`test_add.py` など)に分ける。テストケースは各 `specs/<operation>/tasks.md` に列挙された正常系・異常系の項目を網羅すること。テスト関数にも[Docstringの方針](#docstringの方針)に従いNumPyスタイルのdocstringを付与すること。

## Docstringの方針

関数・メソッドにはNumPyスタイルのdocstringを付与すること(`Parameters` / `Returns` セクションを`----`の下線で区切る形式)。

```python
def add(a: int, b: int) -> int:
    """2つの整数を加算する。

    Parameters
    ----------
    a : int
        被加数。
    b : int
        加数。

    Returns
    -------
    int
        a + b の結果。
    """
```

## PR作成時の言語

PRのタイトル・本文は日本語で記述すること。

## PR作成の粒度

キリの良い作業単位(1機能・1ドキュメント更新など)が完了するたびに、こまめにコミット・push・PR作成を行うこと。複数の無関係な変更を1つの大きなPRにまとめて溜め込まないこと。このリポジトリはPRがマージされるとブランチが自動削除されるため、新たな作業を始める前には必ず `git fetch origin` して `main` を最新化し、そこから新しいブランチを切ること。
