import { useEffect, useState } from "react";
import { deleteDocument, listDocuments } from "../api/client";

export default function DocumentList({ refreshKey }) {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const res = await listDocuments();
      setDocs(res.data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [refreshKey]);

  async function handleDelete(docId) {
    if (!confirm("Bu dokümanı silmek istediğinize emin misiniz?")) return;
    await deleteDocument(docId);
    load();
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h2 className="text-sm font-semibold text-gray-800 mb-3">
        Yüklü Dokümanlar
      </h2>

      {loading && <p className="text-sm text-gray-400">Yükleniyor...</p>}
      {!loading && docs.length === 0 && (
        <p className="text-sm text-gray-400">Henüz doküman yüklenmedi.</p>
      )}

      {docs.length > 0 && (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b border-gray-100">
              <th className="py-1.5 font-medium">Dosya</th>
              <th className="py-1.5 font-medium">Sayfa</th>
              <th className="py-1.5 font-medium">Parça</th>
              <th className="py-1.5 font-medium">Tarih</th>
              <th className="py-1.5 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {docs.map((d) => (
              <tr key={d.doc_id} className="border-b border-gray-50">
                <td className="py-1.5 truncate max-w-[200px]">
                  {d.original_filename}
                </td>
                <td className="py-1.5">{d.page_count}</td>
                <td className="py-1.5">{d.chunk_count}</td>
                <td className="py-1.5 text-gray-500">
                  {new Date(d.uploaded_at).toLocaleString("tr-TR")}
                </td>
                <td className="py-1.5 text-right">
                  <button
                    className="text-red-500 hover:text-red-700 text-xs"
                    onClick={() => handleDelete(d.doc_id)}
                  >
                    Sil
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
