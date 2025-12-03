"""
Feedback System Module
Handles feedback submission, storage, and retrieval
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
from typing import Optional
import auth

# Feedback storage file
FEEDBACK_FILE = "data/feedback.csv"

def init_feedback_storage():
    """Initialize feedback CSV file if it doesn't exist"""
    if not os.path.exists(FEEDBACK_FILE):
        # Create empty DataFrame with schema
        df = pd.DataFrame(columns=[
            'timestamp',
            'username',
            'user_role',
            'section',
            'feedback_text',
            'page',
            'tab',
            'subtab'
        ])
        os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
        df.to_csv(FEEDBACK_FILE, index=False)

def save_feedback(section: str, feedback_text: str, page: str, tab: str = "", subtab: str = ""):
    """
    Save feedback to CSV file
    
    Args:
        section: Full section path (e.g., "Customer Voice > Sub-Dimension Overview")
        feedback_text: User's feedback text
        page: Main page/tab name
        tab: Sub-tab name (if applicable)
        subtab: Sub-sub-tab name (if applicable)
    """
    init_feedback_storage()
    
    # Get current user info
    username = auth.get_current_user()
    user_role = auth.get_current_role()
    
    # Create feedback entry
    feedback_entry = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'username': username,
        'user_role': user_role,
        'section': section,
        'feedback_text': feedback_text,
        'page': page,
        'tab': tab,
        'subtab': subtab
    }
    
    # Read existing feedback
    df = pd.read_csv(FEEDBACK_FILE)
    
    # Append new feedback
    df = pd.concat([df, pd.DataFrame([feedback_entry])], ignore_index=True)
    
    # Save back to CSV
    df.to_csv(FEEDBACK_FILE, index=False)

def get_all_feedback() -> pd.DataFrame:
    """Get all feedback (admin only)"""
    init_feedback_storage()
    df = pd.read_csv(FEEDBACK_FILE)
    if len(df) > 0:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=False)
    return df

def get_user_feedback(username: str) -> pd.DataFrame:
    """Get feedback for specific user"""
    df = get_all_feedback()
    if len(df) > 0:
        return df[df['username'] == username]
    return df

def get_section_feedback(section: str, username: Optional[str] = None) -> pd.DataFrame:
    """Get feedback for specific section, optionally filtered by user"""
    if username:
        df = get_user_feedback(username)
    else:
        df = get_all_feedback()
    
    if len(df) > 0:
        return df[df['section'] == section]
    return df

def update_feedback(timestamp: str, username: str, new_text: str):
    """Update existing feedback entry"""
    init_feedback_storage()
    df = pd.read_csv(FEEDBACK_FILE)
    
    # Find the feedback entry by timestamp and username
    mask = (df['timestamp'] == timestamp) & (df['username'] == username)
    
    if mask.any():
        df.loc[mask, 'feedback_text'] = new_text
        df.to_csv(FEEDBACK_FILE, index=False)
        return True
    return False

def delete_feedback(timestamp: str, username: str):
    """Delete feedback entry"""
    init_feedback_storage()
    df = pd.read_csv(FEEDBACK_FILE)
    
    # Remove the feedback entry by timestamp and username
    mask = (df['timestamp'] == timestamp) & (df['username'] == username)
    df = df[~mask]
    
    df.to_csv(FEEDBACK_FILE, index=False)
    return True

@st.dialog("💬 Provide Feedback")
def show_feedback_modal(section: str, page: str, tab: str = "", subtab: str = ""):
    """
    Show feedback submission modal
    
    Args:
        section: Full section identifier (e.g., "Customer Voice > Sub-Dimension Overview")
        page: Main page name
        tab: Sub-tab name (optional)
        subtab: Sub-sub-tab name (optional)
    """
    st.markdown(f"**Section:** `{section}`")
    st.markdown(f"**User:** {auth.get_current_user()} ({auth.get_current_role()})")
    st.markdown("---")
    
    feedback_text = st.text_area(
        "Your Feedback",
        placeholder="Share your thoughts, suggestions, or issues about this section...",
        height=150,
        help="Provide detailed feedback to help improve this section"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("📤 Submit Feedback", type="primary", use_container_width=True):
            if feedback_text and feedback_text.strip():
                save_feedback(section, feedback_text.strip(), page, tab, subtab)
                st.success("✅ Feedback submitted successfully!")
                # Small delay to show success message
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("⚠️ Please enter feedback text")
    
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

@st.dialog("📋 View Feedback")
def show_feedback_viewer_modal(section: str):
    """
    Show feedback viewer modal
    Shows all feedback for admins, only user's feedback for reviewers (with edit capability)
    
    Args:
        section: Section to view feedback for
    """
    username = auth.get_current_user()
    is_admin = auth.is_admin()
    
    if is_admin:
        st.markdown("### 🔑 All Feedback")
        
        # Add filter for admins to view only their own feedback
        filter_option = st.radio(
            "View:",
            options=["All Feedback", "My Feedback Only"],
            horizontal=True,
            key=f"admin_filter_{section}"
        )
        
        if filter_option == "My Feedback Only":
            df = get_section_feedback(section, username)
        else:
            df = get_section_feedback(section)
    else:
        st.markdown("### 📝 My Feedback")
        df = get_section_feedback(section, username)
    
    st.markdown(f"**Section:** `{section}`")
    st.markdown("---")
    
    if len(df) == 0:
        st.info("📭 No feedback yet for this section")
    else:
        st.markdown(f"**Total Feedback:** {len(df)}")
        
        # Show feedback entries
        for idx, row in df.iterrows():
            is_own_feedback = row['username'] == username
            
            # Use expander for each feedback to allow editing
            with st.expander(f"👤 {row['username']} - {row['timestamp']}", expanded=False):
                # If viewing own feedback (admin or reviewer), allow editing
                if is_own_feedback:
                    # Create unique key for this feedback entry
                    edit_key = f"edit_{row['timestamp']}_{idx}"
                    delete_key = f"delete_{row['timestamp']}_{idx}"
                    
                    # Initialize session state for edit mode
                    if f"editing_{edit_key}" not in st.session_state:
                        st.session_state[f"editing_{edit_key}"] = False
                    
                    # Show edit/delete buttons
                    if not st.session_state[f"editing_{edit_key}"]:
                        st.markdown(f"""
                        <div style="background-color: white; padding: 10px; border-radius: 5px; border: 1px solid #ddd;">
                            {row['feedback_text']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_edit, col_delete = st.columns(2)
                        with col_edit:
                            if st.button("✏️ Edit", key=f"btn_edit_{edit_key}", use_container_width=True):
                                st.session_state[f"editing_{edit_key}"] = True
                                st.rerun()
                        
                        with col_delete:
                            if st.button("🗑️ Delete", key=f"btn_delete_{delete_key}", type="secondary", use_container_width=True):
                                if delete_feedback(row['timestamp'], username):
                                    st.success("✅ Feedback deleted!")
                                    import time
                                    time.sleep(1)
                                    st.rerun()
                    else:
                        # Edit mode
                        new_text = st.text_area(
                            "Edit your feedback",
                            value=row['feedback_text'],
                            height=150,
                            key=f"textarea_{edit_key}"
                        )
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 Save", key=f"btn_save_{edit_key}", type="primary", use_container_width=True):
                                if new_text and new_text.strip():
                                    if update_feedback(row['timestamp'], username, new_text.strip()):
                                        st.success("✅ Feedback updated!")
                                        st.session_state[f"editing_{edit_key}"] = False
                                        import time
                                        time.sleep(1)
                                        st.rerun()
                                else:
                                    st.error("⚠️ Feedback cannot be empty")
                        
                        with col_cancel:
                            if st.button("❌ Cancel", key=f"btn_cancel_{edit_key}", use_container_width=True):
                                st.session_state[f"editing_{edit_key}"] = False
                                st.rerun()
                else:
                    # Admin view or other user's feedback - just display
                    st.markdown(f"""
                    <div style="background-color: white; padding: 10px; border-radius: 5px; border: 1px solid #ddd;">
                        {row['feedback_text']}
                    </div>
                    """, unsafe_allow_html=True)
    
    if st.button("Close", use_container_width=True):
        st.rerun()

def render_feedback_buttons(section: str, page: str, tab: str = "", subtab: str = "", inline: bool = False):
    """
    Render feedback buttons for a section
    
    Args:
        section: Full section identifier
        page: Main page name
        tab: Sub-tab name (optional)
        subtab: Sub-sub-tab name (optional)
        inline: If True, render narrow buttons suitable for title rows
    """
    # Count feedback for this section
    username = auth.get_current_user()
    is_admin = auth.is_admin()
    
    if is_admin:
        feedback_count = len(get_section_feedback(section))
    else:
        feedback_count = len(get_section_feedback(section, username))
    
    # Inline mode for title rows - narrow columns
    if inline:
        col1, col2, col3 = st.columns([8, 1.2, 1.2])
        
        with col1:
            pass  # Title goes here (rendered by caller)
        
        with col2:
            # Styled feedback button with custom HTML for visibility
            feedback_btn_html = """
            <style>
                .feedback-give-btn {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: 600;
                    font-size: 0.9rem;
                    cursor: pointer;
                    border: none;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    white-space: nowrap;
                }
                .feedback-give-btn:hover {
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                }
            </style>
            """
            st.markdown(feedback_btn_html, unsafe_allow_html=True)
            
            if st.button("💬 Feedback", key=f"feedback_btn_{section}_{page}_{tab}_{subtab}", type="primary"):
                show_feedback_modal(section, page, tab, subtab)
        
        with col3:
            # View feedback button with badge
            view_label = f"📊 {feedback_count}" if feedback_count > 0 else "📊 View"
            button_type = "secondary" if feedback_count == 0 else "primary"
            
            if st.button(view_label, key=f"view_feedback_btn_{section}_{page}_{tab}_{subtab}", type=button_type, help="View provided feedback"):
                show_feedback_viewer_modal(section)
    else:
        # Standard mode - wider buttons in two columns
        col1, col2 = st.columns([3, 2])
        
        with col1:
            if st.button("💬 Provide Feedback", key=f"feedback_btn_{section}_{page}_{tab}_{subtab}", type="primary", use_container_width=True):
                show_feedback_modal(section, page, tab, subtab)
        
        with col2:
            button_label = f"📊 Provided Feedback ({feedback_count})" if feedback_count > 0 else "📊 Provided Feedback"
            button_type = "secondary" if feedback_count == 0 else "primary"
            if st.button(button_label, key=f"view_feedback_btn_{section}_{page}_{tab}_{subtab}", type=button_type, use_container_width=True):
                show_feedback_viewer_modal(section)

def render_admin_feedback_dashboard():
    """Render admin dashboard for viewing all feedback"""
    if not auth.is_admin():
        st.error("🔒 Access denied. Admin privileges required.")
        return
    
    st.markdown("## 🔑 Admin Feedback Dashboard")
    st.markdown("View and analyze all feedback from users")
    st.markdown("---")
    
    df = get_all_feedback()
    
    if len(df) == 0:
        st.info("📭 No feedback submitted yet")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Feedback", len(df))
    
    with col2:
        unique_users = df['username'].nunique()
        st.metric("Unique Users", unique_users)
    
    with col3:
        unique_sections = df['section'].nunique()
        st.metric("Sections", unique_sections)
    
    with col4:
        admin_feedback = len(df[df['user_role'] == 'ADMIN'])
        st.metric("Admin Feedback", admin_feedback)
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_user = st.selectbox(
            "Filter by User",
            options=["All Users"] + sorted(df['username'].unique().tolist())
        )
    
    with col2:
        filter_section = st.selectbox(
            "Filter by Section",
            options=["All Sections"] + sorted(df['section'].unique().tolist())
        )
    
    with col3:
        filter_page = st.selectbox(
            "Filter by Page",
            options=["All Pages"] + sorted(df['page'].unique().tolist())
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if filter_user != "All Users":
        filtered_df = filtered_df[filtered_df['username'] == filter_user]
    
    if filter_section != "All Sections":
        filtered_df = filtered_df[filtered_df['section'] == filter_section]
    
    if filter_page != "All Pages":
        filtered_df = filtered_df[filtered_df['page'] == filter_page]
    
    st.markdown(f"### Showing {len(filtered_df)} feedback entries")
    
    # Display feedback
    for idx, row in filtered_df.iterrows():
        role_badge = "🔑 ADMIN" if row['user_role'] == "ADMIN" else "📝 REVIEWER"
        role_color = "#ff6b6b" if row['user_role'] == "ADMIN" else "#4ecdc4"
        
        with st.expander(f"👤 {row['username']} - {row['section']} - {row['timestamp']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Section:** {row['section']}")
                st.markdown(f"**Page:** {row['page']}" + (f" > {row['tab']}" if row['tab'] else "") + (f" > {row['subtab']}" if row['subtab'] else ""))
            
            with col2:
                st.markdown(f"""
                <div style="background-color: {role_color}; color: white; padding: 5px 10px; border-radius: 5px; text-align: center;">
                    {role_badge}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f"**Feedback:**")
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 15px; border-radius: 5px;">
                {row['feedback_text']}
            </div>
            """, unsafe_allow_html=True)
    
    # Export option
    st.markdown("---")
    if st.button("📥 Export Feedback to CSV"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"feedback_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
