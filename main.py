import streamlit as st
import asyncio
from config import OPENROUTER_API_KEY, YOUTUBE_API_KEY, CURRENT_USER
from document_qa import process_input, answer_question
from youtube_qa import YouTubeQASystem
from styles import set_custom_style

def main():
    st.set_page_config(
        page_title="AskIt - Multi-Modal Q&A System", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    set_custom_style()
    
    # Header section with user info
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.title("AskIt - Multi-Modal Q&A System")
        with col2:
            st.write(f"User: {CURRENT_USER}")    
    st.markdown("---")
    
    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["📄 Document Q&A", "🎬 YouTube Q&A"])

    # Document Q&A tab
    with tab1:
        st.markdown("### 🔍 Ask Questions About Your Documents")
        st.markdown(
            """
            Upload documents, provide links, or enter text directly to ask questions and get AI-powered answers.
            The system supports multiple formats including PDFs, Word documents, plain text, and even images.
            """
        )
        
        # Input selection and data entry
        input_col1, input_col2 = st.columns([1, 3])
        with input_col1:
            input_type = st.selectbox(
                "Select Input Type",
                ["PDF", "DOCX", "TXT", "Link", "Text", "Image"],
                help="Choose the type of content you want to analyze"
            )
        
        with input_col2:
            if input_type == "Link":
                number_of_links = st.number_input("Number of Links", min_value=1, max_value=5, value=1, step=1)
                input_data = [st.text_input(f"Link {i+1}", key=f"link_{i}") for i in range(int(number_of_links))]
                input_data = [link for link in input_data if link.strip()]
            elif input_type == "Text":
                input_data = st.text_area("Enter your text", height=200)
            else:
                file_types = {
                    "PDF": ["pdf"],
                    "DOCX": ["docx"],
                    "TXT": ["txt"],
                    "Image": ["png", "jpg", "jpeg", "bmp", "tiff"]
                }[input_type]
                
                input_data = st.file_uploader(
                    f"Upload {input_type} files",
                    type=file_types,
                    accept_multiple_files=True,
                    help=f"Select one or more {input_type} files to upload"
                )

        # Process button and handling
        process_col1, process_col2 = st.columns([3, 1])
        with process_col2:
            process_button = st.button("Process", use_container_width=True)
        
        if process_button:
            if input_data:
                try:
                    with st.spinner("Processing documents..."):
                        vectorstore = process_input(input_type, input_data)
                        st.session_state["vectorstore"] = vectorstore
                        st.markdown(
                            f"""
                            <div class='success-message'>
                                ✅ Processed {"links" if input_type == "Link" else "documents"} successfully!
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                except Exception as e:
                    st.markdown(
                        f"""
                        <div class='error-message'>
                            ❌ Processing error: {str(e)}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    """
                    <div class='error-message'>
                        ❌ Please provide valid input
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("---")

        # Question answering section (once documents are processed)
        if "vectorstore" in st.session_state:
            st.markdown("### 🤔 Ask Your Question")
            query = st.text_input("What would you like to know?", placeholder="Enter your question here...")
            
            if st.button("Submit Question", use_container_width=False) and query.strip():
                with st.spinner("Generating answer..."):
                    answer, context, metrics = answer_question(st.session_state["vectorstore"], query, OPENROUTER_API_KEY)
                    
                    st.markdown("### 💡 Answer")
                    st.markdown(f"<div class='answer-box'>{answer}</div>", unsafe_allow_html=True)
                    
                    with st.expander("View Metrics"):
                        st.markdown("### Performance Metrics")
                        metrics_cols = st.columns(4)
                        with metrics_cols[0]:
                            st.markdown(f"<div class='metric-card'><b>F1 Score</b><br>{metrics['f1']:.2%}</div>", unsafe_allow_html=True)
                        with metrics_cols[1]:
                            st.markdown(f"<div class='metric-card'><b>Exact Match</b><br>{metrics['exact_match']:.2%}</div>", unsafe_allow_html=True)
                        # with metrics_cols[2]:
                            # st.markdown(f"<div class='metric-card'><b>BLEU Score</b><br>{metrics['bleu']:.2%}</div>", unsafe_allow_html=True)
                        with metrics_cols[3]:
                            st.markdown(f"<div class='metric-card'><b>ROUGE-L</b><br>{metrics['rouge']['rougeL']:.2%}</div>", unsafe_allow_html=True)

    # YouTube Q&A tab
    with tab2:
        st.markdown("### 🎥 Ask Questions About YouTube Videos")
        st.markdown("Enter a YouTube video URL and ask questions about its content.")
        
        video_url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
        
        # Display embedded YouTube video when URL is provided
        if video_url:
            try:
                video_id = YouTubeQASystem(YOUTUBE_API_KEY, OPENROUTER_API_KEY).extract_video_id(video_url)
                if video_id:
                    st.markdown(f"""
                        <div style="display: flex; justify-content: center; margin: 1rem 0;">
                            <iframe width="560" height="315" 
                                    src="https://www.youtube.com/embed/{video_id}" 
                                    frameborder="0" 
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                                    allowfullscreen>
                            </iframe>
                        </div>
                    """, unsafe_allow_html=True)
            except:
                pass
        
        question = st.text_input("Your Question", placeholder="What is this video about?")
        
        if st.button("Get Answer", use_container_width=False) and video_url and question:
            youtube_qa = YouTubeQASystem(YOUTUBE_API_KEY, OPENROUTER_API_KEY)
            
            with st.spinner("Processing video and generating answer..."):
                response = asyncio.run(youtube_qa.process_video(video_url, question))
                
                if "error" in response:
                    st.markdown(
                        f"""
                        <div class='error-message'>
                            ❌ Error: {response['error']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(f"### {response['video_title']}")
                    st.markdown(f"<div class='answer-box'>{response['answer']}</div>", unsafe_allow_html=True)
                    
                    if "thumbnail" in response and response["thumbnail"]:
                        with st.expander("Video Information"):
                            st.image(response["thumbnail"], width=300)
                            st.caption(f"Generated at: {response['timestamp']}")
                    else:
                        st.caption(f"Generated at: {response['timestamp']}")

    # Footer
    st.markdown("""
    <div class="footer">
        AskIt - A MultiModal Chatbot
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()