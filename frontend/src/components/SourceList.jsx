export default function SourceList({ sources }) {
  if (!sources || sources.length === 0) return null;

  const text = sources
    .map((s) => `${s.file_name} (sayfa ${s.page_number ?? "?"})`)
    .join(", ");

  return <div className="text-xs text-gray-500 mt-1">Kaynaklar: {text}</div>;
}
