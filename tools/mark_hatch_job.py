from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: mark_hatch_job.py <run-dir> <job-id> <selected-source>")
        return 2

    run_dir = Path(sys.argv[1])
    job_id = sys.argv[2]
    source = Path(sys.argv[3])
    jobs_path = run_dir / "imagegen-jobs.json"

    manifest = json.loads(jobs_path.read_text(encoding="utf-8"))
    job = next(job for job in manifest["jobs"] if job["id"] == job_id)
    output_path = run_dir / job["output_path"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, output_path)

    if job_id == "base":
        canonical = run_dir / "references" / "canonical-base.png"
        canonical.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output_path, canonical)

    job["status"] = "complete"
    job["source_path"] = str(source)
    job["completed_at"] = datetime.now(timezone.utc).isoformat()
    jobs_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"completed {job_id}: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
