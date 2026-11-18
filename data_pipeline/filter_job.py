# /// script
# requires-python = ">=3.11"
# dependencies = ["polars", "huggingface_hub"]
# ///

"""Runs on Hugging Face Jobs: filter the Lichess dataset and push the result to a private repo.

The Lichess dataset is mounted read-only at /lichess, so files are read like local files.
Each filtered month is uploaded as data/YYYY-MM.parquet to <your-user>/lichess-filtered.

Arguments: one or more years, e.g. `2020 2021 2022`.
"""

import sys
import tempfile
from pathlib import Path

import polars as pl
from huggingface_hub import HfApi

SOURCE_DIR = Path("/lichess/data")
OUTPUT_REPO_NAME = "lichess-filtered"

MIN_BASE_TIME = 600
MIN_ELO = 2000
STRIP_COMMENTS = True
KEEP_COLUMNS = ["Site", "Result", "WhiteElo", "BlackElo", "BaseTime", "movetext"]

def filter_games(lf: pl.LazyFrame) -> pl.LazyFrame:
    lf = (
        lf.with_columns(
            pl.col("TimeControl").str.split("+").list.first()
              .cast(pl.Int32, strict = False).alias("BaseTime")
        )
        .filter(
            (pl.col("BaseTime") >= MIN_BASE_TIME)
            & (pl.col("WhiteElo") >= MIN_ELO)
            & (pl.col("BlackElo") >= MIN_ELO)
            & (pl.col("Termination") == "Normal")
            & pl.col("WhiteTitle").ne_missing("BOT")
            & pl.col("BlackTitle").ne_missing("BOT")
        )
    )

    if STRIP_COMMENTS:
        lf = lf.with_columns(
            pl.col("movetext")
            .str.replace_all(r"\{[^}]*\}", "")
            .str.replace_all(r"\d+\.\.\.", "")
            .str.replace_all(r"\s+", " ")
            .str.strip_chars()
        )

    return lf.select(KEEP_COLUMNS)

def main() -> None:
    years = sys.argv[1:]
    
    if not years:
        sys.exit("Usage: filter_job.py YEAR [YEAR ...]")

    api = HfApi()
    repo_id = f"{api.whoami()['name']}/{OUTPUT_REPO_NAME}"
    api.create_repo(repo_id, repo_type = "dataset", exist_ok = True)
    done = set(api.list_repo_files(repo_id, repo_type = "dataset"))

    for year in years:
        for month_dir in sorted(SOURCE_DIR.glob(f"year={year}/month=*")):
            month = month_dir.name.removeprefix("month=")
            target = f"data/{year}-{month}.parquet"

            if target in done:
                print(f"{year}-{month}: already done, skipping", flush = True)
                continue

            with tempfile.TemporaryDirectory() as tmp:
                local = Path(tmp) / "out.parquet"
                filter_games(pl.scan_parquet(month_dir / "*.parquet")).sink_parquet(local)
                kept = pl.scan_parquet(local).select(pl.len()).collect().item()
                api.upload_file(
                    path_or_fileobj = local,
                    path_in_repo = target,
                    repo_id = repo_id,
                    repo_type = "dataset",
                    commit_message = f"Add {year}-{month} ({kept} games)",
                )
            print(f"{year}-{month}: kept {kept} games, uploaded", flush = True)

if __name__ == "__main__":
    main()