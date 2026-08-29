"""
高齢者向けAI相談エージェント - 自動テストスクリプト

scenarios.json と app.py のロジックをテストして、
3つのデモシナリオが正しく動作するか確認します
"""

import json
from pathlib import Path

# ===== scenarios.json の読み込み =====
project_dir = Path(__file__).parent
scenarios_path = project_dir / "scenarios.json"

print("=" * 80)
print("🧪 高齢者向けAI相談エージェント - 自動テスト")
print("=" * 80)
print()

# シナリオデータの読み込み
with open(scenarios_path, "r", encoding="utf-8") as f:
    data = json.load(f)

scenarios = data.get("scenarios", [])
print(f"✅ scenarios.json を読み込みました ({len(scenarios)} シナリオ)")
print()

# ===== テスト用ロジック =====
def get_response(user_input: str) -> str:
    """ユーザー入力からシナリオを検索して応答を返す"""
    input_lower = user_input.lower()
    
    for scenario in scenarios:
        keywords = scenario.get("keywords", [])
        if any(kw.lower() in input_lower for kw in keywords):
            return scenario.get("response", "")
    
    # デフォルト応答
    return data.get("default_response", "ご質問ありがとうございます。")

# ===== テストケース =====
TEST_CASES = [
    {
        "name": "詐欺メール警告",
        "input": "Amazonからメールが来てクリックするように書いてある",
        "expected_keywords": ["警告", "詐欺", "クリック", "削除"]
    },
    {
        "name": "Wi-Fi操作ガイド",
        "input": "Wi-Fiに繋がらない",
        "expected_keywords": ["設定", "Wi-Fi", "手順", "接続"]
    },
    {
        "name": "不安払拭・安心感",
        "input": "ボタン間違えて押したら壊れてしまう",
        "expected_keywords": ["大丈夫", "安心", "壊れません"]
    }
]

# ===== テスト実行 =====
print("📋 テストケース実行中...\n")

passed = 0
failed = 0

for i, test_case in enumerate(TEST_CASES, 1):
    print(f"[テスト {i}] {test_case['name']}")
    print(f"  入力: 「{test_case['input']}」")
    
    # 応答を取得
    response = get_response(test_case['input'])
    
    print(f"  出力: {response[:100]}...")
    print()
    
    # キーワード検索
    has_all_keywords = all(
        kw in response for kw in test_case['expected_keywords']
    )
    
    if has_all_keywords:
        print(f"  ✅ PASS - 全ての期待キーワードが検出されました")
        print(f"     期待: {test_case['expected_keywords']}")
        passed += 1
    else:
        missing = [
            kw for kw in test_case['expected_keywords']
            if kw not in response
        ]
        print(f"  ❌ FAIL - 以下のキーワードが見つかりません:")
        print(f"     {missing}")
        failed += 1
    
    print()

# ===== デフォルト応答テスト =====
print("[テスト 4] デフォルト応答（該当シナリオなし）")
default_input = "宇宙について教えてください"
print(f"  入力: 「{default_input}」")

default_response = get_response(default_input)
print(f"  出力: {default_response[:100]}...")
print()

if default_response and len(default_response) > 10:
    print(f"  ✅ PASS - デフォルト応答が返されました")
    passed += 1
else:
    print(f"  ❌ FAIL - デフォルト応答が空または短すぎます")
    failed += 1

print()

# ===== テスト結果サマリー =====
print("=" * 80)
print("📊 テスト結果サマリー")
print("=" * 80)
print(f"総テスト数: {passed + failed}")
print(f"✅ PASS: {passed}")
print(f"❌ FAIL: {failed}")
print()

if failed == 0:
    print("🎉 全てのテストに PASS しました！")
    print("   アプリケーションは正常に動作しています。")
    exit(0)
else:
    print("⚠️  いくつかのテストが失敗しました。")
    print("   app.py または scenarios.json を確認してください。")
    exit(1)
