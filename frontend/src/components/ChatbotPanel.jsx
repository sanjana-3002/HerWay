import React, { useState, useRef, useEffect } from 'react';
import { Send, X, Sparkles, Loader2 } from 'lucide-react';

const ChatbotPanel = ({ selectedNeighborhood }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const suggestedPrompts = [
    'Quick summary of this area',
    'What is it like at night?',
    'Top 3 tips for visitors',
    'Best times to visit'
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Generate session ID on first open
  useEffect(() => {
    if (isOpen && !sessionId) {
      setSessionId(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
    }
  }, [isOpen, sessionId]);

  const formatResponse = (text) => {
    return text
      .split('\n')
      .map((line, i) => {
        if (line.trim().startsWith('•') || line.trim().startsWith('-') || line.trim().startsWith('*')) {
          return <div key={i} className="chat-bullet">{line.trim().substring(1).trim()}</div>;
        }
        if (/^\d+\./.test(line.trim())) {
          return <div key={i} className="chat-bullet">{line.trim()}</div>;
        }
        if (!line.trim()) return <br key={i} />;
        return <p key={i} style={{ margin: '4px 0' }}>{line}</p>;
      });
  };

  const handleSendMessage = async (text) => {
    if (!text.trim() || isLoading) return;

    // Build the question with neighborhood context if selected
    let question = text;
    if (selectedNeighborhood) {
      question = `About ${selectedNeighborhood.neighborhood}: ${text}`;
    }

    const userMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('https://herway-89n6.onrender.com/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question,
          session_id: sessionId || 'default'
        })
      });

      if (!response.ok) throw new Error('Failed to get response');

      const data = await response.json();
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer || 'Sorry, I could not process that request.'
      }]);

      // Update session ID if returned
      if (data.session_id) {
        setSessionId(data.session_id);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠️ Connection error. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePromptClick = (prompt) => handleSendMessage(prompt);
  const handleSubmit = (e) => { e.preventDefault(); handleSendMessage(inputValue); };
  const clearChat = () => {
    setMessages([]);
    setSessionId(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  };

  if (!isOpen) {
    return (
      <button className="chatbot-fab" onClick={() => setIsOpen(true)} data-testid="chatbot-fab">
        <Sparkles size={22} />
        <span>Ask HerWay</span>
      </button>
    );
  }

  return (
    <div className="chatbot-panel" data-testid="chatbot-panel">
      <div className="chatbot-header">
        <div className="chatbot-header-icon">
          <Sparkles size={20} />
          <span>HerWay</span>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {messages.length > 0 && (
            <button className="chatbot-close" onClick={clearChat} style={{ fontSize: '11px', padding: '5px 10px' }}>
              Clear
            </button>
          )}
          <button className="chatbot-close" onClick={() => setIsOpen(false)} data-testid="chatbot-close">
            <X size={18} />
          </button>
        </div>
      </div>

      <div className="chatbot-body" data-testid="chatbot-body">
        {messages.length === 0 ? (
          <>
            <div className="chatbot-welcome">
              <div className="welcome-icon">🗺️</div>
              <h3>Explore Chicago</h3>
              <p>Click a neighborhood, then ask me anything</p>
            </div>

            {selectedNeighborhood ? (
              <div className="chatbot-context selected" data-testid="chatbot-context">
                <div className="chatbot-context-label">📍 Selected</div>
                <div className="chatbot-context-value">{selectedNeighborhood.neighborhood}</div>
              </div>
            ) : (
              <div className="chatbot-context empty">
                <div className="chatbot-context-label">No area selected</div>
                <div className="chatbot-context-value">Tap a neighborhood on the map</div>
              </div>
            )}

            <div className="suggested-prompts">
              {suggestedPrompts.map((prompt, idx) => (
                <button 
                  key={idx} 
                  className="suggested-prompt" 
                  onClick={() => handlePromptClick(prompt)} 
                  disabled={isLoading}
                  data-testid={`suggested-prompt-${idx}`}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </>
        ) : (
          <>
            {selectedNeighborhood && (
              <div className="chatbot-context selected compact">
                <span>📍 {selectedNeighborhood.neighborhood}</span>
              </div>
            )}
            
            {messages.map((msg, idx) => (
              <div key={idx} className={`chat-message ${msg.role}`} data-testid={`chat-message-${idx}`}>
                {msg.role === 'assistant' ? formatResponse(msg.content) : msg.content}
              </div>
            ))}
            
            {isLoading && (
              <div className="chat-message assistant loading-msg">
                <Loader2 size={16} className="spinner" />
                <span>Thinking...</span>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <form className="chatbot-input-area" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chatbot-input"
          placeholder={selectedNeighborhood ? `Ask about ${selectedNeighborhood.neighborhood}...` : "Ask about any Chicago neighborhood..."}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={isLoading}
          data-testid="chatbot-input"
        />
        <button 
          type="submit" 
          className="chatbot-send" 
          disabled={!inputValue.trim() || isLoading}
          data-testid="chatbot-send"
        >
          {isLoading ? <Loader2 size={18} className="spinner" /> : <Send size={18} />}
        </button>
      </form>
    </div>
  );
};

export default ChatbotPanel;

