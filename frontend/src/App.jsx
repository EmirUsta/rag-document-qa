import { useEffect, useState } from "react";
import { getChatHistory } from "./api/client";
import Chat from "./components/Chat.jsx";
import DocumentList from "./components/DocumentList.jsx";
import Upload from "./components/Upload.jsx";
import { useSessionId } from "./hooks/useSession.js";

export default function App() {
  const sessionId = useSessionId();
  const [tab, setTab] = useState("chat");
  const [initialMessages, setInitialMessages] = useState([]);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    getChatHistory(sessionId)
      .then((res) => setInitialMessages(res.data))
      .catch(() => setInitialMessages([]));
  }, [sessionId]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-lg font-semibold text-gray-800">Doküman Asistanı</h1>
      </header>

      <nav className="bg-white border-b border-gray-200 px-6 flex gap-4">
        <button
          className={`py-3 px-2 border-b-2 text-sm font-medium ${
            tab === "chat"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700"
          }`}
          onClick={() => setTab("chat")}
        >
          Sohbet
        </button>
        <button
          className={`py-3 px-2 border-b-2 text-sm font-medium ${
            tab === "docs"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700"
          }`}
          onClick={() => setTab("docs")}
        >
          Dokümanlar
        </button>
      </nav>

      <main className="flex-1 max-w-3xl w-full mx-auto p-4">
        <div style={{ display: tab === "chat" ? "block" : "none" }}>
          <Chat sessionId={sessionId} initialMessages={initialMessages} />
        </div>
        <div
          className="space-y-6"
          style={{ display: tab === "docs" ? "block" : "none" }}
        >
          <Upload onUploaded={() => setRefreshKey((k) => k + 1)} />
          <DocumentList refreshKey={refreshKey} />
        </div>
      </main>
    </div>
  );
}
