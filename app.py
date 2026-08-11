import streamlit as st
from model import generate_yes_no_response

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Fake News Detector - Fact Checking Chatbot",
    page_icon="🤖",
    layout="centered"
)

# --------------------------------------------------
# CUSTOM CSS STYLE
# --------------------------------------------------
st.markdown("""
<style>
    .yes-card {
        background-color: rgba(38, 166, 154, 0.1);
        border-left: 6px solid #26a69a;
        padding: 18px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .no-card {
        background-color: rgba(239, 83, 80, 0.1);
        border-left: 6px solid #ef5350;
        padding: 18px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .uncertain-card {
        background-color: rgba(255, 167, 38, 0.1);
        border-left: 6px solid #ffa726;
        padding: 18px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .card-title {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("🤖 Fake News Detector")
st.write(
    "Ask any question or submit any claim/headline. Fake News Detector will fact-check it and tell you if it is **Real** or **Fake**."
)
st.divider()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Initial assistant greeting
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I am Fake News Detector. Ask me any question or paste a headline (e.g. *'Did humans walk on the moon?'* or *'Is chocolate toxic to dogs?'*), and I will verify it."
    })

# Clear chat option
col1, col2 = st.columns([5, 1])
with col2:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hello! I am Fake News Detector. Ask me any question or paste a headline (e.g. *'Did humans walk on the moon?'* or *'Is chocolate toxic to dogs?'*), and I will verify it."
        }]
        st.rerun()

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "structured" in msg:
            ans = msg["structured"]["answer"]
            conf = msg["structured"]["confidence"]
            expl = msg["structured"]["explanation"]

            if ans == "Yes / Real News":
                st.markdown(f"""
                <div class="yes-card">
                    <div class="card-title">✅ REAL NEWS / YES</div>
                    <div><strong>Confidence:</strong> {conf}</div>
                    <div style="margin-top: 6px;">{expl}</div>
                </div>
                """, unsafe_allow_html=True)
            elif ans == "No / Fake News":
                st.markdown(f"""
                <div class="no-card">
                    <div class="card-title">❌ FAKE NEWS / NO</div>
                    <div><strong>Confidence:</strong> {conf}</div>
                    <div style="margin-top: 6px;">{expl}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="uncertain-card">
                    <div class="card-title">⚠️ UNCERTAIN</div>
                    <div><strong>Confidence:</strong> {conf}</div>
                    <div style="margin-top: 6px;">{expl}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write(msg["content"])

# Chat Input
if prompt := st.chat_input("Ask or claim something..."):
    # Append User input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing truth and credibility..."):
            response_data = generate_yes_no_response(prompt, st.session_state.messages[:-1])

            # Save assistant response
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"{response_data['answer']}: {response_data['explanation']}",
                "structured": response_data
            })

            ans = response_data["answer"]
            conf = response_data["confidence"]
            expl = response_data["explanation"]

            if ans == "Yes / Real News":
                st.markdown(f"""
                <div class="yes-card">
                    <div class="card-title">✅ REAL NEWS / YES</div>
                    <div><strong>Confidence:</strong> {conf}</div>
                    <div style="margin-top: 6px;">{expl}</div>
                </div>
                """, unsafe_allow_html=True)
            elif ans == "No / Fake News":
                st.markdown(f"""
                <div class="no-card">
                    <div class="card-title">❌ FAKE NEWS / NO</div>
                    <div><strong>Confidence:</strong> {conf}</div>
                    <div style="margin-top: 6px;">{expl}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="uncertain-card">
                    <div class="card-title">⚠️ UNCERTAIN</div>
                    <div><strong>Confidence:</strong> {conf}</div>
                    <div style="margin-top: 6px;">{expl}</div>
                </div>
                """, unsafe_allow_html=True)

# --------------------------------------------------
# FOOTER & INFO
# --------------------------------------------------
st.divider()
st.caption(
    "⚠️ This tool provides an AI-based credibility assessment and should not be considered definitive proof."
)