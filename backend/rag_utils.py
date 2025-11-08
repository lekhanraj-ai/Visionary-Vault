import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Setup Chroma DB path
CHROMA_DB_DIR = os.path.join(os.getcwd(), "chroma_db")
os.makedirs(CHROMA_DB_DIR, exist_ok=True)

# Load embeddings model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def ingest_pdfs_to_chroma(file_path: str):
    """
    Loads a PDF, splits it into chunks, and stores embeddings into Chroma DB.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF not found at {file_path}")

        print(f"📄 Loading PDF: {file_path}")
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = splitter.split_documents(documents)

        print(f"💾 Storing {len(chunks)} chunks in Chroma DB...")
        vector_store = Chroma.from_documents(chunks, embedding=embeddings, persist_directory=CHROMA_DB_DIR)
        vector_store.persist()

        return {"message": f"✅ Ingested {os.path.basename(file_path)} and stored {len(chunks)} chunks in Chroma DB."}

    except Exception as e:
        print(f"❌ Error ingesting {file_path}: {e}")
        return {"error": str(e)}

def answer_query(question: str):
    """
    Queries the Chroma DB for context and uses Gemini to generate an answer.
    """
    try:
        vector_store = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)
        retriever = vector_store.as_retriever(search_kwargs={"k": 4})
        docs = retriever.invoke(question)

        if not docs:
            return {"answer": "⚠️ No relevant context found in indexed documents. Try ingesting more PDFs."}

        context = "\n\n".join([doc.page_content for doc in docs])

        prompt = f"""
        You are an ESG compliance expert.
        Based on the following documents, answer this question precisely.

        Context:
        {context}

        Question:
        {question}

        Provide a clear, well-structured explanation.
        """

        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return {"answer": response.text.strip()}

    except Exception as e:
        print(f"❌ Error answering query: {e}")
        return {"error": str(e)}
