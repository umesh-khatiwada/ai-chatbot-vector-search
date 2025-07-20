"""
Streamlit CSS Styles for AI Chatbot

This module contains all the custom CSS styles used in the Streamlit chatbot interface.
Separated from the main chat file for better organization and maintainability.
"""

def get_custom_css():
    """
    Returns the custom CSS styles for the Streamlit chatbot interface.
    
    Returns:
        str: CSS styles as a string
    """
    return """
    <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 2rem;
        }
        
        .chat-container {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        
        .status-online {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status-offline {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .sidebar-content {
            background-color: #f1f3f4;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        .footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            border-top: 1px solid #eee;
            margin-top: 3rem;
        }
        
        /* Enhanced chat message styling */
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .user-message {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: 2rem;
        }
        
        .assistant-message {
            background-color: #f8f9fa;
            border-left: 4px solid #667eea;
            margin-right: 2rem;
        }
        
        /* Source documents styling */
        .source-document {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .source-header {
            font-weight: bold;
            color: #495057;
            margin-bottom: 0.5rem;
        }
        
        .relevance-score {
            display: inline-block;
            padding: 0.2rem 0.5rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .score-high {
            background-color: #d4edda;
            color: #155724;
        }
        
        .score-medium {
            background-color: #fff3cd;
            color: #856404;
        }
        
        .score-low {
            background-color: #f8d7da;
            color: #721c24;
        }
        
        /* Welcome banner styling */
        .welcome-banner {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin: 2rem 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .welcome-banner h3 {
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }
        
        .welcome-banner p {
            margin: 0.5rem 0;
            opacity: 0.9;
        }
        
        /* Sidebar enhancements */
        .sidebar-section {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 4px solid #667eea;
        }
        
        .sidebar-title {
            font-weight: bold;
            color: #495057;
            margin-bottom: 0.5rem;
        }
        
        /* Loading spinner customization */
        .stSpinner > div {
            border-top-color: #667eea !important;
        }
        
        /* Custom button styling */
        .custom-button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .custom-button:hover {
            box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
            transform: translateY(-2px);
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main-header {
                font-size: 2rem;
            }
            
            .welcome-banner {
                padding: 1.5rem;
            }
            
            .chat-message {
                margin-left: 0.5rem;
                margin-right: 0.5rem;
            }
        }
        
        /* Hide Streamlit default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #5a6fd8;
        }
    </style>
    """

def get_welcome_banner(title="🤖 AI Chatbot with Vector Search"):
    """
    Returns the HTML for the welcome banner with customizable title.
    
    Args:
        title (str): The title to display in the banner
    
    Returns:
        str: HTML string for the welcome banner
    """
    return f"""
    <div class="main-header">
        {title}
    </div>
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #666;">
            Get intelligent responses powered by advanced AI and vector search
        </p>
    </div>
    """

def get_footer():
    """
    Returns the HTML for the footer.
    
    Returns:
        str: HTML string for the footer
    """
    return """
    <div class="footer">
        <p>🤖 Powered by Google Gemini API & Qdrant Vector Database</p>
        <p>💡 <strong>Tip:</strong> Ask specific questions for better results</p>
    </div>
    """

def format_status_indicator(status_text, service_name, color_class):
    """
    Returns HTML for a status indicator.
    
    Args:
        status_text (str): The status text to display (e.g., "🟢 Connected")
        service_name (str): The name of the service (e.g., "Qdrant Database")
        color_class (str): The CSS class for styling (e.g., "status-online")
    
    Returns:
        str: HTML string for the status indicator
    """
    return f'<div class="status-indicator {color_class}">{status_text} {service_name}</div>'

def format_relevance_score(score):
    """
    Returns HTML for a relevance score badge.
    
    Args:
        score (float): Relevance score between 0 and 1
    
    Returns:
        str: HTML string for the score badge
    """
    if score > 0.8:
        score_class = "score-high"
        emoji = "🟢"
    elif score > 0.6:
        score_class = "score-medium"
        emoji = "🟡"
    else:
        score_class = "score-low"
        emoji = "🔴"
    
    return f'<span class="relevance-score {score_class}">{emoji} {score:.2f}</span>'
