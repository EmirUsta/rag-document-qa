import { useEffect, useRef, useState } from "react";
import { getJobStatus, listJobs, uploadDocuments } from "../api/client";

function formatStage(stage) {
  const m = /^embedding (\d+)\/(\d+)$/.exec(stage || "");
  if (m) return `Embedding: ${m[1]}/${m[2]} parça`;
  return stage;
}

export default function Upload({ onUploaded }) {
  const [uploadPercent, setUploadPercent] = useState(null);
  const [jobs, setJobs] = useState([]);
  const inputRef = useRef(null);

  useEffect(() => {
    listJobs()
      .then((res) => {
        const restored = res.data.map((j) => ({ ...j, jobId: j.job_id }));
        setJobs(restored);
        restored
          .filter((j) => j.status !== "done" && j.status !== "error")
          .forEach((j) => pollJob(j.jobId, j.filename));
      })
      .catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function pollJob(jobId, filename) {
    const interval = setInterval(async () => {
      try {
        const res = await getJobStatus(jobId);
        const job = res.data;
        setJobs((prev) =>
          prev.map((j) => (j.jobId === jobId ? { ...j, ...job, filename } : j))
        );
        if (job.status === "done" || job.status === "error") {
          clearInterval(interval);
          onUploaded?.();
        }
      } catch {
        clearInterval(interval);
      }
    }, 1000);
  }

  async function handleFiles(e) {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    setUploadPercent(0);

    try {
      const res = await uploadDocuments(files, (progressEvent) => {
        if (progressEvent.total) {
          setUploadPercent(
            Math.round((progressEvent.loaded * 100) / progressEvent.total)
          );
        }
      });

      const jobIds = res.data.job_ids;
      const newJobs = jobIds.map((jobId, i) => ({
        jobId,
        filename: files[i]?.name || "dosya",
        stage: "sırada",
        progress_percent: 0,
        status: "queued",
      }));
      setJobs((prev) => [...prev, ...newJobs]);
      newJobs.forEach((j) => pollJob(j.jobId, j.filename));
    } catch (err) {
      alert(err.response?.data?.detail || "Yükleme başarısız oldu.");
    } finally {
      setUploadPercent(null);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 space-y-3">
      <h2 className="text-sm font-semibold text-gray-800">Doküman Yükle</h2>

      <input
        ref={inputRef}
        type="file"
        accept="application/pdf,.pdf"
        multiple
        onChange={handleFiles}
        className="block w-full text-sm text-gray-600 file:mr-3 file:py-2 file:px-3 file:rounded-md file:border-0 file:bg-blue-50 file:text-blue-700 file:text-sm"
      />

      {uploadPercent !== null && (
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${uploadPercent}%` }}
          />
        </div>
      )}

      {jobs.length > 0 && (
        <ul className="space-y-2">
          {jobs.map((j) => (
            <li key={j.jobId} className="text-sm">
              <div className="flex justify-between text-gray-700">
                <span className="truncate">{j.filename}</span>
                <span className="text-gray-500 shrink-0 ml-2">
                  {formatStage(j.stage)}
                  {j.status !== "done" && j.status !== "error"
                    ? ` (%${j.progress_percent || 0})`
                    : ""}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                <div
                  className={`h-1.5 rounded-full transition-all ${
                    j.status === "error" ? "bg-red-500" : "bg-green-500"
                  }`}
                  style={{ width: `${j.progress_percent || 0}%` }}
                />
              </div>
              {j.status === "error" && (
                <p className="text-xs text-red-500 mt-1">{j.error}</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
