import streamlit as st

def set_custom_style():
    """Set custom styling for the Streamlit app"""
    st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1 {
            color: #1E3A8A;
            margin-bottom: 1.5rem;
        }
        h2 {
            color: #2563EB;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }
        h3 {
            color: #3B82F6;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }
        .stButton>button {
            background-color: #2563EB;
            color: white;
            border-radius: 0.375rem;
            padding: 0.5rem 1rem;
            font-weight: 600;
            border: none;
        }
        .stButton>button:hover {
            background-color: #1D4ED8;
        }
        .metric-card {
            # background-color: #F3F4F6;
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .answer-box {
            # background-color: #F0F9FF;
            border-left: 4px solid #2563EB;
            padding: 1rem;
            border-radius: 0.25rem;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        .error-message {
            color: #DC2626;
            background-color: #FEE2E2;
            padding: 0.75rem;
            border-radius: 0.375rem;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }
        .success-message {
            color: #047857;
            background-color: #ECFDF5;
            padding: 0.75rem;
            border-radius: 0.375rem;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }
        .info-text {
            color: #4B5563;
            font-size: 0.875rem;
        }
        .footer {
            margin-top: 2rem;
            text-align: center;
            color: #6B7280;
            font-size: 0.75rem;
        }
    </style>
    """, unsafe_allow_html=True)