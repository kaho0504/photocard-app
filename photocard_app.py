"""
所持写真一覧アプリ（プロトタイプ）- Streamlit版
実行方法:
  1) pip install streamlit
  2) streamlit run photocard_app.py
"""

import streamlit as st
import json
import os
from datetime import date

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photocard_data.json")


def load_cards():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("cards", []), data.get("next_id", 1)
        except (json.JSONDecodeError, OSError):
            pass
    return None, None


def save_cards(cards, next_id):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"cards": cards, "next_id": next_id}, f, ensure_ascii=False, indent=2)

# ---------- データ定義 ----------
GROUPS = [
    {"id": "g1", "name": "SixTONES", "color": "#F6D9E3"},
    {"id": "g2", "name": "B&ZAI", "color": "#DCEAF7"},
    {"id": "g3", "name": "KEY TO LIT", "color": "#FDEBD3"},
]

MEMBERS = {
    "g1": ["ジェシー", "田中樹", "森本慎太郎", "髙地優吾", "京本大我", "松村北斗"],
    "g2": ["橋本涼", "本髙克樹", "今野大輝", "川崎星輝", "稲葉通陽", "鈴木悠仁", "菅田琳寧", "矢花黎"],
    "g3": ["岩﨑大昇", "井上瑞稀", "中村嶺亜", "猪狩蒼弥", "佐々木大光"],
}

PREFIX = {"g1": "ST", "g2": "BZI", "g3": "KEY"}


def group_of(gid):
    return next(g for g in GROUPS if g["id"] == gid)


def today_str():
    d = date.today()
    return f"{d.month:02d}/{d.day:02d}"


# ---------- 初期データ（保存ファイルがあればそちらを読み込む） ----------
if "cards" not in st.session_state:
    loaded_cards, loaded_next_id = load_cards()
    if loaded_cards is not None:
        st.session_state.cards = loaded_cards
        st.session_state.next_id = loaded_next_id
    else:
        st.session_state.cards = [
            {"id": 1, "group": "g1", "member": "松村北斗", "code": "ST-0231", "date": "03/14"},
            {"id": 2, "group": "g2", "member": "橋本涼", "code": "BZI-0089", "date": "05/02"},
            {"id": 3, "group": "g1", "member": "京本大我", "code": "ST-0177", "date": "06/21"},
            {"id": 4, "group": "g3", "member": "岩﨑大昇", "code": "KEY-0012", "date": "07/09"},
        ]
        st.session_state.next_id = 5
        save_cards(st.session_state.cards, st.session_state.next_id)
if "show_add" not in st.session_state:
    st.session_state.show_add = False
if "add_step" not in st.session_state:
    st.session_state.add_step = "group"
if "draft" not in st.session_state:
    st.session_state.draft = {"group": None, "member": None}
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = None
if "sort_key" not in st.session_state:
    st.session_state.sort_key = "date_new"
if "filter_group" not in st.session_state:
    st.session_state.filter_group = None
if "filter_member" not in st.session_state:
    st.session_state.filter_member = None
if "filter_step" not in st.session_state:
    st.session_state.filter_step = None


# ---------- 見た目（パステル・柔らかめ） ----------
st.set_page_config(page_title="所持写真一覧", page_icon="🎀", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg,#FDF7F9 0%,#F7F4FB 100%);
    }
    .photo-card {
        background: #FFFFFFCC;
        border-radius: 18px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .photo-date { font-size: 13px; color: #8C7A93; }
    .photo-code { font-size: 16px; font-weight: 700; color: #5A4A5C; }
    .photo-sub { font-size: 12px; color: #B3A6B8; margin-top: 3px; }
    div.stButton > button {
        border-radius: 14px;
        border: 1px solid #EAD9E2;
        background: #FBF6F8;
        color: #5A4A5C;
    }
    /* スマホ幅でも横並びのカラムを縦積みにせず維持する */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        align-items: center !important;
    }
    [data-testid="stHorizontalBlock"] > div {
        min-width: 0 !important;
    }
    @media (max-width: 600px) {
        h1 { font-size: 26px !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎀 所持写真一覧")

# ---------- 並べかえ & 追加ボタン ----------
col_sort, col_add = st.columns([3, 1])
with col_sort:
    label_to_key = {"登録日順（新しい順）": "date_new", "登録日順（古い順）": "date_old"}
    key_to_label = {v: k for k, v in label_to_key.items()}
    chosen_label = st.selectbox(
        "並べかえ",
        list(label_to_key.keys()),
        index=list(label_to_key.values()).index(st.session_state.sort_key),
    )
    st.session_state.sort_key = label_to_key[chosen_label]
with col_add:
    st.write("")
    st.write("")
    if st.button("＋ 追加", use_container_width=True):
        st.session_state.show_add = True
        st.session_state.add_step = "group"
        st.session_state.draft = {"group": None, "member": None}
        st.session_state.filter_step = None
        st.session_state.confirm_delete = None
        st.rerun()

# ---------- 絞り込みボタン ----------
col_fg, col_fm, col_fc = st.columns([2, 2, 1])
with col_fg:
    g_label = "グループ"
    if st.session_state.filter_group:
        g_label += f"：{group_of(st.session_state.filter_group)['name']}"
    if st.button(g_label, key="open_filter_group", use_container_width=True):
        st.session_state.filter_step = "group"
        st.session_state.show_add = False
        st.session_state.confirm_delete = None
        st.rerun()
with col_fm:
    m_label = "メンバー"
    if st.session_state.filter_member:
        m_label += f"：{st.session_state.filter_member}"
    if st.button(m_label, key="open_filter_member", use_container_width=True):
        st.session_state.filter_step = "member"
        st.session_state.show_add = False
        st.session_state.confirm_delete = None
        st.rerun()
with col_fc:
    st.write("")
    if (st.session_state.filter_group or st.session_state.filter_member) and st.button(
        "解除", key="clear_filter"
    ):
        st.session_state.filter_group = None
        st.session_state.filter_member = None
        st.rerun()


# ---------- 追加フロー（ダイアログ） ----------
@st.dialog("写真を登録")
def add_dialog():
    step = st.session_state.add_step
    draft = st.session_state.draft

    if step == "group":
        st.write("グループを選択")
        for g in GROUPS:
            if st.button(g["name"], key=f"pick_group_{g['id']}", use_container_width=True):
                st.session_state.draft["group"] = g["id"]
                st.session_state.add_step = "member"
                st.rerun()

    elif step == "member":
        st.write(f"{group_of(draft['group'])['name']} のメンバーを選択")
        for m in MEMBERS[draft["group"]]:
            if st.button(m, key=f"pick_member_{m}", use_container_width=True):
                st.session_state.draft["member"] = m
                st.session_state.add_step = "code"
                st.rerun()
        if st.button("戻る"):
            st.session_state.add_step = "group"
            st.rerun()

    elif step == "code":
        g = group_of(draft["group"])
        st.write(f"{g['name']} ・ {draft['member']}")
        col_prefix, col_input = st.columns([1, 3])
        with col_prefix:
            st.markdown(f"**{PREFIX[draft['group']]}-**")
        with col_input:
            suffix = st.text_input("品番（残りの番号）", placeholder="0231", label_visibility="collapsed")
        if st.button("登録する", use_container_width=True):
            if suffix.strip():
                st.session_state.cards.insert(
                    0,
                    {
                        "id": st.session_state.next_id,
                        "group": draft["group"],
                        "member": draft["member"],
                        "code": f"{PREFIX[draft['group']]}-{suffix.strip()}",
                        "date": today_str(),
                    },
                )
                st.session_state.next_id += 1
                save_cards(st.session_state.cards, st.session_state.next_id)
                st.session_state.show_add = False
                st.rerun()
        if st.button("戻る", key="back_from_code"):
            st.session_state.add_step = "member"
            st.rerun()





# ---------- 絞り込み：グループ選択ダイアログ ----------
@st.dialog("グループで絞り込む")
def filter_group_dialog():
    for g in GROUPS:
        if st.button(g["name"], key=f"filter_group_{g['id']}", use_container_width=True):
            st.session_state.filter_group = g["id"]
            st.session_state.filter_member = None
            st.session_state.filter_step = None
            st.rerun()





# ---------- 絞り込み：メンバー選択ダイアログ ----------
@st.dialog("メンバーで絞り込む")
def filter_member_dialog():
    target_groups = [st.session_state.filter_group] if st.session_state.filter_group else [g["id"] for g in GROUPS]
    for gid in target_groups:
        g = group_of(gid)
        if not st.session_state.filter_group:
            st.caption(g["name"])
        for m in MEMBERS[gid]:
            if st.button(m, key=f"filter_member_{gid}_{m}", use_container_width=True):
                st.session_state.filter_group = gid
                st.session_state.filter_member = m
                st.session_state.filter_step = None
                st.rerun()





# ---------- 削除確認ダイアログ ----------
@st.dialog("この写真を削除しますか？")
def confirm_delete_dialog():
    card = next(c for c in st.session_state.cards if c["id"] == st.session_state.confirm_delete)
    g = group_of(card["group"])
    st.write(f"{g['name']} ・ {card['member']} ・ {card['code']}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("キャンセル", use_container_width=True):
            st.session_state.confirm_delete = None
            st.rerun()
    with col2:
        if st.button("削除する", use_container_width=True, type="primary"):
            st.session_state.cards = [
                c for c in st.session_state.cards if c["id"] != st.session_state.confirm_delete
            ]
            save_cards(st.session_state.cards, st.session_state.next_id)
            st.session_state.confirm_delete = None
            st.rerun()


# ---------- ダイアログの呼び出し（同時に1つだけ開く） ----------
if st.session_state.confirm_delete is not None:
    confirm_delete_dialog()
elif st.session_state.show_add:
    add_dialog()
elif st.session_state.filter_step == "group":
    filter_group_dialog()
elif st.session_state.filter_step == "member":
    filter_member_dialog()


# ---------- 一覧表示 ----------
cards = st.session_state.cards
if st.session_state.filter_group:
    cards = [c for c in cards if c["group"] == st.session_state.filter_group]
if st.session_state.filter_member:
    cards = [c for c in cards if c["member"] == st.session_state.filter_member]

cards = sorted(
    cards, key=lambda c: c["date"], reverse=(st.session_state.sort_key == "date_new")
)

if not cards:
    st.info("まだ写真が登録されていません")

for c in cards:
    g = group_of(c["group"])
    col_main, col_del = st.columns([6, 1])
    with col_main:
        st.markdown(
            f"""
            <div class="photo-card">
                <span class="photo-date">{c['date']}</span>
                &nbsp;&nbsp;
                <span class="photo-code">{c['code']}</span>
                <div class="photo-sub">🎨 {g['name']} ・ {c['member']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_del:
        st.write("")
        if st.button("×", key=f"del_{c['id']}"):
            st.session_state.confirm_delete = c["id"]
            st.session_state.show_add = False
            st.session_state.filter_step = None
            st.rerun()
