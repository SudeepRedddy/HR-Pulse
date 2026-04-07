import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { Send, X, MessageCircle, Bot, Loader2 } from 'lucide-react';
import api from '../../api/client';

export function FloatingAria() {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState<{ role: 'user' | 'assistant', content: string }[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history, isOpen]);

  if (location.pathname === '/login') return null;

  const handleSend = async () => {
    if (!message.trim() || isLoading) return;

    const userMessage = { role: 'user' as const, content: message };
    setHistory(prev => [...prev, userMessage]);
    setMessage('');
    setIsLoading(true);

    try {
      const res = await api.post('/aria/chat', { 
        message: userMessage.content,
        history: history.slice(-6) 
      });
      
      const assistantMessage = { 
        role: 'assistant' as const, 
        content: res.data?.response || "I've analyzed your request. Is there anything else you'd like to explore?" 
      };
      setHistory(prev => [...prev, assistantMessage]);
    } catch {
      setHistory(prev => [...prev, { role: 'assistant', content: "Connection to the intelligence core was interrupted. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Button */}
      <button 
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-8 right-8 w-[52px] h-[52px] bg-white text-hr-black rounded-full shadow-lg flex items-center justify-center hover:scale-105 transition-all duration-300 z-40 border border-hr-border ${isOpen ? 'scale-0 opacity-0' : 'scale-100 opacity-100'}`}
      >
        <MessageCircle className="w-6 h-6" />
      </button>

      {/* Chat Drawer */}
      <div 
        className={`fixed inset-y-0 right-0 w-full md:w-[420px] bg-white text-hr-black z-50 transform transition-transform duration-500 ease-in-out flex flex-col shadow-2xl border-l border-hr-border ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}
      >
        {/* Header */}
        <div className="p-6 bg-white flex items-center justify-between border-b border-hr-border">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-hr-surface border border-hr-border rounded flex items-center justify-center">
              <Bot className="w-5 h-5 text-hr-black" />
            </div>
            <div>
              <h3 className="font-serif text-lg tracking-tight text-hr-black">ARIA AI</h3>
              <p className="text-[10px] text-gray-500 uppercase tracking-[0.2em] font-medium">Strategic Support Core</p>
            </div>
          </div>
          <button onClick={() => setIsOpen(false)} className="text-gray-400 hover:text-hr-black transition-colors duration-300">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Messages area */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 bg-[#FAFAFA]">
          {history.length === 0 && (
            <div className="text-center py-12 space-y-6">
              <div className="w-16 h-16 mx-auto bg-hr-surface flex items-center justify-center border border-hr-border rounded">
                <Bot className="w-8 h-8 text-gray-400" />
              </div>
              <p className="text-xs uppercase tracking-[0.15em] font-medium text-gray-500">How can I assist your objectives today?</p>
              <div className="space-y-2 text-[11px] text-gray-400 italic">
                <p>"What is our leave policy?"</p>
                <p>"Show me recruitment insights"</p>
                <p>"How does the performance predictor work?"</p>
              </div>
            </div>
          )}
          {history.map((chat, i) => (
            <div key={i} className={`flex ${chat.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] p-4 text-[13px] rounded tracking-wide ${
                chat.role === 'user' 
                  ? 'bg-hr-black text-white shadow-sm' 
                  : 'bg-white border border-hr-border text-hr-black shadow-sm'
              }`}>
                <div className="leading-relaxed whitespace-pre-line">{chat.content}</div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-hr-border p-4 rounded shadow-sm flex items-center space-x-3">
                <Loader2 className="w-4 h-4 animate-spin text-hr-black" />
                <span className="text-[11px] text-gray-500 uppercase tracking-widest animate-pulse font-medium">Thinking...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="p-6 border-t border-hr-border bg-white">
          <div className="flex items-center space-x-3 bg-hr-surface p-1.5 rounded border border-hr-border focus-within:border-hr-black transition-colors">
            <input 
              type="text" 
              value={message}
              onChange={e => setMessage(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              placeholder="Message ARIA..."
              className="flex-1 bg-transparent px-3 py-2 text-[13px] focus:outline-none placeholder:text-gray-400 text-hr-black"
            />
            <button 
              onClick={handleSend}
              disabled={isLoading || !message.trim()}
              className="bg-hr-black text-white p-2.5 rounded hover:opacity-85 disabled:opacity-30 disabled:hover:bg-hr-black transition-opacity"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <p className="mt-4 text-center text-[10px] text-gray-400">Powered by HRPulse Core & Ollama Engine</p>
        </div>
      </div>
    </>
  );
}
