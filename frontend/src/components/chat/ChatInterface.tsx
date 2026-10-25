import { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../services/api';
import { Conversation, ConversationMessage, ChatRequest, ChatResponse } from '../../types';
import { clsx } from 'clsx';
import { Send, Plus, Trash2, ChevronLeft, ChevronRight, Loader2, Bot, User, FileText, Link2, AlertTriangle, CheckCircle, XCircle, HelpCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface ChatInterfaceProps {
  initialConversationId?: number;
}

export function ChatInterface({ initialConversationId }: ChatInterfaceProps) {
  const queryClient = useQueryClient();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(initialConversationId || null);
  const [showSidebar, setShowSidebar] = useState(true);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const { data: messagesData } = useQuery({
    queryKey: ['messages', activeConversationId],
    queryFn: () => api.getConversation(activeConversationId!),
    enabled: !!activeConversationId,
  });

  const messages = messagesData?.messages || [];

  const createConversationMutation = useMutation({
    mutationFn: (title: string) => api.createConversation(title),
    onSuccess: (newConversation) => {
      setConversations((prev) => [newConversation, ...prev]);
      setActiveConversationId(newConversation.id);
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });

  const sendMessageMutation = useMutation({
    mutationFn: (request: ChatRequest) => api.sendMessage(request.message, request.conversation_id),
    onSuccess: (response: ChatResponse) => {
      setIsLoading(false);
      if (activeConversationId) {
        queryClient.invalidateQueries({ queryKey: ['messages', activeConversationId] });
      }
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
    onError: () => {
      setIsLoading(false);
    },
  });

  const loadConversations = async () => {
    try {
      const data = await api.getConversations();
      setConversations(data);
      if (!activeConversationId && data.length > 0 && !initialConversationId) {
        setActiveConversationId(data[0].id);
      }
    } catch (error) {
      console.error('Failed to load conversations', error);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const message = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    sendMessageMutation.mutate({ message, conversation_id: activeConversationId || undefined });
  };

  const handleNewConversation = () => {
    const title = prompt('Enter conversation title:') || 'New Conversation';
    createConversationMutation.mutate(title);
  };

  const handleDeleteConversation = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this conversation?')) {
      await api.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConversationId === id) {
        setActiveConversationId(conversations.find((c) => c.id !== id)?.id || null);
      }
    }
  };

  const renderMessageContent = (message: ConversationMessage) => {
    const citations = message.citations ? JSON.parse(message.citations) : [];
    const toolCalls = message.tool_calls ? JSON.parse(message.tool_calls) : [];
    
    return (
      <div className="prose prose-sm max-w-none">
        <div className="whitespace-pre-wrap">{message.content}</div>
        
        {toolCalls.length > 0 && (
          <details className="mt-2 text-xs text-gray-500">
            <summary className="cursor-pointer flex items-center gap-1">
              <HelpCircle className="w-4 h-4" />
              How this answer was produced
            </summary>
            <div className="mt-2 p-2 bg-gray-50 rounded text-left">
              <p className="font-medium mb-1">Tools called:</p>
              <ul className="list-disc list-inside space-y-1">
                {toolCalls.map((tc: any, i: number) => (
                  <li key={i}>{tc.tool}({JSON.stringify(tc.args)}) - {tc.result ? '✓' : '✗'}</li>
                ))}
              </ul>
              {citations.length > 0 && (
                <>
                  <p className="font-medium mt-2 mb-1">Sources:</p>
                  <ul className="list-disc list-inside space-y-1">
                    {citations.map((c: any, i: number) => (
                      <li key={i}>
                        <span className="font-mono">{c.type}:{c.reference || c.id}</span>
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          </details>
        )}

        {citations.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-100">
            <p className="text-xs font-medium text-gray-500 mb-1">Sources:</p>
            <div className="flex flex-wrap gap-1">
              {citations.map((c: any, i: number) => (
                <span
                  key={i}
                  className="px-2 py-1 text-xs bg-gray-100 rounded font-mono text-gray-700"
                  title={`${c.type}: ${c.reference || c.id}`}
                >
                  {c.type}:{c.reference || c.id}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Chat</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={handleNewConversation}
            className="btn-secondary text-sm"
            title="New Conversation"
          >
            <Plus className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="btn-secondary text-sm"
            title={showSidebar ? 'Hide conversations' : 'Show conversations'}
          >
            {showSidebar ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </button>
        </div>
      </div>

      <div className={clsx('flex-1 flex', showSidebar ? 'flex-row' : 'flex-col')}>
        {showSidebar && (
          <aside className="w-72 border-r border-gray-200 flex flex-col hidden lg:flex">
            <div className="p-3 border-b border-gray-200">
              <input
                type="text"
                placeholder="Search conversations..."
                className="input text-sm py-1"
              />
            </div>
            <div className="flex-1 overflow-y-auto">
              {conversations.length === 0 ? (
                <div className="p-4 text-center text-gray-500 text-sm">
                  No conversations yet. Click + to start.
                </div>
              ) : (
                <ul className="divide-y divide-gray-100">
                  {conversations.map((conv) => (
                    <li key={conv.id}>
                      <button
                        onClick={() => setActiveConversationId(conv.id)}
                        className={clsx(
                          'w-full text-left p-3 rounded-lg transition-colors flex items-center justify-between gap-2',
                          activeConversationId === conv.id
                            ? 'bg-primary-50 text-primary-700'
                            : 'hover:bg-gray-50 text-gray-700'
                        )}
                      >
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{conv.title}</p>
                          <p className="text-xs text-gray-500 truncate">
                            {formatDistanceToNow(new Date(conv.updated_at), { addSuffix: true })}
                          </p>
                        </div>
                        <button
                          onClick={(e) => handleDeleteConversation(conv.id, e)}
                          className="text-gray-400 hover:text-red-500 p-1"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </aside>
        )}

        <div className="flex-1 flex flex-col min-w-0">
          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <Bot className="w-12 h-12 mb-4 opacity-50" />
                <p className="text-lg font-medium text-gray-500">Welcome to EnterpriseOps Copilot</p>
                <p className="text-sm text-gray-400 mt-1 max-w-md text-center">
                  Ask questions about purchase orders, inventory, suppliers, invoices, and more.
                </p>
                <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
                  {[
                    'Which purchase orders are awaiting approval?',
                    'What products are below reorder level?',
                    'Show me overdue deliveries',
                    'Check invoice INV-2002 for discrepancies',
                  ].map((suggestion, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        setInputMessage(suggestion);
                        handleSendMessage(new Event('submit'));
                      }}
                      className="p-2 text-left bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={clsx(
                    'flex gap-3',
                    message.role === 'user' ? 'flex-row-reverse' : ''
                  )}
                >
                  <div
                    className={clsx(
                      'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
                      message.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : message.role === 'assistant'
                        ? 'bg-gray-100 text-gray-600'
                        : 'bg-yellow-100 text-yellow-600'
                    )}
                  >
                    {message.role === 'user' ? (
                      <User className="w-4 h-4" />
                    ) : message.role === 'assistant' ? (
                      <Bot className="w-4 h-4" />
                    ) : (
                      <AlertTriangle className="w-4 h-4" />
                    )}
                  </div>
                  <div
                    className={clsx(
                      'max-w-3xl px-4 py-2 rounded-2xl',
                      message.role === 'user'
                        ? 'bg-primary-600 text-white rounded-tr-sm'
                        : 'bg-white border border-gray-100 rounded-tl-sm shadow-sm'
                    )}
                  >
                    {renderMessageContent(message)}
                    <div className="mt-1 text-xs opacity-60 text-right">
                      {formatDistanceToNow(new Date(message.created_at), { addSuffix: true })}
                    </div>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-200 bg-white">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask about procurement, inventory, suppliers, invoices..."
                className="input flex-1"
                disabled={isLoading}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage(e)}
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || isLoading}
                className="btn-primary px-6"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Press Enter to send, Shift+Enter for new line. Answers are grounded in your business data with citations.
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}