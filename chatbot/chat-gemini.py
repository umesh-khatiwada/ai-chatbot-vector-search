import google.generativeai as genai
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from qdrant_client import QdrantClient
import streamlit as st
import os
from dotenv import load_dotenv
from styles import get_custom_css, get_welcome_banner, get_footer, format_status_indicator

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    st.error("❌ Please set your GEMINI_API_KEY in the .env file")
    st.info("Get your API key from: https://makersuite.google.com/app/apikey")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# Custom embedding class for Gemini
class GeminiEmbeddings:
    def __init__(self, model="models/text-embedding-004"):
        self.model = model
    
    def embed_documents(self, texts):
        """Embed a list of documents"""
        embeddings = []
        for text in texts:
            try:
                result = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
            except Exception as e:
                st.error(f"Error embedding document: {e}")
                return None
        return embeddings
    
    def embed_query(self, text):
        """Embed a single query"""
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            st.error(f"Error embedding query: {e}")
            return None

# Initialize Gemini model for chat
ai_model = os.getenv("AI_MODEL", "gemini-pro")
chat_model = genai.GenerativeModel(ai_model)

# Chat prompt template
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant who helps in finding answers to questions using the provided context.",
        ),
        (
            "human",
            """
        The answer should be based on the text context given in "text_context" and the conversation history given in "conversation_history".
        Base your response on the provided text context and the current conversation history to answer the query.
        Select the most relevant information from the context.
        Generate a draft response using the selected information. Remove duplicate content from the draft response.
        Generate your final response after adjusting it to increase accuracy and relevance.
        Now only show your final response!
        If you do not know the answer or context is not relevant, response with "I don't know".

        text_context:
        {context}

        conversation_history:
        {history}

        query:
        {query}
        """,
        ),
    ]
)

# Initialize embedding model
embedding_model = GeminiEmbeddings()

# Initialize Qdrant client
client = QdrantClient(
    url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    api_key=os.getenv("APIKEY") if os.getenv("APIKEY") != "fkjabjkbsajkbasjkdbaksjbdkabdkjbadkjbadbauosdib" else None,
)

collection_name = os.getenv("COLLECTION_NAME", "chatbot-docs")

# Function to search similar documents
def similarity_search(query, k=4):
    """Search for similar documents in Qdrant"""
    try:
        # Get query embedding
        query_embedding = embedding_model.embed_query(query)
        if query_embedding is None:
            return []
        
        # Search in Qdrant
        search_results = client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=k
        )
        
        # Convert to documents format
        docs = []
        for result in search_results:
            docs.append({
                "page_content": result.payload.get("text", ""),
                "metadata": result.payload.get("metadata", {}),
                "score": result.score
            })
        
        return docs
    except Exception as e:
        st.error(f"Error searching documents: {e}")
        return []

def format_docs(docs):
    return "\n\n".join([d["page_content"] for d in docs])

def display_sources(docs):
    """Display source documents with scores"""
    if docs and len(docs) > 0:
        with st.expander(f"📄 Sources ({len(docs)} documents found)", expanded=False):
            for i, doc in enumerate(docs, 1):
                score_color = "🟢" if doc.get("score", 0) > 0.8 else "🟡" if doc.get("score", 0) > 0.6 else "🔴"
                st.markdown(f"""
                **Source {i}** {score_color} Relevance: {doc.get("score", 0):.2f}
                
                {doc["page_content"][:300]}{"..." if len(doc["page_content"]) > 300 else ""}
                
                ---
                """)

# Streamlit UI Configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    # Connection Status
    try:
        # Test Qdrant connection
        collections = client.get_collections()
        qdrant_status = "🟢 Connected"
        qdrant_color = "status-online"
    except:
        qdrant_status = "🔴 Disconnected"
        qdrant_color = "status-offline"
    
    st.markdown(format_status_indicator(qdrant_status, "Qdrant Database", qdrant_color), unsafe_allow_html=True)
    
    # API Status
    try:
        # Test Gemini API
        test_response = genai.embed_content(
            model="models/text-embedding-004",
            content="test",
            task_type="retrieval_query"
        )
        api_status = "🟢 Connected"
        api_color = "status-online"
    except:
        api_status = "🔴 API Key Invalid"
        api_color = "status-offline"
    
    st.markdown(format_status_indicator(api_status, "Gemini API", api_color), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Chat Settings
    st.markdown("### 🎛️ Chat Settings")
    
    # Model selection
    model_options = ["gemini-2.5-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
    current_model = os.getenv("AI_MODEL", "gemini-pro")
    selected_model = st.selectbox("AI Model", model_options, index=model_options.index(current_model) if current_model in model_options else 0)
    
    # Search results count
    search_limit = st.slider("Search Results", min_value=1, max_value=10, value=4, help="Number of relevant documents to retrieve")
    
    # Temperature (if we want to add it later)
    temperature = st.slider("Response Creativity", min_value=0.0, max_value=1.0, value=0.7, step=0.1, help="Higher values make responses more creative")
    
    st.markdown("---")
    
    # Statistics
    st.markdown("### 📊 Session Stats")
    message_count = len(st.session_state.get("messages", [])) - 1  # Exclude welcome message
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Messages", message_count)
    with col2:
        st.metric("Collection", collection_name)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
        st.session_state["messages"] = [{"role": "ai", "content": os.getenv("APP_CONTENT", "Welcome to the AI Chatbot! How can I help you?")}]
        st.session_state["memory"].clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📚 Quick Help")
    with st.expander("💡 Tips"):
        st.markdown("""
        - Ask specific questions for better results
        - Reference previous conversation context
        - Use keywords related to your documents
        - Check the status indicators above
        """)
    
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        - **Red status**: Check your API keys and connections
        - **No results**: Ensure documents are uploaded to Qdrant
        - **Slow responses**: Try reducing search results count
        """)

# Main Chat Interface
app_title = os.getenv("APP_TITLE", "🤖 AI Chatbot with Vector Search")
st.markdown(get_welcome_banner(app_title), unsafe_allow_html=True)

# Welcome message (shown only for new sessions)
if len(st.session_state.get("messages", [])) <= 1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; color: white; text-align: center; margin: 2rem 0;">
        <h3>👋 Welcome to your AI Assistant!</h3>
        <p>I can help you find information from your knowledge base. Ask me anything!</p>
        <p><strong>💡 Example:</strong> "What is this chatbot?" or "How does vector search work?"</p>
    </div>
    """, unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    app_content = os.getenv("APP_CONTENT", "Welcome to the AI Chatbot! How can I help you?")
    st.session_state["messages"] = [{"role": "ai", "content": app_content}]

# Initialize conversation memory
if "memory" not in st.session_state:
    st.session_state["memory"] = ConversationBufferWindowMemory(
        memory_key="history",
        ai_prefix="Assistant",
        human_prefix="User",
        k=3,
    )

# Chat container
chat_container = st.container()

with chat_container:
    # Display chat history with enhanced styling
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "ai":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message["content"])
        else:
            with st.chat_message("user", avatar="👤"):
                st.markdown(message["content"])

# Chat input
if chat_input := st.chat_input("💬 Ask me anything about your documents..."):
    # Add user message to chat
    with st.chat_message("user", avatar="👤"):
        st.markdown(chat_input)
        st.session_state.messages.append({"role": "human", "content": chat_input})

    # Search for relevant documents
    with st.spinner("🔍 Searching knowledge base..."):
        found_docs = similarity_search(chat_input, k=search_limit)
        context = format_docs(found_docs)

    # Prepare the prompt
    history = st.session_state.memory.load_memory_variables({}).get("history", "")
    
    prompt_text = f"""
    You are a helpful AI assistant. Use the provided context and conversation history to answer the user's question.
    
    INSTRUCTIONS:
    - Base your response primarily on the provided context
    - Reference the conversation history when relevant
    - If the context doesn't contain relevant information, say "I don't have enough information to answer that question."
    - Be concise but comprehensive
    - Use a friendly, professional tone
    
    CONTEXT:
    {context}
    
    CONVERSATION HISTORY:
    {history}
    
    USER QUESTION:
    {chat_input}
    
    RESPONSE:
    """

    # Generate response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🤔 Thinking..."):
            try:
                # Update model if changed in sidebar
                current_chat_model = genai.GenerativeModel(selected_model)
                
                response = current_chat_model.generate_content(prompt_text)
                content = response.text
                
                # Display response with typing effect simulation
                response_placeholder = st.empty()
                displayed_text = ""
                
                # Simulate typing effect (optional, remove if too slow)
                import time
                words = content.split()
                for i, word in enumerate(words):
                    displayed_text += word + " "
                    if i % 5 == 0:  # Update every 5 words
                        response_placeholder.markdown(displayed_text)
                        time.sleep(0.1)
                
                response_placeholder.markdown(content)
                st.session_state.messages.append({"role": "ai", "content": content})
                
                # Display sources
                display_sources(found_docs)
                
                # Save to memory
                st.session_state.memory.save_context({"input": chat_input}, {"output": content})
                
                # Success metrics
                if found_docs:
                    avg_score = sum(doc.get("score", 0) for doc in found_docs) / len(found_docs)
                    if avg_score > 0.7:
                        st.success(f"✅ High confidence response (relevance: {avg_score:.2f})")
                    elif avg_score > 0.5:
                        st.info(f"ℹ️ Moderate confidence response (relevance: {avg_score:.2f})")
                    else:
                        st.warning(f"⚠️ Low confidence response (relevance: {avg_score:.2f})")
                
            except Exception as e:
                error_msg = f"❌ Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "ai", "content": error_msg})

# Footer
st.markdown(get_footer(), unsafe_allow_html=True)
