"""
高齢者向けAI相談エージェント - Streamlit版
式典デモンストレーション用 MVP

技術: Streamlit + Python
期限: 2026-08-22（1日完成）
"""

import streamlit as st
import json
from pathlib import Path

# ===========================
# ページ設定
# ===========================
st.set_page_config(
    page_title="AI相談エージェント",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# ===========================
# スタイル設定（高齢者向け）
# ===========================
st.markdown("""
    <style>
        /* 全体フォントサイズを大きく */
        html, body, [class*="css"]  {
            font-size: 18px;
        }
        
        /* タイトルを特に大きく */
        h1 {
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        /* メッセージフォント */
        .user-message {
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            font-size: 18px;
            border-left: 4px solid #2196F3;
        }
        
        .ai-message {
            background-color: #f3e5f5;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            font-size: 18px;
            border-left: 4px solid #9c27b0;
        }
        
        /* ボタンをより大きく・目立つように */
        .stButton > button {
            font-size: 18px;
            padding: 15px 30px;
            height: 60px;
            border-radius: 8px;
        }
        
        /* 入力ボックスも大きく */
        .stTextInput > div > div > input {
            font-size: 18px;
            padding: 12px;
        }
        
        /* コンテナの余白 */
        .main {
            padding: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ===========================
# セッション状態の初期化
# ===========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ===========================
# シナリオデータのロード
# ===========================
def load_scenarios():
    """scenarios.json を読み込む"""
    scenario_path = Path(__file__).parent / "scenarios.json"
    if scenario_path.exists():
        with open(scenario_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "scenarios": [],
        "default_response": "申し訳ありませんが、その質問についてお答えできません。もう一度お試しください。"
    }

# ===========================
# ロジック層：応答生成
# ===========================
def get_response(user_input: str) -> str:
    """
    ユーザー入力からシナリオを検索して応答を返す
    
    Args:
        user_input: ユーザーの入力テキスト
    
    Returns:
        AI相談エージェントの応答
    """
    scenarios = load_scenarios()
    input_lower = user_input.lower()
    
    # 各シナリオのキーワードをチェック
    for scenario in scenarios.get("scenarios", []):
        keywords = scenario.get("keywords", [])
        if any(kw.lower() in input_lower for kw in keywords):
            return scenario.get("response", "")
    
    # デフォルト応答
    return scenarios.get(
        "default_response",
        "ご質問ありがとうございます。申し訳ありませんが、この質問について具体的な情報を持っていません。"
    )


def handle_message(user_input: str):
    """
    ユーザーメッセージを処理して、セッション状態を更新
    
    Args:
        user_input: ユーザーの入力テキスト
    """
    if not user_input.strip():
        return
    
    # ユーザーメッセージをセッションに追加
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # AI応答を生成
    ai_response = get_response(user_input)
    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_response
    })
    
    # 画面を再描画
    st.rerun()


# ===========================
# UI: ヘッダー
# ===========================
st.markdown("""
# 🤖 高齢者向けAI相談エージェント

お困りなことはありますか？何でもお話ください。  
このエージェントが、あなたのお困りごとをサポートします。
""")

st.divider()

# ===========================
# UI: チャット表示エリア
# ===========================
st.markdown("### 📋 相談内容")

chat_container = st.container()
with chat_container:
    if st.session_state.messages:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                <b>👤 あなた：</b><br>{message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="ai-message">
                <b>🤖 AI相談エージェント：</b><br>{message["content"]}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📝 質問を入力すると、ここに会話が表示されます。")

st.divider()

# ===========================
# UI: 入力フォーム
# ===========================
st.markdown("### ✍️ 質問を入力してください")

# テキスト入力
user_input = st.text_input(
    label="質問してください：",
    placeholder="例：『Amazonからメールが来た』『Wi-Fiに繋がらない』『ボタン間違えて押したら...』",
    key="user_input_field",
    label_visibility="collapsed"
)

# ボタン配置（3列レイアウト）
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    send_btn = st.button(
        "📤 送信",
        use_container_width=True,
        key="send_button",
        help="質問を送信します"
    )

with col2:
    reset_btn = st.button(
        "🔄 リセット",
        use_container_width=True,
        key="reset_button",
        help="会話をリセットします"
    )

with col3:
    st.empty()  # スペーサー

# ===========================
# イベントハンドリング
# ===========================
# 送信ボタンが押された時
if send_btn:
    if user_input.strip():
        handle_message(user_input)
    else:
        st.warning("📢 質問を入力してください。")

# リセットボタンが押された時
if reset_btn:
    st.session_state.messages = []
    st.rerun()

# ===========================
# フッター
# ===========================
st.divider()
st.markdown("""
**📌 このエージェントについて**

このAI相談エージェントは、高齢者が日々の不安や疑問に対して、いつでも相談できるシステムです。

✅ 詐欺メールの警告  
✅ スマートフォンやパソコンの操作ガイド  
✅ 不安や心配事への共感と励まし
""")
