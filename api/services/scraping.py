import os
import subprocess
import uuid
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import threading
import logging

from api.models.papers import ScrapingRequest, ScrapingStatus
from api.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScrapingService:
    def __init__(self):
        self.jobs: Dict[str, ScrapingStatus] = {}
        self.job_processes: Dict[str, subprocess.Popen] = {}

        # Create jobs directory if it doesn't exist
        self.jobs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "jobs")
        os.makedirs(self.jobs_dir, exist_ok=True)

        # Load existing jobs from disk
        self._load_jobs()

    def _load_jobs(self):
        """Load existing jobs from the jobs directory"""
        if os.path.exists(self.jobs_dir):
            for filename in os.listdir(self.jobs_dir):
                if filename.endswith(".json"):
                    try:
                        job_id = filename.replace(".json", "")
                        with open(os.path.join(self.jobs_dir, filename), "r") as f:
                            job_data = json.load(f)

                        # Convert string dates to datetime objects
                        job_data["created_at"] = datetime.fromisoformat(job_data["created_at"])
                        if job_data.get("updated_at"):
                            job_data["updated_at"] = datetime.fromisoformat(job_data["updated_at"])
                        if job_data.get("completed_at"):
                            job_data["completed_at"] = datetime.fromisoformat(job_data["completed_at"])

                        # Create ScrapingStatus object
                        self.jobs[job_id] = ScrapingStatus(**job_data)
                    except Exception as e:
                        logger.error(f"Error loading job {filename}: {e}")

    def _save_job(self, job_id: str):
        """Save job data to disk"""
        job = self.jobs[job_id]
        job_data = job.dict()

        # Convert datetime objects to strings
        job_data["created_at"] = job_data["created_at"].isoformat()
        if job_data.get("updated_at"):
            job_data["updated_at"] = job_data["updated_at"].isoformat()
        if job_data.get("completed_at"):
            job_data["completed_at"] = job_data["completed_at"].isoformat()

        with open(os.path.join(self.jobs_dir, f"{job_id}.json"), "w") as f:
            json.dump(job_data, f, indent=2)

    def create_job(self, request: ScrapingRequest) -> str:
        """Create a new scraping job"""
        job_id = str(uuid.uuid4())
        job = ScrapingStatus(
            job_id=job_id,
            status="created",
            created_at=datetime.now(),
            request=request,
            progress=0.0,
            total_items=0,
            processed_items=0
        )
        self.jobs[job_id] = job
        self._save_job(job_id)
        return job_id

    def run_scraping_job(self, job_id: str):
        """Run the scraping job using the run_scraper.py script"""
        if job_id not in self.jobs:
            logger.error(f"Job {job_id} not found")
            return

        job = self.jobs[job_id]
        job.status = "running"
        job.updated_at = datetime.now()
        self._save_job(job_id)

        try:
            # Prepare command to run the scraper script
            script_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "scripts",
                "run_scraper.py"
            )

            # Convert request to command line arguments
            cmd = [
                "python", script_path,
                "--query", job.request.query,
                "--max-results", str(job.request.max_results),
                "--job-id", job_id
            ]

            if job.request.categories:
                cmd.extend(["--categories", ",".join(job.request.categories)])

            if job.request.date_from:
                cmd.extend(["--date-from", job.request.date_from])

            if job.request.date_to:
                cmd.extend(["--date-to", job.request.date_to])

            if job.request.preprocess:
                cmd.append("--preprocess")

            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            self.job_processes[job_id] = process

            # Start a thread to monitor the process
            monitor_thread = threading.Thread(
                target=self._monitor_job_process,
                args=(job_id, process)
            )
            monitor_thread.daemon = True
            monitor_thread.start()

        except Exception as e:
            logger.error(f"Error starting job {job_id}: {e}")
            job.status = "failed"
            job.error = str(e)
            job.updated_at = datetime.now()
            self._save_job(job_id)

    def _monitor_job_process(self, job_id: str, process: subprocess.Popen):
        """Monitor the scraping process and update job status"""
        job = self.jobs[job_id]

        # Read output lines
        for line in process.stdout:
            line = line.strip()
            if line.startswith("PROGRESS:"):
                try:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        progress_data = parts[1].strip()
                        if "/" in progress_data:
                            current, total = map(int, progress_data.split("/"))
                            job.processed_items = current
                            job.total_items = total
                            job.progress = (current / total) * 100 if total > 0 else 0
                            job.updated_at = datetime.now()
                            self._save_job(job_id)
                except Exception as e:
                    logger.error(f"Error parsing progress for job {job_id}: {e}")

            if line.startswith("RESULTS_FILE:"):
                try:
                    job.results_file = line.split(":", 1)[1].strip()
                except Exception as e:
                    logger.error(f"Error parsing results file for job {job_id}: {e}")

        # Process has finished
        process.wait()

        if process.returncode == 0:
            job.status = "completed"
        else:
            job.status = "failed"
            # Get error message from stderr
            error_output = process.stderr.read()
            job.error = error_output if error_output else f"Process exited with code {process.returncode}"

        job.updated_at = datetime.now()
        job.completed_at = datetime.now()
        job.progress = 100.0 if job.status == "completed" else job.progress
        self._save_job(job_id)

        # Remove process from tracked processes
        if job_id in self.job_processes:
            del self.job_processes[job_id]

    def get_job_status(self, job_id: str) -> Optional[ScrapingStatus]:
        """Get the status of a job"""
        return self.jobs.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        if job_id not in self.jobs:
            return False

        job = self.jobs[job_id]
        if job.status not in ["created", "running"]:
            return False

        # Terminate the process if it's running
        if job_id in self.job_processes:
            process = self.job_processes[job_id]
            try:
                process.terminate()
                process.wait(timeout=5)
            except Exception as e:
                logger.error(f"Error terminating job {job_id}: {e}")
                try:
                    process.kill()
                except:
                    pass

            del self.job_processes[job_id]

        job.status = "cancelled"
        job.updated_at = datetime.now()
        job.completed_at = datetime.now()
        self._save_job(job_id)

        return True

    def get_all_jobs(self, limit: int = 10, skip: int = 0, status: Optional[str] = None) -> List[ScrapingStatus]:
        """Get all jobs with optional filtering by status"""
        jobs = list(self.jobs.values())

        if status:
            jobs = [job for job in jobs if job.status == status]

        # Sort by created_at (newest first)
        jobs.sort(key=lambda x: x.created_at, reverse=True)

        # Apply pagination
        return jobs[skip:skip + limit]