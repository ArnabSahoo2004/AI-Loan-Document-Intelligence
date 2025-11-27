import streamlit as st
import pandas as pd
import os
from PIL import Image

# Config
DATA_FILE = "data/training_data_final.csv"
IMAGE_DIR = "data/kaggle_dataset/Salary Slip"

st.set_page_config(layout="wide", page_title="Data Verification Tool")

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

def save_data(df):
    try:
        df.to_csv(DATA_FILE, index=False)
        st.toast("Saved successfully!", icon="✅")
    except PermissionError:
        st.error("⚠️ Permission Denied! Please close the CSV file in Excel or other programs and try again.")
    except Exception as e:
        st.error(f"Error saving file: {e}")

def main():
    st.title("🕵️ Salary Slip Data Verification")
    
    if "df" not in st.session_state:
        st.session_state.df = load_data()
    
    df = st.session_state.df
    
    if df.empty:
        st.error("No data found!")
        return

    # Filter for Review Needed
    review_needed = df[df['status'].str.contains("Review", na=False)]
    auto_labeled = df[~df['status'].str.contains("Review", na=False)]
    
    st.sidebar.header("Progress")
    st.sidebar.metric("Total Images", len(df))
    st.sidebar.metric("Needs Review", len(review_needed))
    st.sidebar.metric("Verified/Auto", len(auto_labeled))
    
    # Navigation
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
        
    # Option to filter
    filter_mode = st.sidebar.radio("Show:", ["All", "Needs Review Only"], index=1)
    
    if filter_mode == "Needs Review Only":
        current_df = review_needed
    else:
        current_df = df
        
    if current_df.empty:
        st.success("🎉 No items need review! You are done.")
        return

    # Progress Bar
    progress_val = len(auto_labeled) / len(df)
    st.progress(progress_val)
    st.write(f"**Progress:** {len(auto_labeled)} / {len(df)} Verified ({len(review_needed)} Remaining)")

    # Pagination
    idx = st.session_state.current_index
    if idx >= len(current_df):
        idx = 0
        st.session_state.current_index = 0
        
    row = current_df.iloc[idx]
    original_index = row.name # Keep track of index in main DF
    
    # Layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(f"Image: {row['filename']}")
        img_path = os.path.join(IMAGE_DIR, row['filename'])
        if os.path.exists(img_path):
            image = Image.open(img_path)
            st.image(image, use_column_width=True)
        else:
            st.error(f"Image not found: {img_path}")
            
    with col2:
        st.subheader("Edit Data")
        
        with st.form("edit_form"):
            new_salary = st.number_input("Salary", value=float(row['salary']))
            new_net_pay = st.number_input("Net Pay", value=float(row['net_pay']))
            new_name = st.text_input("Name", value=str(row['extracted_name']) if pd.notna(row['extracted_name']) else "")
            
            # Status
            status_options = ["Verified", "Review Needed", "Discard (Unreadable)"]
            current_status = "Review Needed" if "Review" in row['status'] else "Verified"
            if "Discard" in row['status']: current_status = "Discard (Unreadable)"
            
            new_status = st.selectbox("Status", status_options, index=status_options.index(current_status) if current_status in status_options else 1)
            
            # Navigation Buttons
            c1, c2, c3 = st.columns(3)
            submitted = c1.form_submit_button("💾 Save & Next")
            skip = c2.form_submit_button("⏭️ Skip")
            prev = c3.form_submit_button("⏮️ Previous")
            
            if submitted:
                # Update Main DF
                st.session_state.df.at[original_index, 'salary'] = new_salary
                st.session_state.df.at[original_index, 'net_pay'] = new_net_pay
                st.session_state.df.at[original_index, 'extracted_name'] = new_name
                st.session_state.df.at[original_index, 'status'] = new_status
                
                save_data(st.session_state.df)
                
                # Move to next
                if st.session_state.current_index < len(current_df) - 1:
                    st.session_state.current_index += 1
                st.rerun()
                
            if skip:
                if st.session_state.current_index < len(current_df) - 1:
                    st.session_state.current_index += 1
                st.rerun()

            if prev:
                if st.session_state.current_index > 0:
                    st.session_state.current_index -= 1
                st.rerun()

    # Raw Text for Context
    with st.expander("Show OCR Text Snippet"):
        st.text(row['raw_text_snippet'])

if __name__ == "__main__":
    main()
