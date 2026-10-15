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
from itertools import combinations

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photocard_data.json")

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


def pair_combos(gid):
    return [f"{a}・{b}" for a, b in combinations(MEMBERS[gid], 2)]


# ---------- 保存／読み込み ----------
def load_cards():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                cards = data.get("cards", [])
                for c in cards:
                    c.setdefault("qty", 1)
                    c.setdefault("favorite", False)
                return cards, data.get("next_id", 1)
        except (json.JSONDecodeError, OSError):
            pass
    return None, None


def save_cards(cards, next_id):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"cards": cards, "next_id": next_id}, f, ensure_ascii=False, indent=2)


def persist():
    save_cards(st.session_state.cards, st.session_state.next_id)


# ---------- 初期データ ----------
if "cards" not in st.session_state:
    loaded_cards, loaded_next_id = load_cards()
    if loaded_cards is not None:
        st.session_state.cards = loaded_cards
        st.session_state.next_id = loaded_next_id
    else:
        st.session_state.cards = [
            {"id": 1, "group": "g1", "member": "松村北斗", "code": "ST-0231", "qty": 2, "date": "03/14", "favorite": False},
            {"id": 2, "group": "g2", "member": "橋本涼", "code": "BZI-0089", "qty": 1, "date": "05/02", "favorite": True},
            {"id": 3, "group": "g1", "member": "京本大我", "code": "ST-0177", "qty": 1, "date": "06/21", "favorite": False},
            {"id": 4, "group": "g3", "member": "岩﨑大昇", "code": "KEY-0012", "qty": 3, "date": "07/09", "favorite": False},
        ]
        st.session_state.next_id = 5
        persist()

for key, default in {
    "page": "list",
    "sort_key": "date_new",
    "filter_group": None,
    "filter_member": None,
    "filter_step": None,
    "show_add": False,
    "add_step": "group",
    "draft": {"group": None, "type": None, "member": None},
    "confirm_delete": None,
    "confirm_unfav": None,
    "edit_card": None,
    "search_group": None,
    "search_member": None,
    "search_code": "",
    "search_result": "idle",  # idle | found | notfound
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def close_all_dialogs():
    st.session_state.show_add = False
    st.session_state.filter_step = None
    st.session_state.confirm_delete = None
    st.session_state.confirm_unfav = None
    st.session_state.edit_card = None


# ---------- 見た目 ----------
st.set_page_config(page_title="所持写真一覧", page_icon="🎀", layout="centered")

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg,#FDF7F9 0%,#F7F4FB 100%); }
    .photo-card { background: #FFFFFFCC; border-radius: 18px; padding: 14px 18px; margin-bottom: 10px; }
    .photo-date { font-size: 13px; color: #8C7A93; }
    .photo-code { font-size: 16px; font-weight: 700; color: #5A4A5C; }
    .photo-sub { font-size: 12px; color: #B3A6B8; margin-top: 3px; }
    .photo-qty { font-size: 12px; color: #B37FA0; font-weight: 700; margin-left: 6px; }
    div.stButton > button { border-radius: 14px; border: 1px solid #EAD9E2; background: #FBF6F8; color: #5A4A5C; }
    [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; align-items: center !important; }
    [data-testid="stHorizontalBlock"] > div { min-width: 0 !important; }
    @media (max-width: 600px) { h1 { font-size: 26px !important; } }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎀 所持写真一覧")

# ---------- ページ切り替え ----------
nav1, nav2, nav3 = st.columns(3)
with nav1:
    if st.button("📋 一覧", use_container_width=True, type="primary" if st.session_state.page == "list" else "secondary"):
        st.session_state.page = "list"
        st.rerun()
with nav2:
    if st.button("🔍 品番検索", use_container_width=True, type="primary" if st.session_state.page == "search" else "secondary"):
        st.session_state.page = "search"
        st.rerun()
with nav3:
    if st.button("♡ お気に入り", use_container_width=True, type="primary" if st.session_state.page == "favorites" else "secondary"):
        st.session_state.page = "favorites"
        st.rerun()

st.write("")


# =====================================================================
# ダイアログ群
# =====================================================================

@st.dialog("写真を登録")
def add_dialog():
    step = st.session_state.add_step
    draft = st.session_state.draft

    if step == "group":
        st.write("グループを選択")
        for g in GROUPS:
            if st.button(g["name"], key=f"ag_{g['id']}", use_container_width=True):
                st.session_state.draft["group"] = g["id"]
                st.session_state.add_step = "type"
                st.rerun()

    elif step == "type":
        g = group_of(draft["group"])
        st.write(f"{g['name']} ・ 追加タイプを選択")
        if st.button("メンバー単体", use_container_width=True):
            st.session_state.draft["type"] = "single"
            st.session_state.add_step = "member"
            st.rerun()
        if st.button("集合", use_container_width=True):
            st.session_state.draft["type"] = "set"
            st.session_state.draft["member"] = "(集合)"
            st.session_state.add_step = "code"
            st.rerun()
        if st.button("ペア（全組み合わせ）", use_container_width=True):
            st.session_state.draft["type"] = "pair"
            st.session_state.add_step = "code"
            st.rerun()
        if st.button("戻る", key="back_type"):
            st.session_state.add_step = "group"
            st.rerun()

    elif step == "member":
        g = group_of(draft["group"])
        st.write(f"{g['name']} のメンバーを選択")
        for m in MEMBERS[draft["group"]]:
            if st.button(m, key=f"am_{m}", use_container_width=True):
                st.session_state.draft["member"] = m
                st.session_state.add_step = "code"
                st.rerun()
        if st.button("戻る", key="back_member"):
            st.session_state.add_step = "type"
            st.rerun()

    elif step == "code":
        g = group_of(draft["group"])
        ptype = draft["type"]

        if ptype == "pair":
            st.write(f"{g['name']} ・ ペア（全{len(pair_combos(draft['group']))}組み合わせ）")
            st.caption("品番は空欄でもOK（あとで編集ボタンから1件ずつ入力できます）")
        else:
            st.write(f"{g['name']} ・ {draft['member']}")

        col_prefix, col_input = st.columns([1, 3])
        with col_prefix:
            st.markdown(f"**{PREFIX[draft['group']]}-**")
        with col_input:
            suffix = st.text_input("品番（残りの番号）", placeholder="0231", label_visibility="collapsed", key="code_suffix_input")
        qty = st.number_input("所持枚数", min_value=1, value=1, step=1, key="qty_input")

        if st.button("登録する", use_container_width=True):
            code = f"{PREFIX[draft['group']]}-{suffix.strip()}" if suffix.strip() else ""
            if ptype == "pair":
                for combo in pair_combos(draft["group"]):
                    st.session_state.cards.insert(
                        0,
                        {
                            "id": st.session_state.next_id,
                            "group": draft["group"],
                            "member": combo,
                            "code": code,
                            "qty": int(qty),
                            "date": today_str(),
                            "favorite": False,
                        },
                    )
                    st.session_state.next_id += 1
            else:
                st.session_state.cards.insert(
                    0,
                    {
                        "id": st.session_state.next_id,
                        "group": draft["group"],
                        "member": draft["member"],
                        "code": code,
                        "qty": int(qty),
                        "date": today_str(),
                        "favorite": False,
                    },
                )
                st.session_state.next_id += 1
            persist()
            st.session_state.show_add = False
            st.rerun()

        back_step = "member" if ptype == "single" else "type"
        if st.button("戻る", key="back_code"):
            st.session_state.add_step = back_step
            st.rerun()


@st.dialog("グループで絞り込む")
def filter_group_dialog():
    for g in GROUPS:
        if st.button(g["name"], key=f"fg_{g['id']}", use_container_width=True):
            st.session_state.filter_group = g["id"]
            st.session_state.filter_member = None
            st.session_state.filter_step = None
            st.rerun()


@st.dialog("メンバーで絞り込む")
def filter_member_dialog():
    target_groups = [st.session_state.filter_group] if st.session_state.filter_group else [g["id"] for g in GROUPS]
    for gid in target_groups:
        g = group_of(gid)
        if not st.session_state.filter_group:
            st.caption(g["name"])
        for m in MEMBERS[gid]:
            if st.button(m, key=f"fm_{gid}_{m}", use_container_width=True):
                st.session_state.filter_group = gid
                st.session_state.filter_member = m
                st.session_state.filter_step = None
                st.rerun()


@st.dialog("この写真を削除しますか？")
def confirm_delete_dialog():
    card = next((c for c in st.session_state.cards if c["id"] == st.session_state.confirm_delete), None)
    if card is None:
        st.session_state.confirm_delete = None
        st.rerun()
        return
    g = group_of(card["group"])
    st.write(f"{g['name']} ・ {card['member']} ・ {card['code'] or '(品番未入力)'}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("キャンセル", use_container_width=True, key="del_cancel"):
            st.session_state.confirm_delete = None
            st.rerun()
    with col2:
        if st.button("削除する", use_container_width=True, type="primary", key="del_ok"):
            st.session_state.cards = [c for c in st.session_state.cards if c["id"] != st.session_state.confirm_delete]
            persist()
            st.session_state.confirm_delete = None
            st.rerun()


@st.dialog("お気に入りから削除しますか？")
def confirm_unfav_dialog():
    card = next((c for c in st.session_state.cards if c["id"] == st.session_state.confirm_unfav), None)
    if card is None:
        st.session_state.confirm_unfav = None
        st.rerun()
        return
    g = group_of(card["group"])
    st.write(f"{g['name']} ・ {card['member']} ・ {card['code'] or '(品番未入力)'}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("キャンセル", use_container_width=True, key="unfav_cancel"):
            st.session_state.confirm_unfav = None
            st.rerun()
    with col2:
        if st.button("削除する", use_container_width=True, type="primary", key="unfav_ok"):
            card["favorite"] = False
            persist()
            st.session_state.confirm_unfav = None
            st.rerun()


@st.dialog("編集")
def edit_dialog():
    card = next((c for c in st.session_state.cards if c["id"] == st.session_state.edit_card), None)
    if card is None:
        st.session_state.edit_card = None
        st.rerun()
        return
    g = group_of(card["group"])
    st.write(f"{g['name']} ・ {card['member']}")
    new_code = st.text_input("品番", value=card["code"])
    new_qty = st.number_input("所持枚数", min_value=1, value=int(card["qty"]), step=1)
    if st.button("保存する", use_container_width=True):
        card["code"] = new_code.strip()
        card["qty"] = int(new_qty)
        persist()
        st.session_state.edit_card = None
        st.rerun()
    if st.button("キャンセル", key="edit_cancel"):
        st.session_state.edit_card = None
        st.rerun()


# ---------- ダイアログの呼び出し（同時に1つだけ開く） ----------
if st.session_state.confirm_delete is not None:
    confirm_delete_dialog()
elif st.session_state.confirm_unfav is not None:
    confirm_unfav_dialog()
elif st.session_state.edit_card is not None:
    edit_dialog()
elif st.session_state.show_add:
    add_dialog()
elif st.session_state.filter_step == "group":
    filter_group_dialog()
elif st.session_state.filter_step == "member":
    filter_member_dialog()


# =====================================================================
# カード描画の共通関数
# =====================================================================
def render_card(c, show_edit_delete=True):
    g = group_of(c["group"])
    if show_edit_delete:
        col_main, col_heart, col_edit, col_del = st.columns([6, 1, 1, 1])
    else:
        col_main, col_heart = st.columns([6, 1])
    with col_main:
        code_display = c["code"] if c["code"] else "（品番未入力）"
        st.markdown(
            f"""
            <div class="photo-card">
                <span class="photo-date">{c['date']}</span>&nbsp;&nbsp;
                <span class="photo-code">{code_display}</span>
                <span class="photo-qty">× {c['qty']}枚</span>
                <div class="photo-sub">🎨 {g['name']} ・ {c['member']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_heart:
        st.write("")
        heart = "♥" if c["favorite"] else "♡"
        if st.button(heart, key=f"heart_{c['id']}"):
            if c["favorite"]:
                st.session_state.confirm_unfav = c["id"]
            else:
                c["favorite"] = True
                persist()
            st.rerun()
    if show_edit_delete:
        with col_edit:
            st.write("")
            if st.button("✎", key=f"edit_{c['id']}"):
                st.session_state.edit_card = c["id"]
                st.rerun()
        with col_del:
            st.write("")
            if st.button("×", key=f"del_{c['id']}"):
                st.session_state.confirm_delete = c["id"]
                st.rerun()


# =====================================================================
# ページ：一覧
# =====================================================================
if st.session_state.page == "list":
    col_sort, col_add = st.columns([3, 1])
    with col_sort:
        label_to_key = {"登録日順（新しい順）": "date_new", "登録日順（古い順）": "date_old"}
        chosen_label = st.selectbox(
            "並べかえ", list(label_to_key.keys()),
            index=list(label_to_key.values()).index(st.session_state.sort_key),
        )
        st.session_state.sort_key = label_to_key[chosen_label]
    with col_add:
        st.write("")
        st.write("")
        if st.button("＋ 追加", use_container_width=True):
            close_all_dialogs()
            st.session_state.show_add = True
            st.session_state.add_step = "group"
            st.session_state.draft = {"group": None, "type": None, "member": None}
            st.rerun()

    col_fg, col_fm, col_fc = st.columns([2, 2, 1])
    with col_fg:
        g_label = "グループ"
        if st.session_state.filter_group:
            g_label += f"：{group_of(st.session_state.filter_group)['name']}"
        if st.button(g_label, key="open_fg", use_container_width=True):
            close_all_dialogs()
            st.session_state.filter_step = "group"
            st.rerun()
    with col_fm:
        m_label = "メンバー"
        if st.session_state.filter_member:
            m_label += f"：{st.session_state.filter_member}"
        if st.button(m_label, key="open_fm", use_container_width=True):
            close_all_dialogs()
            st.session_state.filter_step = "member"
            st.rerun()
    with col_fc:
        st.write("")
        if (st.session_state.filter_group or st.session_state.filter_member) and st.button("解除", key="clear_filter"):
            st.session_state.filter_group = None
            st.session_state.filter_member = None
            st.rerun()

    cards = st.session_state.cards
    if st.session_state.filter_group:
        cards = [c for c in cards if c["group"] == st.session_state.filter_group]
    if st.session_state.filter_member:
        cards = [c for c in cards if c["member"] == st.session_state.filter_member]
    cards = sorted(cards, key=lambda c: c["date"], reverse=(st.session_state.sort_key == "date_new"))

    if not cards:
        st.info("まだ写真が登録されていません")
    for c in cards:
        render_card(c)


# =====================================================================
# ページ：品番検索
# =====================================================================
elif st.session_state.page == "search":
    st.subheader("品番検索")

    g_names = ["（指定しない）"] + [g["name"] for g in GROUPS]
    chosen_g = st.selectbox("グループ", g_names)
    search_gid = None
    if chosen_g != "（指定しない）":
        search_gid = next(g["id"] for g in GROUPS if g["name"] == chosen_g)

    m_options = ["（指定しない）"]
    if search_gid:
        m_options += MEMBERS[search_gid]
    chosen_m = st.selectbox("メンバー", m_options)
    search_member = None if chosen_m == "（指定しない）" else chosen_m

    if search_gid:
        col_prefix, col_input = st.columns([1, 3])
        with col_prefix:
            st.markdown(f"**{PREFIX[search_gid]}-**")
        with col_input:
            suffix_input = st.text_input(
                "品番（残りの番号）", placeholder="0231", label_visibility="collapsed"
            )
        full_code = f"{PREFIX[search_gid]}-{suffix_input.strip()}" if suffix_input.strip() else ""
    else:
        full_code = st.text_input("品番を入力（例：ST-0231）", value=st.session_state.search_code)

    if st.button("検索する", use_container_width=True):
        st.session_state.search_code = full_code.strip()
        candidates = st.session_state.cards
        if search_gid:
            candidates = [c for c in candidates if c["group"] == search_gid]
        if search_member:
            candidates = [c for c in candidates if c["member"] == search_member]
        found = [c for c in candidates if c["code"] == st.session_state.search_code and st.session_state.search_code != ""]
        if found:
            st.session_state.search_result = "found"
            st.session_state["search_found_cards"] = found
        else:
            st.session_state.search_result = "notfound"

    st.write("")
    if st.session_state.search_result == "found":
        st.success("この品番は登録されています！")
        for c in st.session_state.get("search_found_cards", []):
            render_card(c, show_edit_delete=False)
    elif st.session_state.search_result == "notfound":
        st.warning("この品番はまだ登録されていません。")


# =====================================================================
# ページ：お気に入り
# =====================================================================
elif st.session_state.page == "favorites":
    st.subheader("お気に入り一覧")
    fav_cards = [c for c in st.session_state.cards if c["favorite"]]
    fav_cards = sorted(fav_cards, key=lambda c: c["date"], reverse=True)
    if not fav_cards:
        st.info("お気に入りに登録された写真はまだありません")
    for c in fav_cards:
        render_card(c, show_edit_delete=False)
