# 実装計画: 高齢者向けAI相談エージェント

**ブランチ**: `feature/consultation-agent-demo` | **日付**: 2026-08-22 | **仕様**: spec.md  
**入力**: spec.md の要件と1日完成フロー

---

## 📌 概要

式典でのデモンストレーション用に、Streamlit を使ったシンプルなテキストベース相談エージェントを1日で構築する。詐欺警告・操作ガイド・不安払拭の3シナリオをハードコード＋最小限のLLM連携で実装。

---

## 🔧 技術コンテキスト

| 項目 | 内容 |
|-----|------|
| **言語/バージョン** | Python 3.9+ |
| **フレームワーク** | Streamlit 1.28+ |
| **主要依存ライブラリ** | openai, streamlit, python-dotenv |
| **ストレージ** | N/A（メモリベース、セッション単位） |
| **テスト** | 手動テスト（3デモシナリオで確認） |
| **ターゲット** | Streamlit Cloud（無料ティア） |
| **プロジェクト型** | シングルアプリケーション（Web） |
| **パフォーマンス目標** | 応答時間 ≤ 3秒 |
| **制約** | 1日（8時間以内）、3人以下でのチーム |
| **スケール** | デモ用（同時実行1ユーザー） |

---

## 📐 アーキテクチャ設計

### 全体構成

```
┌─────────────────────────────────────────────┐
│        Streamlit Frontend（ブラウザ）         │
│  ┌────────────────────────────────────────┐ │
│  │  - チャット入力フォーム                 │ │
│  │  - メッセージ履歴表示                   │ │
│  │  - 送信ボタン / リセット                │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│   Logic Layer（Python backend in Streamlit） │
│  ┌────────────────────────────────────────┐ │
│  │  1. ユーザー入力を受け取り             │ │
│  │  2. キーワード検索（パターンマッチ）   │ │
│  │  3. 対応するシナリオ応答を返す         │ │
│  │  4. （オプション）LLM で返答を調整    │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│    Data Layer（デモシナリオ + LLM API）      │
│  ┌────────────────────────────────────────┐ │
│  │  scenarios.json                        │ │
│  │  ├─ 詐欺検知シナリオ                   │ │
│  │  ├─ 操作ガイドシナリオ                 │ │
│  │  └─ 安心感シナリオ                     │ │
│  │                                        │ │
│  │  OpenAI API（オプション）              │ │
│  │  └─ より自然な応答をする場合は利用    │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### データフロー

```
User Input
    ↓
[Keyword Detection] → "詐欺" + "メール" キーワードある？
    ↓ YES           ↓ NO
 詐欺シナリオ      [Keyword Detection] → "Wi-Fi" + "繋がらない"？
    ↓               ↓ YES              ↓ NO
[LLM Polish]      操作ガイド         [Keyword Detection] → "壊れる" / "不安"？
    ↓             [LLM Polish]        ↓ YES                ↓ NO
返答表示            ↓                  安心感             デフォルト応答
                  返答表示           [LLM Polish]           ↓
                                        ↓                 返答表示
                                      返答表示
```

---

## 🏗️ ファイル構成

```
相談エージェントの作成/
├── spec.md                    # 仕様書（完了）
├── plan.md                    # 本ファイル（実装計画）
├── tasks.md                   # タスク分解（8時間スケジュール）
├── app.py                     # ★ Streamlit アプリ本体
├── scenarios.json             # ★ デモシナリオデータ
├── requirements.txt           # ★ Python 依存パッケージ
├── .streamlit/
│   └── config.toml           # Streamlit 設定ファイル
└── README.md                 # デプロイ・実行ガイド（後日）
```

---

## 💻 実装の詳細設計

### 1. **Streamlit UI コンポーネント** (`app.py` の主要部)

#### ヘッダー（シンプル・大きな文字）
```python
st.set_page_config(
    page_title="AI相談エージェント",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 大きなタイトル＋説明
st.markdown("""
# 🤖 高齢者向けAI相談エージェント
お困りなことはありますか？何でもお話ください。
""")
```

#### チャット表示エリア
```python
# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# チャット履歴の表示
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"**👤 あなた**: {message['content']}")
        else:
            st.markdown(f"**🤖 AI**: {message['content']}")
```

#### 入力＆ボタン
```python
# ユーザー入力
user_input = st.text_input(
    "質問してください：",
    key="user_input",
    placeholder="例：メールが来た、Wi-Fi繋がらない"
)

# 送信ボタン
if st.button("📤 送信", use_container_width=True, key="send_btn"):
    if user_input:
        handle_message(user_input)

# リセットボタン
if st.button("🔄 リセット", use_container_width=True, key="reset_btn"):
    st.session_state.messages = []
    st.rerun()
```

### 2. **ロジック層** (`app.py` のメイン処理)

#### キーワード検索 + マッピング
```python
def get_response(user_input: str) -> str:
    """
    ユーザー入力からシナリオを検索して応答を返す
    """
    input_lower = user_input.lower()
    
    # シナリオA: 詐欺検知
    fraud_keywords = ["詐欺", "メール", "クリック", "amazon", "apple", "bank"]
    if any(kw in input_lower for kw in fraud_keywords):
        return get_fraud_response(user_input)
    
    # シナリオB: 操作ガイド
    guide_keywords = ["wi-fi", "繋がら", "接続", "操作", "やり方", "どうやって"]
    if any(kw in input_lower for kw in guide_keywords):
        return get_guide_response(user_input)
    
    # シナリオC: 安心感
    concern_keywords = ["壊れる", "壊してしまった", "不安", "怖い", "失敗", "間違え"]
    if any(kw in input_lower for kw in concern_keywords):
        return get_reassurance_response(user_input)
    
    # デフォルト応答
    return get_default_response(user_input)
```

#### 各シナリオの応答関数
```python
def get_fraud_response(user_input: str) -> str:
    """詐欺警告応答"""
    return """🚨 【警告】これは詐欺メール（フィッシング）の可能性が非常に高いです。

❌ やってはいけないこと：
  - そのメール内のリンクをクリックしない
  - 個人情報（パスワード、電話番号など）を入力しない
  - メール内の番号に電話しない

✅ やるべきこと：
  - そのメールは削除してください
  - 本物の公式サイトから直接ログインしてください
  - 不安なら家族や友人に相談してください

安心してください。本物のAmazonやAppleからは、このような急かすメールは来ません。"""

def get_guide_response(user_input: str) -> str:
    """操作ガイド応答"""
    return """分かりました。以下の手順をお試しください。

📱 【Wi-Fi接続手順】
1️⃣ スマートフォンの『設定』アプリを開く
2️⃣ 『Wi-Fi』をタップ
3️⃣ 接続したい自分のWi-Fi名を選ぶ
4️⃣ パスワードを入力して『接続』をタップ

✅ これでつながるはずです。

💡 うまくいかない場合：
 - スマートフォンを再起動してみてください
 - ルーターの電源を一度切ってから、30秒後に入れ直してください
 - それでも繋がらないときは、お近くの人に聞いてみてください。"""

def get_reassurance_response(user_input: str) -> str:
    """安心感応答"""
    return """大丈夫ですよ。安心してください。

✅ スマートフォンやパソコンについて：
 - ボタンを少し押しただけでは、まず壊れません
 - 間違えて何かしても、ほぼ大丈夫です
 - 不安なことは、ためらわずに周りの人に聞いてください

🤖 【AI相談エージェントから】
あなたの質問や不安は、まったく問題ありません。
むしろ、分からないままにしておく方が問題です。
いつでも何回でも聞いてくださいね。
私たちは、あなたのサポートのためにここにいます。"""

def get_default_response(user_input: str) -> str:
    """デフォルト応答"""
    return f"""ご質問ありがとうございます。
    
「{user_input}」ですね。
申し訳ありませんが、この質問について具体的な情報を持っていません。

以下をお試しください：
 - もう少し詳しく説明してもらえますか？
 - キーワード（例：「Wi-Fi」「メール」など）を教えてください
 - お近くの家族や友人に相談することもお勧めします。

何かお力になれることはありますか？"""
```

### 3. **デモシナリオデータ** (`scenarios.json`)

```json
{
  "scenarios": [
    {
      "id": "fraud_detection",
      "keywords": ["詐欺", "メール", "クリック", "amazon", "apple"],
      "response": "【警告】これは詐欺メール...（上記参照）"
    },
    {
      "id": "operation_guide",
      "keywords": ["wi-fi", "繋がら", "接続", "操作"],
      "response": "分かりました。以下の手順を...（上記参照）"
    },
    {
      "id": "reassurance",
      "keywords": ["壊れる", "不安", "怖い", "失敗"],
      "response": "大丈夫ですよ。安心してください...（上記参照）"
    }
  ]
}
```

### 4. **依存パッケージ** (`requirements.txt`)

```
streamlit==1.28.1
openai==1.3.5
python-dotenv==1.0.0
```

### 5. **設定ファイル** (`.streamlit/config.toml`)

```toml
[theme]
primaryColor = "#4f46e5"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f3f4f6"
textColor = "#1f2937"
font = "sans serif"

[client]
showErrorDetails = false
showSidebarNavigation = false

[logger]
level = "warning"
```

---

## 🎨 UI/UX 設計原則

### 高齢者対応の配慮
- **フォントサイズ**: 最小18px（デフォルト Streamlit = 16px より大きく）
- **色分け**: ユーザー = 青 / AI = 紫（目立つ、区別明確）
- **行間**: 十分な余白（読みやすさ）
- **ボタンサイズ**: 50px以上の高さ（押しやすい）
- **言葉づかい**: 敬語・やさしい日本語（難しい用語なし）
- **情報量**: 1画面に詰め込まない（スクロール最小限）

### レスポンシブデザイン
- デスクトップ、タブレット、スマートフォン全対応
- Streamlit が自動で対応

---

## 🧪 テスト戦略（1日版・簡易）

### テスト項目（手動テスト）

| # | テスト | 条件 | 期待結果 | 確認 |
|---|--------|------|---------|------|
| T-1 | 詐欺警告 | "Amazonからメールが来てクリックしろって" | 🚨警告が表示される | ✅ |
| T-2 | 操作ガイド | "Wi-Fi繋がらない" | 手順が番号付きで表示 | ✅ |
| T-3 | 安心感 | "ボタン間違えて押したら壊れる？" | 温かい返答が表示 | ✅ |
| T-4 | 履歴表示 | 3回以上メッセージ送信 | 過去のメッセージが表示される | ✅ |
| T-5 | UI/UX | Chrome / Safari で閲覧 | 文字が大きく、色が見やすい | ✅ |
| T-6 | 応答速度 | メッセージ送信後 | 2秒以内に応答表示 | ✅ |
| T-7 | デプロイ | Streamlit Cloud にアップ | ブラウザで動作する | ✅ |

---

## 🚀 デプロイ戦略

### ローカル開発
```bash
# 環境構築
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# ローカル実行
streamlit run app.py
```

### Streamlit Cloud へのデプロイ
1. GitHub リポジトリに push
2. Streamlit Cloud で接続
3. ブラウザでアクセス（https://[app-name].streamlit.app）

### デプロイ用ファイル
- `requirements.txt` ← 必須
- `.streamlit/config.toml` ← セッティング
- `app.py` ← アプリ本体
- `scenarios.json` ← デモデータ

---

## 🔐 セキュリティ & ベストプラクティス

### API キー管理（LLM 連携時）
```python
# .env に保存
OPENAI_API_KEY=sk-...

# コード内で読み込む
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

### 注意事項
- API キーを GitHub にコミットしない
- `.gitignore` に `.env` を追加
- Streamlit Cloud の Secrets 機能を使う

---

## 📈 パフォーマンス最適化（1日版）

### 最適化ポイント
- ✅ セッション状態をキャッシュ（Streamlit の `@st.cache_data`）
- ✅ 不要な再レンダリング回避（`key` パラメータ活用）
- ✅ LLM API 呼び出しは最小限（パターンマッチ優先）

### 応答速度目標
- パターンマッチ: ≤ 100ms
- LLM API: ≤ 2秒（API待機含む）
- **合計**: ≤ 3秒 ✅

---

## 🎯 実装ガイドライン

### Phase 1: 基本 UI 構築（1時間）
- [ ] Streamlit アプリの骨組み
- [ ] チャット表示・入力エリア
- [ ] 送信・リセットボタン

### Phase 2: ロジック実装（1.5時間）
- [ ] キーワード検索ロジック
- [ ] 3つのシナリオ応答関数
- [ ] デフォルト応答

### Phase 3: 統合・テスト（1時間）
- [ ] 3デモシナリオの動作確認
- [ ] UI/UX 最終調整
- [ ] ローカルテスト完了

### Phase 4: デプロイ（0.5時間）
- [ ] Streamlit Cloud へのデプロイ
- [ ] 本番環境でのテスト確認

---

## ⚠️ リスク & 対策

| リスク | 影響 | 対策 |
|--------|------|------|
| **LLM API が遅い** | 応答遅延 | パターンマッチを優先、LLM は補助的に |
| **デプロイ失敗** | 式典で使えない | ローカル環境を本番機に用意（バックアップ） |
| **UI 調整時間超過** | スケジュール遅延 | テンプレート利用、カスタマイズ最小限 |
| **キーワード漏れ** | シナリオ検出失敗 | 実装後すぐにテスト、漏れあれば追加 |

---

## 📝 コード品質基準（1日版は簡易版）

- ✅ 関数は明確な役割を持つ（10行～50行程度）
- ✅ コメントは重要な処理のみ（自明でない部分）
- ✅ 変数名は分かりやすく（`msg` より `user_message`）
- ✅ エラーハンドリング：try/catch で API 呼び出しをカバー
- ✅ テスト：3デモシナリオで確認（自動テストは 1日版では省略）

---

## 🎬 式典でのデモンストレーション方法

### セットアップ
1. Streamlit Cloud リンクをプロジェクターに表示
2. ノートパソコンから入力（またはタッチペン / 音声入力をシミュレート）

### デモシーケンス
```
【司会】「それでは、AI相談エージェントのデモです」

【デモ1】 詐欺メール相談
  入力: 「Amazonからメールが来て、クリックするように書いてある」
  出力: 🚨警告が表示される

【デモ2】 操作ガイド
  入力: 「Wi-Fiに繋がらない」
  出力: 手順が表示される

【デモ3】 不安払拭
  入力: 「ボタン間違えて押したら壊れてしまう」
  出力: 温かい返答が表示される

【司会】「このように、AIが高齢者の不安や疑問に
         24/7 で応答することで、
         社会課題（サポート不足）を解決できます」
```

---

## 📚 参考・今後の拡張

### 1日版の次（1週間版 / 本番化）
- 音声入出力（Web Speech API）
- SQLite での履歴永続化
- より複雑な会話フロー
- ユーザー認証
- 複数言語対応
- モバイルアプリ化

### 技術的負債
- [ ] 単体テスト追加（pytest）
- [ ] E2E テスト（Playwright）
- [ ] パフォーマンス計測（Lighthouse）
- [ ] ログ・モニタリング

---

**版**: v1.0 | **作成日**: 2026-08-22 | **次**: tasks.md（作業タスク分解）→ 実装開始
