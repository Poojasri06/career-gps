import streamlit as st

st.set_page_config(
    page_title="Career GPS - Debug",
    page_icon="🎯",
    layout="wide"
)

st.title("🚀 Career GPS Debug Mode")
st.success("✅ Streamlit is working!")
st.write("If you can see this, the app is loading correctly.")

st.write("### Testing CSS Background")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0a1929 0%, #1a237e 50%, #0d47a1 100%) !important;
    }
    
    .main .block-container {
        position: relative;
        z-index: 10;
    }
    
    h1, h2, h3, p, div, span {
        color: #e3f2fd !important;
    }
    </style>
""", unsafe_allow_html=True)

st.write("### Basic UI Test")
name = st.text_input("Enter your name:")
if name:
    st.success(f"Hello, {name}! 👋")

st.write("If you see this text in white/light blue on a dark blue background, the CSS is working.")
st.info("The original app.py has indentation errors. Please restore from backup or fix the syntax errors.")
