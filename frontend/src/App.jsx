import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2 } from 'lucide-react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { role: 'agent', content: 'Hello. I am the clinical intake assistant. Can you briefly describe what brings you in today?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to the bottom when a new message arrives
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(() => { scrollToBottom(); }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      // Ping your local FastAPI backend
      const response = await fetch('https://jubilant-couscous-4j99pvp64474fqv4x-8000.app.github.dev/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userMessage,
          thread_id: "demo_user_1" // Hardcoded for this demo
        })
      });

      if (!response.ok) throw new Error('Network response was not ok');
      
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'agent', content: data.reply }]);
      
    } catch (error) {
      console.error("Error connecting to backend:", error);
      setMessages(prev => [...prev, { role: 'agent', content: "Sorry, I'm having trouble connecting to the clinic's server right now." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Healthcare Intake Portal</h1>
        <p>Confidential & Secure AI Triage</p>
      </header>

      <main className="chat-container">
        <div className="message-list">
          {messages.map((msg, index) => (
            <div key={index} className={`message-wrapper ${msg.role}`}>
              <div className="avatar">
                {msg.role === 'agent' ? <Bot size={20} /> : <User size={20} />}
              </div>
              <div className="message-bubble">
                {msg.content}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message-wrapper agent">
              <div className="avatar"><Bot size={20} /></div>
              <div className="message-bubble loading">
                <Loader2 className="spinner" size={16} /> Typing...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={sendMessage} className="input-area">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe your symptoms..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            <Send size={18} />
          </button>
        </form>
      </main>
    </div>
  );
}

export default App;