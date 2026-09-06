# CLAUDE.md

このファイルは、このリポジトリで作業するClaude Code (claude.ai/code) に向けたガイダンスを提供します。

## プロジェクトの現状

四則演算の **`add`(加算)・`subtract`(減算)・`multiply`(乗算)・`divide`(除算)がすべて実装済み** です。lint・型チェック・CIは4演算すべてが動く状態を対象として整備済みです。ローカルKubernetesへのデプロイ環境は、4演算すべてが揃った状態でイメージを再ビルド・再デプロイし、`POST /calculate/<operation>`の応答(正常系`200`・異常系`422`)を4演算すべてで確認済みです。

`specs/`(add/subtract/multiply/divide/deployment/ci/lint)は、別リポジトリでSDD(仕様駆動開発)を行っていた際に作成した要件定義・設計ドキュメントをそのまま引き継いだものです。各 `tasks.md` のチェックボックスはすべて `[x]` になっていますが、これは**旧リポジトリでの完了状態の引き継ぎ**です(`add`・`subtract`・`multiply`・`divide`・lint・CIについては本リポジトリでも実際に完了済みです)。本リポジトリでは要件・設計(`requirements.md`・`design.md`)はそのまま仕様源として使いますが、実装の進め方はSDDではなく**TDD(テスト駆動開発)**で行います(詳細は[TDDでの実装の進め方](#tddでの実装の進め方)を参照)。

実装済み:
- `apps/`(`schemas.py`・`main.py`・`routers/add.py`・`routers/subtract.py`・`routers/multiply.py`・`routers/divide.py`)、`pyproject.toml`(uv管理の依存定義、ruff・mypy設定を含む)
- `tests/unit/test_add.py`・`test_subtract.py`・`test_multiply.py`・`test_divide.py`(pytestユニットテスト。いずれもテストを先に実装しRed確認後に`apps/`を実装してGreenにした)
- `Dockerfile`・`k8s/`(`namespace.yaml`・`deployment.yaml`)。4演算すべてが揃った状態でローカルのDocker Desktop Kubernetes上にイメージ再ビルド・再デプロイし、4演算すべての応答(正常系`200`・異常系`422`)を確認済み
- CI(`.github/workflows/ci-pull-request.yml`・`ci-main.yml`)。GitHub Actions上で`test`・`docker-build`両ジョブの成功を確認済み

演算を追加した際は、`Dockerfile`・`k8s/`マニフェストは変更不要だが、イメージの再ビルド・再デプロイと全演算での動作再確認が必要。

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

2個の**正の整数**パラメータに対して四則演算(加算・減算・乗算・除算)を行うシンプルなAPIサーバー。技術スタックは Python 3.12+、FastAPI、バリデーション用のPydantic v2、テスト用のpytest + httpx。

## specs/ の構成と使い方

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

`requirements.md`・`design.md` は本リポジトリでも仕様源としてそのまま使う(設計をやり直す必要はない)。ただし `tasks.md` のチェックボックスは前述の通り旧リポジトリでの完了状態の引き継ぎであり、本リポジトリでの実装状況とは無関係(未実装)なので、実装済みの印として扱わないこと。新しい演算・機能を追加する場合も、同様に `specs/<feature>/` に同じ3ファイル構成を作成してこの形式を維持すること。

## TDDでの実装の進め方

本リポジトリでは、SDD(仕様が先にあり後からテストを追認生成する進め方)ではなく、**TDD(テスト駆動開発)**で実装する。

- 各演算(add/subtract/multiply/divide)を実装する際は、`specs/<operation>/tasks.md` に列挙されたテストケース一覧を先に `tests/unit/test_<operation>.py` に実装し(Red確認)、その後に `apps/` 側の実装を追加してテストを通す(Green)。
- 進め方の単位は**演算ごとに1サイクル**(テスト作成→実装→lint/mypy確認→コミット→push→PR作成)とし、1つの演算のPRが完結してから次の演算に進む。4演算分のテストや実装をまとめて先に書く方式は採らない。
- `specs/<operation>/tasks.md` の各項目(スキーマ定義→ハンドラ実装→テスト実装、という記載順)は要件の網羅リストとして参照し、実際の着手順序はテスト実装を先に行う。

## 4演算に共通する主要な設計判断

- 全エンドポイントは `POST /calculate/<operation>` で、JSONボディ `{"a": integer, "b": integer}` を受け取り、成功時は `{"operation", "a", "b", "result"}` を返す。
- `a`/`b` は**正の整数(> 0)のみ**を許容する(Pydanticの `PositiveInt` を使用)。`0`・負数・小数・非数値・欠落はすべてFastAPI/Pydantic標準の `422` レスポンスに委ねる。独自のバリデーションを実装しないこと。
- `divide` の `b == 0` も上記の正の整数バリデーションで弾かれるため、ゼロ除算専用の `400` エラーハンドリングは実装しない(`ZeroDivisionError` が発生する経路自体が存在しない)。
- 認証・永続化・CORSはスコープ外。

## 実行環境(Kubernetes)に関する設計判断

詳細は [`specs/deployment/`](specs/deployment/) を参照。**導入済み**(`add`のみの状態でローカルデプロイ・動作確認済み)。

- ローカルPCのDocker Desktopで有効化したKubernetes上に、専用Namespace `calculator-api` 配下で `Deployment`リソースとしてデプロイする(本番運用は想定しない)。`default` Namespaceは使用しない。
- リソース節約を最優先するため、レプリカ数は `1`、`livenessProbe`/`readinessProbe`は設定しない、CPU/メモリの`requests`/`limits`は最小限、という最小構成を維持すること。
- `Service`/`Ingress`・オートスケーリングなどはスコープ外。追加する場合は要件から見直すこと。

## CI(GitHub Actions)に関する設計判断

詳細は [`specs/ci/`](specs/ci/) を参照。**導入済み**(GitHub Actions上でtest・docker-build両ジョブの成功を確認済み)。

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

[TDDでの実装の進め方](#tddでの実装の進め方)の通り、各演算の実装コードより**先に**ユニットテストコードを出力すること(テストが失敗する=Redであることを確認してから実装に進む)。出力先は `tests/unit/` 配下とし、演算ごとに個別のテストファイル(`test_add.py` など)に分ける。テストケースは各 `specs/<operation>/tasks.md` に列挙された正常系・異常系の項目を網羅すること。テスト関数にも[Docstringの方針](#docstringの方針)に従いNumPyスタイルのdocstringを付与すること。

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

四則演算の実装では、[TDDでの実装の進め方](#tddでの実装の進め方)に記載の「演算ごとに1サイクル」が最小のPR単位となる。1つの演算のテスト・実装・lint/mypy確認が完了しPRがマージされてから、次の演算のブランチを切ること。
