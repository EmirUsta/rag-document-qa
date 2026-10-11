import { useEffect, useRef, useState } from "react";
import { resetChatHistory, streamChat } from "../api/client";
import Message from "./Message.jsx";

export default function Chat({ sessionId, initialMessages }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    setMessages(
      initialMessages.map((m) => ({
        role: m.role === "human" ? "user" : "assistant",
        content: m.content,
        sources: [],
      }))
    );
  }, [initialMessages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    const question = input.trim();
    if (!question || sending) return;

    setInput("");
    setSending(true);
    setMessages((prev) => [
      ...prev,
      { role: "user", content: question, sources: [] },
      { role: "assistant", content: "", sources: [] },
    ]);

    try {
      await streamChat(sessionId, question, (event) => {
        if (event.type === "token") {
          setMessages((prev) => {
            const next = [...prev];
            const last = next[next.length - 1];
            next[next.length - 1] = { ...last, content: last.content + event.content };
            return next;
          });
        } else if (event.type === "done") {
          setMessages((prev) => {
            const next = [...prev];
            const last = next[next.length - 1];
            next[next.length - 1] = { ...last, sources: event.sources || [] };
            return next;
          });
        }
      });
    } catch (err) {
      setMessages((prev) => {
        const next = [...prev];
        next[next.length - 1] = {
          role: "assistant",
          content: "Bir hata oluştu, lütfen tekrar deneyin.",
          sources: [],
        };
        return next;
      });
    } finally {
      setSending(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  async function handleNewChat() {
    if (sending) return;
    try {
      await resetChatHistory(sessionId);
    } catch {
    }
    setMessages([]);
  }

  return (
    <div className="flex flex-col h-[70vh] bg-white rounded-lg border border-gray-200">
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200">
        <span className="text-sm font-semibold text-gray-800">Sohbet</span>
        <button
          onClick={handleNewChat}
          disabled={sending}
          className="text-xs text-gray-500 hover:text-red-600 disabled:opacity-50"
        >
          Yeni Sohbet
        </button>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <p className="text-sm text-gray-400 text-center mt-8">
            Yüklenen dokümanlarla ilgili bir soru sorarak başlayın.
          </p>
        )}
        {messages.map((m, i) => (
          <Message key={i} role={m.role} content={m.content} sources={m.sources} />
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-gray-200 p-3 flex gap-2">
        <textarea
          className="flex-1 resize-none border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={2}
          placeholder="Sorunuzu yazın..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={sending}
        />
        <button
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md disabled:opacity-50"
          onClick={handleSend}
          disabled={sending || !input.trim()}
        >
          Gönder
        </button>
      </div>
    </div>
  );
}
