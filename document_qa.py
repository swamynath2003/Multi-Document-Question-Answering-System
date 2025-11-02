import numpy as np
import faiss
import re
from io import BytesIO
from docx import Document
from PyPDF2 import PdfReader
from PIL import Image
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from image_processor import ImageProcessor
from utils import calculate_metrics

def process_input(input_type, input_data):
    """Process different types of input and create a vector store for querying"""
    documents = ""
    
    if input_type == "Link":
        loader = WebBaseLoader(input_data)
        web_documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = [str(doc.page_content) for doc in text_splitter.split_documents(web_documents)]
    elif input_type == "PDF":
        for file in input_data:
            pdf_reader = PdfReader(BytesIO(file.read()))
            for page in pdf_reader.pages:
                documents += page.extract_text() + "\n"
    elif input_type == "Text":
        documents = input_data
    elif input_type == "DOCX":
        for file in input_data:
            doc = Document(BytesIO(file.read()))
            documents += "\n".join([para.text for para in doc.paragraphs]) + "\n"
    elif input_type == "TXT":
        for file in input_data:
            documents += file.read().decode('utf-8') + "\n"
    elif input_type == "Image":
        image_processor = ImageProcessor()
        for file in input_data:
            image = Image.open(BytesIO(file.read()))
            text = image_processor.process_image(image)
            documents += text + "\n"
    else:
        raise ValueError("Unsupported input type")

    if input_type != "Link":
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.split_text(documents)

    # Create embeddings using HuggingFace model
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': False}
    )
    
    # Set up FAISS vector store
    dimension = np.array(embeddings.embed_query("sample text")).shape[0]
    index = faiss.IndexFlatL2(dimension)
    
    vector_store = FAISS(
        embedding_function=embeddings.embed_query,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    vector_store.add_texts(texts)
    return vector_store

def answer_question(vectorstore, query, openrouter_api_key):
    """Answer a question using the vector store and OpenRouter API"""
    try:
        # Get relevant context from vector store
        context = " ".join([doc.page_content for doc in vectorstore.as_retriever().get_relevant_documents(query)])
        
        # Use OpenRouter with Mistral-7B-Instruct (free)
        llm = ChatOpenAI(
            model="mistralai/mistral-7b-instruct:free",
            openai_api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.6,
            max_tokens=1000
        )
        
        # Use LangChain for retrieval QA
        qa = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())
        result = qa({"query": query})
        answer = result.get("result", "No answer found.")
        
        # Calculate metrics
        metrics = calculate_metrics(answer, context)
        return answer, context, metrics
        
    except Exception as e:
        error_metrics = {
            'f1': 0.0, 'exact_match': 0.0, 'bleu': 0.0,
            'rouge': {'rouge1': 0.0, 'rouge2': 0.0, 'rougeL': 0.0}
        }
        return f"An error occurred: {str(e)}", "", error_metrics