import streamlit as st
import httpx
import re
from datetime import date, datetime, timedelta

# -------------------- Streamlit Page Setup --------------------
st.set_page_config(
    page_title="🏫 School Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------- Enhanced Styling --------------------
st.markdown(
    """
    <style>
    /* Main app background and text */
    .stApp {
        background: linear-gradient(135deg, #0B0C10 0%, #1F2833 100%);
        color: #FFFFFF;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(90deg, #45A29E 0%, #66FCF1 100%);
        color: #0B0C10;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(102, 252, 241, 0.2);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 252, 241, 0.4);
    }
    
    /* Chat container */
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 15px;
        margin: 20px 0;
        border-radius: 15px;
        background: rgba(31, 40, 51, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Chat messages */
    .chat-message {
        border-radius: 15px;
        padding: 12px 16px;
        margin-bottom: 10px;
        max-width: 80%;
        word-wrap: break-word;
        animation: slideIn 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .user-message {
        background: linear-gradient(135deg, #45A29E 0%, #66FCF1 100%);
        color: #0B0C10;
        margin-left: auto;
        text-align: right;
        font-weight: 500;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #1F2833 0%, #2A3642 100%);
        color: #FFFFFF;
        margin-right: auto;
        border-left: 4px solid #66FCF1;
    }
    
    /* Text input */
    .stTextInput>div>div>input {
        background-color: #1F2833;
        color: #FFFFFF;
        border-radius: 12px;
        padding: 12px;
        border: 2px solid #45A29E;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #66FCF1;
        box-shadow: 0 0 15px rgba(102, 252, 241, 0.3);
    }
    
    /* Title styling */
    h1 {
        color: #66FCF1;
        text-shadow: 0 0 20px rgba(102, 252, 241, 0.5);
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, rgba(69, 162, 158, 0.1) 0%, rgba(102, 252, 241, 0.1) 100%);
        border-left: 4px solid #66FCF1;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0B0C10;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #45A29E;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #66FCF1;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #66FCF1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🏫 School Assistant Chatbot")
st.markdown(
    """
    <div class="info-box">
    <strong>Welcome!</strong> 👋<br><br>
    I can help you with:<br>
    • 📅 <strong>Report absences</strong> - "I will be absent tomorrow"<br>
    • 🍕 <strong>Check lunch menu</strong> - "Show me the lunch menu"<br>
    • 📚 <strong>Homework & Schedule</strong> - Coming Soon!<br>
    • 💬 <strong>General questions</strong> - Coming Soon!
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------- API Configuration --------------------
API_BASE_URL = "http://127.0.0.1:8000"

# -------------------- Session State --------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! 👋 I'm your School Assistant. How can I help you today?"}
    ]

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

if "waiting_for_reason" not in st.session_state:
    st.session_state.waiting_for_reason = False

if "absence_date" not in st.session_state:
    st.session_state.absence_date = None

# -------------------- Helper Functions --------------------
def parse_absence_date(text: str) -> date:
    """Parse date from natural language text."""
    text_lower = text.lower()
    
    # Check for relative dates
    if "tomorrow" in text_lower:
        return date.today() + timedelta(days=1)
    elif "today" in text_lower:
        return date.today()
    elif "next monday" in text_lower:
        days_ahead = 0 - date.today().weekday() + 7
        return date.today() + timedelta(days=days_ahead)
    
    # Check for explicit date (YYYY-MM-DD format)
    match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d").date()
        except ValueError:
            pass
    
    # Default to today
    return date.today()


def report_absence(absence_date: date, reason: str) -> str:
    """Report absence via API with the provided date and reason."""
    try:
        response = httpx.post(
            f"{API_BASE_URL}/tools/report_absence",
            json={"date": str(absence_date), "reason": reason},
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("message", f"✅ Absence reported for {absence_date}")
        else:
            return f"❌ Server returned error: {response.status_code}"
        
    except httpx.ConnectError:
        return "❌ Cannot connect to server. Please make sure `python mcp_server.py` is running!"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def start_absence_report(text: str) -> str:
    """Start the absence reporting process by asking for reason."""
    absence_date = parse_absence_date(text)
    st.session_state.absence_date = absence_date
    st.session_state.waiting_for_reason = True
    
    date_str = absence_date.strftime('%B %d, %Y')
    return f"📅 I'll help you report an absence for **{date_str}**.\n\nPlease tell me the reason for your absence:"


def get_lunch_menu() -> str:
    """Get today's lunch menu from API."""
    try:
        response = httpx.get(
            f"{API_BASE_URL}/tools/get_lunch_menu",
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("menu", "🍽️ Today's lunch menu")
        else:
            return f"❌ Server returned error: {response.status_code}"
        
    except httpx.ConnectError:
        return "❌ Cannot connect to server. Please make sure `python mcp_server.py` is running!"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def process_user_input(user_input: str) -> str:
    """Process user input and route to appropriate handler."""
    user_input_lower = user_input.lower()
    
    try:
        # If waiting for absence reason, process it
        if st.session_state.waiting_for_reason:
            reason = user_input.strip()
            absence_date = st.session_state.absence_date
            
            # Reset state
            st.session_state.waiting_for_reason = False
            st.session_state.absence_date = None
            
            # Report the absence with the provided reason
            return report_absence(absence_date, reason)
        
        # Check for lunch menu request
        if any(word in user_input_lower for word in ["lunch", "menu", "food", "eat"]):
            return get_lunch_menu()
        
        # Check for absence report - start the conversation flow
        elif any(word in user_input_lower for word in ["absent", "absence", "miss school", "won't be there"]):
            return start_absence_report(user_input)
        
        # Check for homework or general questions
        elif any(word in user_input_lower for word in ["homework", "schedule", "class"]):
            return "📚 **Coming Soon!** The homework and schedule features are currently under development. Stay tuned!"
        
        # General questions - coming soon
        else:
            return "💬 **Coming Soon!** General chat functionality is currently under development. For now, I can help you report absences or check the lunch menu!"
            
    except Exception as e:
        # Reset state on error
        st.session_state.waiting_for_reason = False
        st.session_state.absence_date = None
        return f"❌ Oops! Something went wrong: {str(e)}"


# -------------------- Display Chat --------------------
def display_chat():
    """Display all messages in the chat."""
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        role_class = "user-message" if msg["role"] == "user" else "assistant-message"
        content = msg["content"].replace("\n", "<br>")
        st.markdown(
            f'<div class="chat-message {role_class}">{content}</div>',
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)


# Display the chat history
display_chat()

# -------------------- Chat Input --------------------
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Type your message here...",
            placeholder="Ask me anything...",
            label_visibility="collapsed",
            disabled=st.session_state.is_processing
        )
    
    with col2:
        submitted = st.form_submit_button(
            "Send",
            use_container_width=True,
            disabled=st.session_state.is_processing
        )

# Process the input
if submitted and user_input and not st.session_state.is_processing:
    st.session_state.is_processing = True
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Show processing indicator
    with st.spinner("Thinking... 🤔"):
        bot_reply = process_user_input(user_input)
    
    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    
    st.session_state.is_processing = False
    st.rerun()

# -------------------- Sidebar with Quick Actions --------------------
with st.sidebar:
    st.header("⚡ Quick Actions")
    
    if st.button("📅 Report Absence", use_container_width=True):
        st.session_state.messages.append(
            {"role": "user", "content": "I will be absent tomorrow"}
        )
        bot_reply = start_absence_report("I will be absent tomorrow")
        st.session_state.messages.append(
            {"role": "assistant", "content": bot_reply}
        )
        st.rerun()
    
    if st.button("🍕 View Lunch Menu", use_container_width=True):
        st.session_state.messages.append(
            {"role": "user", "content": "Show me the lunch menu"}
        )
        bot_reply = get_lunch_menu()
        st.session_state.messages.append(
            {"role": "assistant", "content": bot_reply}
        )
        st.rerun()
    
    st.divider()
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat cleared! How can I help you?"}
        ]
        st.session_state.waiting_for_reason = False
        st.session_state.absence_date = None
        st.rerun()
    
    st.divider()
    st.caption("💡 **Tip**: Type naturally and I'll understand what you need!")