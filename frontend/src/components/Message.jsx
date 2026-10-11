import SourceList from "./SourceList.jsx";

export default function Message({ role, content, sources }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap ${
          isUser ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-800"
        }`}
      >
        {content || (!isUser ? "…" : "")}
        {!isUser && <SourceList sources={sources} />}
      </div>
    </div>
  );
}
