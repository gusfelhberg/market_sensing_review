"""
Authentication and Session Management Module
Handles user login, role management, and session caching
"""

import streamlit as st
from typing import Optional, Literal

# User roles
ADMIN = "ADMIN"
REVIEWER = "REVIEWER"

def get_admin_usernames() -> list:
    """Get list of admin usernames from secrets"""
    try:
        return st.secrets.get("admin_usernames", [])
    except:
        # Fallback if secrets not configured
        return ["admin"]

def get_passwords() -> dict:
    """Get passwords for each role from secrets"""
    try:
        return {
            ADMIN: st.secrets.get("admin_password", "admin123"),
            REVIEWER: st.secrets.get("reviewer_password", "reviewer123")
        }
    except:
        # Fallback passwords
        return {
            ADMIN: "admin123",
            REVIEWER: "reviewer123"
        }

def determine_user_role(username: str) -> str:
    """Determine if user is ADMIN or REVIEWER based on username"""
    admin_usernames = get_admin_usernames()
    return ADMIN if username in admin_usernames else REVIEWER

def validate_credentials(username: str, password: str) -> tuple[bool, Optional[str], Optional[str]]:
    """
    Validate user credentials
    Returns: (is_valid, role, error_message)
    """
    if not username or not password:
        return False, None, "Please enter both username and password"
    
    # Determine role
    role = determine_user_role(username)
    passwords = get_passwords()
    
    # Check password for role
    if password == passwords[role]:
        return True, role, None
    else:
        return False, None, "Invalid credentials"

def init_session_state():
    """Initialize session state variables for authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    
    # Check for username in query parameters for auto-login
    if not st.session_state.authenticated:
        query_params = st.query_params
        if 'user' in query_params:
            username = query_params['user']
            if username:
                # Auto-login with appropriate role
                role = determine_user_role(username)
                passwords = get_passwords()
                # Use the role-appropriate password for auto-login
                auto_login_success, _ = login(username, passwords[role])
                if auto_login_success:
                    # Clear the query parameter after successful auto-login
                    st.query_params.clear()

def login(username: str, password: str) -> tuple[bool, Optional[str]]:
    """
    Login user and set session state
    Returns: (success, error_message)
    """
    is_valid, role, error = validate_credentials(username, password)
    
    if is_valid:
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.user_role = role
        return True, None
    else:
        return False, error

def logout():
    """Logout user and clear session"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_role = None
    st.rerun()

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def get_current_user() -> Optional[str]:
    """Get current logged in username"""
    return st.session_state.get('username', None)

def get_current_role() -> Optional[str]:
    """Get current user role"""
    return st.session_state.get('user_role', None)

def is_admin() -> bool:
    """Check if current user is admin"""
    return st.session_state.get('user_role') == ADMIN

def render_login_page():
    """Render the login page"""
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background-color: #f0f2f6;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 🔐 Login")
        st.markdown("### HCM Market Intelligence Platform")
        
        # Show info about URL parameter login
        st.info("💡 **Tip:** You can auto-login by adding `?user=your.username` to the URL")
        
        st.markdown("---")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if submit:
                success, error = login(username, password)
                if success:
                    st.success(f"Welcome {username}! ({get_current_role()})")
                    st.rerun()
                else:
                    st.error(f"❌ {error}")
        
        st.markdown("---")
        st.markdown("""
        <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; margin-top: 20px;">
            <p style="margin: 0; font-size: 0.85rem; color: #856404;">
                <strong>⚠️ Important Notice</strong><br/><br/>
                This platform is an <strong>experimental prototype</strong> designed to explore innovative approaches to market intelligence analysis. 
                It serves as an ideation tool to demonstrate potential insights that can be derived from customer feedback and analyst intelligence 
                using advanced data analytics and machine learning techniques.<br/><br/>
                As a <strong>concept validation environment</strong>, this dashboard is intended to inspire discussion and refinement of analytical 
                approaches. It may not adhere to all Dayforce production standards and is subject to ongoing modifications as we collectively 
                develop and enhance our intelligence capabilities.<br/><br/>
                <em>Your feedback and suggestions are valuable in shaping future analytical solutions.</em>
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_user_info_sidebar():
    """Render user info and logout button in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 User Info")
    
    role_icon = "🔑" if is_admin() else "📝"
    role_color = "#ff6b6b" if is_admin() else "#4ecdc4"
    
    st.sidebar.markdown(f"""
    <div style="background-color: {role_color}20; padding: 10px; border-radius: 5px; border-left: 4px solid {role_color};">
        <strong>{role_icon} {get_current_user()}</strong><br/>
        <small>Role: {get_current_role()}</small>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
