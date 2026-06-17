import streamlit as st
import pandas as pd
import os
import shutil
from datetime import datetime

MEMORY_FILE = "data/memory.csv"
BACKUP_FILE = "data/memory_backup.csv"

os.makedirs("data", exist_ok=True)

if not os.path.exists(MEMORY_FILE):
    pd.DataFrame(columns=["time", "title", "content"]).to_csv(MEMORY_FILE, index=False)


def load_memory():
    try:
        return pd.read_csv(MEMORY_FILE).fillna("")
    except Exception:
        df = pd.DataFrame(columns=["time", "title", "content"])
        df.to_csv(MEMORY_FILE, index=False)
        return df


def backup_memory():
    try:
        shutil.copy(MEMORY_FILE, BACKUP_FILE)
    except Exception:
        pass


def save_df(df):
    df.to_csv(MEMORY_FILE, index=False)
    backup_memory()


memory_df = load_memory()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def is_question(text):
    t = text.lower().strip()
    question_words = [
        "?", "gì", "bao nhiêu", "ở đâu", "không", "chưa",
        "phải không", "là ai", "tên gì", "tên là gì",
        "ai vậy", "khi nào", "thế nào"
    ]
    return any(w in t for w in question_words)


def auto_memory(text):
    text_clean = text.strip()
    text_lower = text_clean.lower()

    if text_clean == "":
        return None, None

    if is_question(text_clean):
        return None, None

    if " bạn " in text_lower:
        return None, None

    if text_lower.startswith("đã nhớ"):
        return None, None

    if " tên " in f" {text_lower} ":
        idx = text_lower.find(" tên ")

        relation = text_clean[:idx].strip()
        name = text_clean[idx + 5:].strip(" .:")

        relation = (
            relation
            .replace(" của tôi", "")
            .replace(" tôi", "")
            .replace("Tôi", "")
            .replace("Của tôi", "")
            .strip()
        )

        if relation and relation.lower() not in ["tôi", "tên tôi", "tên tôi là"]:
            return relation.title(), name

    if "tôi tên" in text_lower:
        return "Tên", text_clean.replace("Tôi tên", "").replace("tôi tên", "").strip(" .:")

    if "tên tôi là" in text_lower:
        return "Tên", text_clean.replace("Tên tôi là", "").replace("tên tôi là", "").strip(" .:")

    if "tôi sinh năm" in text_lower:
        return "Năm sinh", text_clean.replace("Tôi sinh năm", "").replace("tôi sinh năm", "").strip(" .:")

    if "tôi ở" in text_lower:
        return "Nơi ở", text_clean.replace("Tôi ở", "").replace("tôi ở", "").strip(" .:")

    if "tôi đang làm" in text_lower:
        return "Công việc", text_clean.replace("Tôi đang làm", "").replace("tôi đang làm", "").strip(" .:")

    if "tôi làm" in text_lower:
        return "Công việc", text_clean.replace("Tôi làm", "").replace("tôi làm", "").strip(" .:")

    if "tôi thích" in text_lower:
        return "Sở thích", text_clean.replace("Tôi thích", "").replace("tôi thích", "").strip(" .:")

    if "tôi muốn" in text_lower:
        return "Kế hoạch", text_clean.replace("Tôi muốn", "").replace("tôi muốn", "").strip(" .:")

    if "dự án" in text_lower:
        return "Dự án", text_clean

    return None, None

def smart_memory_search(question):
    q = question.lower().strip()

    relation_map = {
        "vợ": ["vợ", "bà xã", "người yêu"],
        "con trai": ["con trai", "con trai tôi"],
        "con gái": ["con gái", "con gái tôi"],
        "mẹ": ["mẹ", "má"],
        "bố": ["bố", "ba", "cha"],
        "ông nội": ["ông nội"],
        "cháu nội": ["cháu nội"],
        "tên": ["tên tôi", "tôi tên", "tôi là ai"],
        "năm sinh": ["sinh năm", "năm sinh", "bao nhiêu tuổi"],
        "nơi ở": ["ở đâu", "nơi ở", "địa chỉ"],
        "công việc": ["làm gì", "nghề gì", "công việc"],
        "sở thích": ["thích gì", "sở thích"],
        "kế hoạch": ["kế hoạch", "mục tiêu", "muốn gì"],
    }

    for title, keywords in relation_map.items():
        if any(k in q for k in keywords):
            rows = memory_df[
                memory_df["title"].astype(str).str.lower().str.contains(title, na=False)
            ]

            if not rows.empty:
                value = rows.iloc[-1]["content"]
                return f"{rows.iloc[-1]['title']} của bạn là {value}."

    if "nhớ gì" in q or "biết gì" in q or "thông tin gì" in q:
        if memory_df.empty:
            return "Tôi chưa có ký ức nào."

        text = ""
        for _, row in memory_df.iterrows():
            text += f"• {row['title']}: {row['content']}\n"

        return text
    # LEVEL 70.3 - HIỂU QUAN HỆ NGƯỢC
    # Ví dụ: Hạnh là ai? Nam là ai? Ngọc là ai?
    if "là ai" in q or "la ai" in q:
        name_query = (
            q.replace("là ai", "")
            .replace("la ai", "")
            .replace("?", "")
            .strip()
        )

        if name_query:
            for _, row in memory_df.iterrows():
                title = str(row["title"]).strip()
                content = str(row["content"]).strip()

                if name_query.lower() == content.lower():
                    return f"{content} là {title} của bạn."
    return None
def add_memory(title, content):
    global memory_df

    if title is None or content is None or str(content).strip() == "":
        return False

    title = str(title).strip()
    content = str(content).strip(" .:")

    same = memory_df[
        (memory_df["title"].astype(str).str.strip().str.lower() == title.lower()) &
        (memory_df["content"].astype(str).str.strip().str.lower() == content.lower())
    ]

    if not same.empty:
        return False

    new_row = pd.DataFrame([{
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": title,
        "content": content
    }])

    memory_df = pd.concat([memory_df, new_row], ignore_index=True)
    save_df(memory_df)
    return True


def get_latest_memory(title):
    rows = memory_df[
        memory_df["title"].astype(str).str.strip().str.lower()
        ==
        str(title).strip().lower()
    ]

    if not rows.empty:
        return str(rows.iloc[-1]["content"]).strip(" .:")

    return None


def get_all_memories():
    if memory_df.empty:
        return "Tôi chưa có ký ức nào."

    result = []
    for _, row in memory_df.iterrows():
        result.append(f"• {row['title']}: {row['content']}")

    return "\n\n".join(result)


def update_memory(title, new_content):
    global memory_df

    title = str(title).strip()
    new_content = str(new_content).strip(" .:")

    mask = memory_df["title"].astype(str).str.strip().str.lower() == title.lower()

    if mask.any():
        memory_df.loc[mask, "content"] = new_content
    else:
        add_memory(title, new_content)

    save_df(memory_df)


def delete_memory(title):
    global memory_df

    title = str(title).strip()

    memory_df = memory_df[
        memory_df["title"].astype(str).str.strip().str.lower()
        != title.lower()
    ]

    memory_df = memory_df.reset_index(drop=True)
    save_df(memory_df)
    return True


def smart_delete_memory(keyword):
    global memory_df

    keyword = str(keyword).strip().lower()

    if keyword == "":
        return 0

    before_count = len(memory_df)

    memory_df = memory_df[
        ~(
            memory_df["title"].astype(str).str.lower().str.contains(keyword, na=False)
            |
            memory_df["content"].astype(str).str.lower().str.contains(keyword, na=False)
        )
    ]

    memory_df = memory_df.reset_index(drop=True)
    save_df(memory_df)

    return before_count - len(memory_df)


def clean_trash_memory():
    global memory_df

    before_count = len(memory_df)

    trash_keywords = [
        "đổ la",
        "ký tại rác",
        "xem bộ nhớ",
        "không có dữ liệu này",
        "tôi chưa biết",
        "khác",
        "tên ông",
        "ông nội bạn",
        "bố bạn",
        "mẹ bạn",
        "nội thất",
        "khúc nội"
    ]

    mask_trash = memory_df["title"].astype(str).str.lower().apply(
        lambda x: any(k in x for k in trash_keywords)
    ) | memory_df["content"].astype(str).str.lower().apply(
        lambda x: any(k in x for k in trash_keywords)
    )

    memory_df = memory_df[~mask_trash]

    memory_df = memory_df.drop_duplicates(
        subset=["title", "content"],
        keep="last"
    ).reset_index(drop=True)

    save_df(memory_df)

    deleted_count = before_count - len(memory_df)
    return deleted_count
def format_memory_pretty():
    if memory_df.empty:
        return "Tôi chưa có ký ức nào."

    lines = []

    groups = {
        "👤 Thông tin cá nhân": [
            "Tên", "Năm sinh", "Nơi ở", "Công việc", "Sở thích", "Kế hoạch"
        ],
        "👨‍👩‍👧 Gia đình": [
            "Vợ", "Con trai", "Con gái", "Mẹ", "Bố", "Ông Nội", "Cháu Nội"
        ],
    }

    used_titles = []

    for group_name, titles in groups.items():
        lines.append(f"### {group_name}")

        found = False

        for title in titles:
            value = get_latest_memory(title)
            if value:
                lines.append(f"- **{title}:** {value}")
                used_titles.append(title.lower())
                found = True

        if not found:
            lines.append("- Chưa có dữ liệu.")

        lines.append("")

    lines.append("### 🤝 Quan hệ khác")

    found_other = False

    for _, row in memory_df.iterrows():
        title = str(row["title"]).strip()
        content = str(row["content"]).strip()

        if title.lower() not in used_titles:
            lines.append(f"- **{title}:** {content}")
            found_other = True

    if not found_other:
        lines.append("- Chưa có dữ liệu.")

    return "\n".join(lines)


def natural_update_memory(text):
    text_clean = text.strip()
    text_lower = text_clean.lower()

    update_rules = {
        "đổi tên vợ thành": "Vợ",
        "đổi tên con trai thành": "Con trai",
        "đổi tên con gái thành": "Con gái",
        "đổi tên mẹ thành": "Mẹ",
        "đổi tên bố thành": "Bố",
        "đổi tên ông nội thành": "Ông Nội",
        "đổi tên cháu nội thành": "Cháu Nội",
        "đổi tên cô giáo thành": "Cô Giáo",
        "đổi nơi ở thành": "Nơi ở",
        "đổi sở thích thành": "Sở thích",
        "đổi kế hoạch thành": "Kế hoạch",
        "đổi công việc thành": "Công việc",
    }

    for key, title in update_rules.items():
        if key in text_lower:
            new_value = text_clean.split("thành")[-1].strip(" .:")
            update_memory(title, new_value)
            return f"Đã đổi {title} thành {new_value}."

    if "đổi tên" in text_lower and "thành" in text_lower:
        left = text_lower.split("đổi tên")[1]
        relation = left.split("thành")[0].strip()
        new_name = text_clean.split("thành")[-1].strip(" .:")

        if relation and new_name:
            update_memory(relation.title(), new_name)
            return f"Đã đổi {relation.title()} thành {new_name}."

    if text_lower.startswith("xóa "):
        keyword = text_clean[4:].strip(" .:")

        if keyword:
            deleted_count = smart_delete_memory(keyword)

            if deleted_count > 0:
                return f"Đã xóa {deleted_count} ký ức liên quan đến {keyword}."
            else:
                return f"Không tìm thấy ký ức liên quan đến {keyword}."

    if "dọn bộ nhớ" in text_lower or "dọn ký ức" in text_lower or "xóa rác" in text_lower:
        deleted_count = clean_trash_memory()
        return f"Đã dọn {deleted_count} ký ức rác."

    return None


st.title("🧠 Hệ điều hành AI MASTER — CẤP 70.1")
st.caption("Trí nhớ cá nhân + quan hệ động + sửa/xóa/dọn bộ nhớ thông minh")

st.metric("📚 Tổng ký ức", len(memory_df))

st.divider()

st.header("🧠 THÊM KÝ ỨC")

memory_title = st.text_input("Tiêu đề")
memory_content = st.text_area("Nội dung cần lưu")

if st.button("💾 Lưu ký ức"):
    if memory_content.strip() == "":
        st.warning("Sếp chưa nhập nội dung.")
    else:
        title = memory_title.strip() or "Khác"
        add_memory(title, memory_content.strip())
        st.success("Đã lưu ký ức.")
        st.rerun()

st.divider()

st.header("🧹 QUẢN LÝ BỘ NHỚ THÔNG MINH")

col_clean1, col_clean2 = st.columns(2)

with col_clean1:
    if st.button("🧹 Dọn ký ức rác", key="btn_clean_memory_center"):
        deleted = clean_trash_memory()
        st.success(f"Đã dọn {deleted} ký ức rác.")

with col_clean2:

    delete_keyword = st.text_input(
        "Nhập từ muốn xóa",
        key="delete_memory_keyword_center"
    )

    if st.button(
        "🗑️ Xóa theo từ khóa",
        key="btn_delete_memory_center"
    ):

        if delete_keyword.strip() == "":
            st.warning("Chưa nhập từ khóa.")
        else:
            deleted = smart_delete_memory(delete_keyword)
            st.success(
                f"Đã xóa {deleted} ký ức liên quan."
            )

st.divider()
# ====================================
# LEVEL 70.1 - SAO LƯU / KHÔI PHỤC / XUẤT EXCEL
# ====================================

st.header("💾 SAO LƯU & XUẤT BỘ NHỚ")

col_backup1, col_backup2, col_backup3 = st.columns(3)

with col_backup1:
    if st.button("💾 Sao lưu CSV", key="btn_backup_csv"):
        memory_df.to_csv(BACKUP_FILE, index=False)
        st.success("Đã sao lưu bộ nhớ vào memory_backup.csv")

with col_backup2:
    if st.button("♻️ Khôi phục Backup", key="btn_restore_backup"):
        if os.path.exists(BACKUP_FILE):
            memory_df = pd.read_csv(BACKUP_FILE).fillna("")
            save_df(memory_df)
            st.success("Đã khôi phục bộ nhớ từ backup.")
        else:
            st.warning("Chưa có file backup để khôi phục.")

with col_backup3:
    if st.button("📥 Xuất Excel", key="btn_export_excel"):
        excel_file = "data/memory_export.xlsx"
        memory_df.to_excel(excel_file, index=False)
        st.success("Đã xuất bộ nhớ ra Excel.")

        with open(excel_file, "rb") as f:
            st.download_button(
                label="⬇️ Tải memory_export.xlsx",
                data=f,
                file_name="memory_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_memory_excel"
            )

st.header("👁️ AI ĐANG NHỚ GÌ")

with st.expander("📋 Mở / đóng danh sách ký ức", expanded=False):

    if memory_df.empty:
        st.info("Chưa có ký ức nào.")
    else:
        for idx, row in memory_df.iterrows():
            st.markdown(f"### • {row['title']}: {row['content']}")

            col1, col2 = st.columns([8, 1])

            with col1:
                with st.expander("✏️ Sửa ký ức"):
                    new_title = st.text_input(
                        "Tiêu đề",
                        value=str(row["title"]),
                        key=f"edit_title_{idx}"
                    )

                    new_content = st.text_area(
                        "Nội dung",
                        value=str(row["content"]),
                        key=f"edit_content_{idx}"
                    )

                    if st.button("💾 Lưu sửa", key=f"save_edit_{idx}"):
                        memory_df.loc[idx, "title"] = new_title.strip()
                        memory_df.loc[idx, "content"] = new_content.strip(" .:")
                        save_df(memory_df)
                        st.success("Đã sửa ký ức.")
                        st.rerun()

            with col2:
                if st.button("❌", key=f"delete_memory_{idx}"):
                    memory_df = memory_df.drop(idx).reset_index(drop=True)
                    save_df(memory_df)
                    st.success("Đã xóa ký ức.")
                    st.rerun()

st.header("🔎 TÌM KIẾM KÝ ỨC")

keyword = st.text_input("Nhập từ khóa cần tìm trong bộ nhớ")

if keyword.strip() != "":
    result = memory_df[
        memory_df["content"].astype(str).str.contains(keyword, case=False, na=False)
        |
        memory_df["title"].astype(str).str.contains(keyword, case=False, na=False)
    ]

    if not result.empty:
        st.success("Đã tìm thấy ký ức:")
        for _, row in result.iterrows():
            st.write(f"• {row['title']}: {row['content']}")
    else:
        st.warning("Không tìm thấy ký ức nào.")

st.divider()

st.header("🤖 CHAT AI CÓ TRÍ NHỚ")

question = st.text_input("Nhập câu hỏi")

if st.button("🚀 Gửi câu hỏi"):
    question_lower = question.lower().strip()
smart_answer = smart_memory_search(question)

if smart_answer:

    st.session_state.chat_history.append({
        "question": question,
        "answer": smart_answer
    })

    st.success(smart_answer)
    update_result = natural_update_memory(question)

    if update_result:
        st.session_state.chat_history.append({
            "question": question,
            "answer": update_result
        })
        st.success("AI đã cập nhật ký ức.")
        
   

    

    auto_title, auto_content = auto_memory(question)
    saved_auto = add_memory(auto_title, auto_content)

    answer = "Tôi chưa có dữ liệu này trong bộ nhớ."

    if auto_title == "Tên":
        answer = f"Tên của bạn là {auto_content}."

    elif auto_title == "Năm sinh":
        answer = f"Bạn sinh năm {auto_content}."

    elif auto_title == "Nơi ở":
        answer = f"Bạn ở {auto_content}."

    elif auto_title == "Công việc":
        answer = f"Công việc của bạn là {auto_content}."

    elif auto_title == "Sở thích":
        answer = f"Bạn thích {auto_content}."

    elif auto_title == "Kế hoạch":
        answer = f"Kế hoạch của bạn là {auto_content}."

    elif auto_title == "Dự án":
        answer = f"Đã nhớ dự án {auto_content}."

    elif auto_title is not None and auto_content is not None:
        answer = f"Đã nhớ {auto_title} tên {auto_content}."

        if value:
            answer = f"Dự án hiện có: {value}."

    st.session_state.chat_history.append({
        "question": question,
        "answer": answer
    })

    st.success("AI đã trả lời.")

    if saved_auto:
        st.info("🧠 AI đã tự động ghi lại thông tin mới.")

st.subheader("📜 Lịch sử hội thoại")

for item in reversed(st.session_state.chat_history):
    st.info(f"👤 {item['question']}")
    st.success(f"🤖 {item['answer']}")
    # ====================================
# LEVEL 70.1 - TRUNG TÂM QUẢN LÝ KÝ ỨC
# ====================================

st.divider()

st.subheader("🧠 Trung tâm quản lý ký ức")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📋 Xem bộ nhớ", key="btn_view_memory_center"):
        st.session_state.show_memory = not st.session_state.get("show_memory", False)
    st.rerun()

with col2:
    
    if st.button("🧹 Dọn ký ức rác", key="btn_clean_memory_center"):
        deleted = clean_trash_memory()
        st.success(f"Đã dọn {deleted} ký ức rác")
        st.rerun()

with col3:
    if st.button("💾 Backup", key="btn_backup_memory_center"):
        memory_df.to_csv("memory_backup.csv", index=False)
        st.success("Đã tạo file memory_backup.csv")
        st.rerun()

with col3:
    
    if st.button("💾 Backup", key="btn_backup_memory_center"):
        memory_df.to_csv("memory_backup.csv", index=False)
        st.success("Đã tạo file memory_backup.csv")
        st.rerun()

if st.session_state.get("show_memory", False):

    st.markdown("### 📋 Toàn bộ ký ức")

    st.dataframe(
        memory_df,
        use_container_width=True
    )

st.markdown("### 🔍 Tìm kiếm ký ức")

search_text = st.text_input(
    "Nhập từ khóa",
    key="memory_search"
)

if search_text:

    result_df = memory_df[
        memory_df["title"].astype(str).str.contains(search_text, case=False, na=False)
        |
        memory_df["content"].astype(str).str.contains(search_text, case=False, na=False)
    ]

    st.dataframe(
        result_df,
        use_container_width=True
    )

st.markdown("### 🗑️ Xóa ký ức")

delete_keyword = st.text_input(
    "Từ khóa cần xóa",
    key="delete_memory_keyword"
)

if st.button("🗑️ Xóa ngay", key="btn_delete_memory_center"):

    if delete_keyword:

        deleted = smart_delete_memory(delete_keyword)

        st.success(
            f"Đã xóa {deleted} ký ức"
        )

        st.rerun()