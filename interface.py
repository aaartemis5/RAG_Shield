import streamlit as st

# --- Custom CSS Styling ---
st.markdown(
    """
    <style>
    /* Main chat section background */
    .stApp {
        background: rgb(5,4,7);
        background: linear-gradient(90deg, rgba(5,4,7,1) 0%, rgba(39,29,61,1) 47%, rgba(44,29,88,1) 100%);
    }
    
    /* Sidebar styling with a darker gradient */
    [data-testid="stSidebar"] {
        background: rgb(5,4,7);
        background: linear-gradient(90deg, rgba(5,4,7,1) 0%, rgba(17,7,37,1) 47%, rgba(44,29,88,1) 100%);
    }
    
    /* Navigation bar styling with a darker gradient */
    [data-testid="stHeader"] {
        background: rgb(5,4,7);
        background: linear-gradient(90deg, rgba(5,4,7,1) 0%, rgba(17,7,37,1) 47%, rgba(44,29,88,1) 100%);
    }
    
    /* Title styling: Main title (ShieldAI) */
    .shield-title {
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 0;
    }
    
    /* Subtitle/tagline styling: smaller and on the next line */
    .shield-subtitle {
        font-size: 1.5em;
        font-weight: normal;
        margin-top: 0;
    }

    /* Container for chat messages */
    .chat-container {
        position:fixed;
        margin-bottom: 150px;
    }

    /* Fixed query box at bottom */
    .fixed-form {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #ffffff;
        padding: 10px 20px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Title Section ---
st.markdown('<div class="shield-title">ShieldAI</div>', unsafe_allow_html=True)
st.markdown('<div class="shield-subtitle">Stay Ahead of Threats with AI Precision</div>', unsafe_allow_html=True)

# --- Session State Initialization ---
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "chat_id_counter" not in st.session_state:
    st.session_state.chat_id_counter = 1
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

def generate_response(user_message):
    # Replace this placeholder with your actual RAG logic.
    return "This is a sample response from your RAG system."

# --- Sidebar: Chat Sessions ---
st.sidebar.title("Chat Sessions")

# "New Chat" button: Save current chat (if any) and reset the conversation.
if st.sidebar.button("New Chat"):
    if st.session_state.current_chat:  # Save current chat if it isn't empty.
        chat_id = f"Chat {st.session_state.chat_id_counter}"
        st.session_state.chat_history[chat_id] = st.session_state.current_chat.copy()
        st.session_state.chat_id_counter += 1
    st.session_state.current_chat = []

# Dropdown to select a previous chat session.
chat_options = list(st.session_state.chat_history.keys())
selected_chat = st.sidebar.selectbox("Select Previous Chat", ["None"] + chat_options)
if selected_chat != "None":
    # Load the selected chat session into the current chat.
    st.session_state.current_chat = st.session_state.chat_history[selected_chat]

# --- Main Chat Interface ---
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.current_chat:
        col1, col2 = st.columns([1, 1])
        if message["role"] == "user":
            with col1:
                st.markdown(
                    f"""
                    <div style="background-color:#DCF8C6; color:black; padding:10px; border-radius:10px; margin:5px;">
                        <strong>User:</strong> {message['content']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col2:
                st.empty()
        else:
            with col1:
                st.empty()
            with col2:
                st.markdown(
                    f"""
                    <div style="background-color:#F1F0F0; color:black; padding:10px; border-radius:10px; margin:5px;">
                        <strong>Assistant:</strong> {message['content']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    st.markdown('</div>', unsafe_allow_html=True)

# --- Fixed Query Box at the Bottom ---
st.markdown('<div class="fixed-form">', unsafe_allow_html=True)

# Store user input persistently before form submission
st.session_state.user_input = st.text_input("Type your message here...", value=st.session_state.user_input)

with st.form("chat_form", clear_on_submit=True):
    submitted = st.form_submit_button("Send")
    if submitted and st.session_state.user_input:
        # Append user message to the current chat
        st.session_state.current_chat.append({"role": "user", "content": st.session_state.user_input})
        # Generate and append the RAG response
        response = generate_response(st.session_state.user_input)
        st.session_state.current_chat.append({"role": "assistant", "content": response})
        # Clear stored input after processing
        st.session_state.user_input = ""

st.markdown('</div>', unsafe_allow_html=True)