import streamlit as st
import os
from datetime import datetime
from PIL import Image, ImageOps
import google.generativeai as genai
import pandas as pd

st.title("🎬 VIDEO STUDIO")
# Gemini API



GEMINI_KEY = os.environ.get("GOOGLE_API_KEY")

genai.configure(api_key=GEMINI_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

# =========================
# Ý TƯỞNG VIDEO
# =========================

idea = st.text_area(
    "Ý tưởng video",
    placeholder="Ví dụ: Một người đàn ông Việt Nam 70 tuổi uống trà trên đồi Đà Lạt lúc bình minh..."
)

# =========================
# ẢNH THAM CHIẾU
# =========================

st.subheader("🖼️ Ảnh tham chiếu")

reference_image = st.file_uploader(
    "Tải ảnh tham chiếu lên",
    type=["png", "jpg", "jpeg", "webp"],
    key="veo3_reference_image"
)

ref_note = ""

if reference_image is not None:
    image = Image.open(reference_image)
    image = ImageOps.exif_transpose(image)

    st.image(
        image,
        caption="Ảnh tham chiếu đã tải lên",
        use_container_width=True
    )

    os.makedirs("data/reference_images", exist_ok=True)

    file_ext = reference_image.name.split(".")[-1].lower()
    save_name = f"ref_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
    save_path = os.path.join("data/reference_images", save_name)

    image.save(save_path)

    st.success(f"✅ Đã lưu ảnh tham chiếu: {save_path}")

    st.session_state["last_reference_image"] = save_path

    ref_note = f"""
Use the uploaded reference image as the main character reference.
Keep the face, age, expression, hairstyle, and overall identity consistent with the reference image.
Reference image path: {save_path}
"""

# =========================
# TẠO PROMPT VEO 3
# =========================

if st.button("🚀 Tạo lời nhắc Veo 3"):

    ai_prompt = f"""
You are an expert Veo 3 Director.

Create an ultra cinematic Veo 3 video prompt.

MAIN IDEA:
{idea}

REFERENCE:
{ref_note}

Requirements:

- Maintain character consistency from reference image
- Professional filmmaking
- Ultra realistic
- Emotional storytelling
- Natural facial expression
- Accurate lip sync
- Cinematic camera movement
- Dynamic lighting
- Shallow depth of field
- Premium color grading
- 4K quality
- High detail
- Veo 3 optimized

Output only the final Veo 3 prompt.
"""

    with st.spinner("🤖 Gemini đang tạo Prompt..."):

        response = model.generate_content(ai_prompt)

        final_prompt = response.text

        history_file = "data/prompt_history.csv"

        new_row = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "idea": idea,
            "prompt": final_prompt
        }

        if os.path.exists(history_file):
            df = pd.read_csv(history_file)
            df = pd.concat(
                [df, pd.DataFrame([new_row])],
                ignore_index=True
            )
        else:
            df = pd.DataFrame([new_row])

        df.to_csv(
            history_file,
            index=False,
            encoding="utf-8-sig"
        )

        st.subheader("🎯 Prompt Veo 3 AI")

        st.code(final_prompt)

        st.download_button(
            "📋 Tải Prompt AI",
            final_prompt,
            file_name="veo3_ai_prompt.txt"
        )
        st.divider()

st.subheader("📚 Lịch sử Prompt")

history_file = "data/prompt_history.csv"

if os.path.exists(history_file):

    try:
        history_df = pd.read_csv(history_file)

        st.dataframe(
            history_df.tail(20),
            use_container_width=True
        )

    except:
        pass