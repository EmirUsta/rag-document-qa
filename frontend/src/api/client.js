import axios from "axios";

export const api = axios.create({ baseURL: "/api" });

export function uploadDocuments(files, onUploadProgress) {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  return api.post("/documents", form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress,
  });
}

export function getJobStatus(jobId) {
  return api.get(`/documents/jobs/${jobId}`);
}

export function listJobs() {
  return api.get("/documents/jobs");
}

export function listDocuments() {
  return api.get("/documents");
}

export function deleteDocument(id) {
  return api.delete(`/documents/${id}`);
}

export function getChatHistory(sessionId) {
  return api.get("/chat/history", { params: { session_id: sessionId } });
}

export function resetChatHistory(sessionId) {
  return api.delete("/chat/history", { params: { session_id: sessionId } });
}

export async function streamChat(sessionId, message, onEvent) {
  const resp = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Session-Id": sessionId,
    },
    body: JSON.stringify({ session_id: sessionId, message }),
  });

  if (!resp.ok || !resp.body) {
    throw new Error(`Sohbet isteği başarısız: ${resp.status}`);
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const lines = buf.split("\n");
    buf = lines.pop();
    for (const line of lines) {
      if (line.trim()) onEvent(JSON.parse(line));
    }
  }
  if (buf.trim()) onEvent(JSON.parse(buf));
}
