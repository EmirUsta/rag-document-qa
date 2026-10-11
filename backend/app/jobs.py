import itertools
import threading
from datetime import datetime, timezone


class JobStore:

    def __init__(self):
        self._lock = threading.Lock()
        self._jobs: dict[str, dict] = {}
        self._counter = itertools.count()

    def create(self, job_id: str, filename: str) -> None:
        with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "status": "queued",
                "stage": "sırada",
                "progress_percent": 0,
                "filename": filename,
                "error": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "order": next(self._counter),
            }

    def update(self, job_id: str, **fields) -> None:
        with self._lock:
            self._jobs.setdefault(job_id, {}).update(fields)

    def get(self, job_id: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return dict(job) if job is not None else None

    def list_all(self) -> list[dict]:
        with self._lock:
            jobs = [dict(j) for j in self._jobs.values()]
        return sorted(jobs, key=lambda j: j["order"])


job_store = JobStore()
