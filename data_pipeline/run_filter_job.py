"""Launch filter_job.py on Hugging Face Jobs, one job per year running in parallel.

Usage (from the project root, after `hf auth login`):
    python -m data_pipeline.run_filter_job 2020 2021 2022 2023 2024 2025
"""

import sys
from pathlib import Path

from huggingface_hub import Volume, get_token, run_uv_job

SCRIPT = Path(__file__).with_name("filter_job.py")

def main() -> None:
    years = sys.argv[1:]

    if not years:
        sys.exit("Usage: python -m data_pipeline.run_filter_job YEAR [YEAR ...]")

    token = get_token()

    if token is None:
        sys.exit("No Hugging Face token found. Run `hf auth login` first.")

    for year in years:
        job = run_uv_job(
            str(SCRIPT),
            script_args = [year],
            flavor = "cpu-upgrade",
            timeout = "4h",
            secrets = {"HF_TOKEN": token},
            volumes = [
                Volume(
                    type = "dataset",
                    source = "Lichess/standard-chess-games",
                    mount_path = "/lichess",
                    read_only = True,
                )
            ],
        )
        print(f"{year}: started job {job.id}  (logs: hf jobs logs {job.id})")

    print("Check all jobs with: hf jobs ps -a")

if __name__ == "__main__":
    main()