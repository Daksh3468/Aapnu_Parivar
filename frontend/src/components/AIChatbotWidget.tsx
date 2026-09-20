import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bot, X, Send, Sparkles, RefreshCw, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface Message {
  id: string;
  sender: 'bot' | 'user';
  text: string;
  actions?: Array<{ label: string; action_type: string; value: string }>;
  timestamp: string;
}

export const AIChatbotWidget: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome-1',
      sender: 'bot',
      text: 'Namaste! 🙏 I am **Aapnu Mitra (આપણું મિત્ર)**, your AI Welfare Assistant. Ask me anything about Gujarat welfare schemes, Family ID, household division splits, or eligibility!',
      actions: [
        { label: 'What schemes am I eligible for?', action_type: 'QUICK_QUERY', value: 'What schemes am I eligible for?' },
        { label: 'How do I split my family?', action_type: 'QUICK_QUERY', value: 'How do I split my family?' },
        { label: 'What is Gujarat Family ID?', action_type: 'QUICK_QUERY', value: 'What is Gujarat Family ID?' },
      ],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSendMessage = async (textToSend?: string) => {
    const queryText = (textToSend || inputQuery).trim();
    if (!queryText || loading) return;

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputQuery('');
    setLoading(true);

    try {
      const res = await fetch('/api/v1/chatbot/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: queryText,
          family_id: user?.family_id || undefined,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Assistant error');

      const botMsg: Message = {
        id: `bot-${Date.now()}`,
        sender: 'bot',
        text: data.reply,
        actions: data.suggested_actions || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'bot',
          text: 'Apologies, I am temporarily unable to reach the Welfare Assistant gateway. Please try again shortly.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleActionClick = (action: { label: string; action_type: string; value: string }) => {
    if (action.action_type === 'NAVIGATE') {
      setIsOpen(false);
      navigate(action.value);
    } else if (action.action_type === 'QUICK_QUERY') {
      handleSendMessage(action.value);
    }
  };

  return (
    <>
      {/* Floating Action Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-40 px-4 py-3 bg-slate-900 text-white rounded-full shadow-2xl hover:scale-105 transition-all duration-200 border-2 border-amber-500 flex items-center gap-2.5 group"
        title="Aapnu Mitra AI Assistant"
      >
        <div className="relative">
          <Bot className="w-6 h-6 text-amber-400 group-hover:rotate-12 transition-transform" />
          <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-500 rounded-full border-2 border-slate-900 animate-ping" />
          <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-500 rounded-full border-2 border-slate-900" />
        </div>
        <span className="font-black text-xs text-amber-400 tracking-wide pr-1 hidden sm:inline">Aapnu Mitra AI</span>
      </button>

      {/* Floating Chat Drawer Window */}
      {isOpen && (
        <div className="fixed bottom-20 right-4 sm:right-6 z-50 w-[calc(100vw-2rem)] sm:w-96 bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col h-[520px] animate-in fade-in slide-in-from-bottom-5 duration-200">
          
          {/* Header */}
          <div className="bg-slate-900 text-white p-4 relative border-b border-slate-800 shrink-0">
            <div className="gov-tricolor-stripe absolute top-0 left-0 right-0 h-1"></div>
            <div className="flex items-center justify-between pt-1">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-slate-900 text-amber-400 flex items-center justify-center border border-amber-500/40 font-bold shadow-sm">
                  <Sparkles className="w-5 h-5 text-amber-400" />
                </div>
                <div>
                  <h3 className="font-extrabold text-sm text-white flex items-center gap-1.5">
                    <span>Aapnu Mitra (આપણું મિત્ર)</span>
                  </h3>
                  <div className="flex items-center gap-1.5 text-[10px] text-emerald-400 font-medium">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    <span>AI Welfare Assistant • Gujarat Portal</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Messages Container */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-slate-50 text-xs">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'} space-y-1.5`}
              >
                <div
                  className={`max-w-[85%] p-3 rounded-2xl ${
                    msg.sender === 'user'
                      ? 'bg-slate-900 text-white rounded-tr-xs shadow-xs font-medium'
                      : 'bg-white text-slate-900 border border-slate-200 rounded-tl-xs shadow-xs font-normal'
                  }`}
                >
                  <p className="whitespace-pre-line leading-relaxed font-sans">{msg.text}</p>
                  
                  {/* Action Chips */}
                  {msg.actions && msg.actions.length > 0 && (
                    <div className="mt-2.5 pt-2 border-t border-slate-100 flex flex-wrap gap-1.5">
                      {msg.actions.map((act, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleActionClick(act)}
                          className="px-2.5 py-1 rounded-full bg-blue-50 hover:bg-blue-100 text-gov-navy border border-blue-200 text-[11px] font-bold flex items-center gap-1 transition-colors text-left"
                        >
                          <span>{act.label}</span>
                          <ArrowRight className="w-3 h-3 text-saffron shrink-0" />
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                <span className="text-[10px] text-slate-400 px-1 font-mono">{msg.timestamp}</span>
              </div>
            ))}

            {loading && (
              <div className="flex items-center gap-2 text-slate-500 text-xs bg-white p-3 rounded-2xl border border-slate-200 w-fit">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-gov-navy" />
                <span className="italic font-medium">Aapnu Mitra is thinking...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Footer Form */}
          <form
            onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
            className="p-3 bg-white border-t border-slate-200 flex items-center gap-2 shrink-0"
          >
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder="Ask about schemes, family ID, or split..."
              className="flex-1 px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-900 focus:outline-hidden focus:ring-2 focus:ring-gov-blue"
            />
            <button
              type="submit"
              disabled={!inputQuery.trim() || loading}
              className="p-2.5 bg-gov-navy hover:bg-slate-800 disabled:opacity-50 text-saffron rounded-xl transition-colors shadow-xs"
              title="Send Message"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>

        </div>
      )}
    </>
  );
};
