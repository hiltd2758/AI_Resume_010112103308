"""Trang Home - entry point Streamlit (Role: Dũng)."""
import streamlit as st
from core.storage import init_db

st.set_page_config(page_title="CV-JD Matcher", page_icon="🧩", layout="wide")
init_db()

st.title("🧩 CV-JD Matcher")
st.write("""
Hệ thống chấm % match giữa CV và Job Description (Rule-based + AI).

**Quy trình dùng:**
1. Vào trang **Tạo Job** để thêm vị trí tuyển dụng.
2. Vào trang **Upload CV** để thêm ứng viên.
3. Vào trang **Kết quả ứng viên** để xem % match + khuyến nghị cho từng job.
""")

st.info("Dùng menu bên trái để chuyển trang.")
