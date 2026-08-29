# 相談エージェント

高齢者向けAI相談エージェント - 創立50周年記念式典デモンストレーション

## 概要

このアプリケーションは、高齢者やIT低リテラシー層が詐欺メール、操作不安、心理的な不安などに直面した時に、AIが24/7でサポートするシステムです。

## 技術スタック

- **フロントエンド**: Streamlit 1.28+
- **言語**: Python 3.9+
- **ホスティング**: Streamlit Cloud

## クイックスタート

### ローカル実行

```bash
pip install -r requirements.txt
streamlit run app.py
```

ブラウザが自動で `http://localhost:8501` で開きます。

### Streamlit Cloud へのデプロイ

1. GitHub にこのリポジトリを push
2. [Streamlit Cloud](https://streamlit.io/cloud) にアクセス
3. GitHub リポジトリを選択してデプロイ
4. `https://[app-name].streamlit.app` でアクセス可能

## デモシナリオ

### シナリオ1: 詐欺メール警告
```
ユーザー: Amazonからメールが来てクリックするように書いてある
AI: 🚨 警告を表示 → 削除を推奨
```

### シナリオ2: Wi-Fi操作ガイド
```
ユーザー: Wi-Fiに繋がらない
AI: 📱 4ステップの操作ガイドを表示
```

### シナリオ3: 不安払拭
```
ユーザー: ボタン間違えて押したら壊れる？
AI: 💪 温かく共感的な返答で安心感を提供
```

## ファイル構成

```
.
├── app.py                  # Streamlit メインアプリ
├── scenarios.json          # デモシナリオデータ
├── requirements.txt        # Python依存パッケージ
├── test_scenarios.py       # 自動テストスクリプト
├── .streamlit/
│   └── config.toml        # Streamlit設定
├── spec.md                # 仕様書
├── plan.md                # 実装計画
├── tasks.md               # タスク分解
└── README.md              # このファイル
```

## テスト

自動テストスクリプトで3シナリオの動作を確認：

```bash
python test_scenarios.py
```

## ライセンス

このプロジェクトは創立50周年記念式典用のデモンストレーション目的で作成されました。

## お問い合わせ

技術的な質問やバグ報告は、GitHub Issues までお願いします。
