import os
import gc
import duckdb
from huggingface_hub import hf_hub_download

from config import HF_DATASET, HF_REPO_TYPE


PARQUET_FILES = [
    f"idx_phone.{i}.parquet"
    for i in range(32)
]


def search_number(number, progress_callback=None):
    number = str(number).strip()

    for index, filename in enumerate(PARQUET_FILES, start=1):
        local_file = None

        try:
            if progress_callback:
                progress_callback(
                    f"📂 File {index}/32\n"
                    f"⏳ Searching `{filename}`..."
                )

            local_file = hf_hub_download(
                repo_id=HF_DATASET,
                filename=filename,
                repo_type=HF_REPO_TYPE,
            )

            con = duckdb.connect()

            query = """
                SELECT *
                FROM read_parquet(?)
                WHERE CAST(Number AS VARCHAR) = ?
                LIMIT 1
            """

            result = con.execute(
                query,
                [local_file, number]
            ).fetchone()

            columns = [
                "Number",
                "Name",
                "Address",
                "Email",
                "Gender",
                "Carrier",
            ]

            con.close()

            if result:
                if progress_callback:
                    progress_callback(
                        f"📂 File {index}/32\n"
                        f"✅ Match found!"
                    )

                return dict(zip(columns, result))

            if progress_callback:
                progress_callback(
                    f"📂 File {index}/32\n"
                    f"❌ No data found\n\n"
                    f"➡️ Starting next file..."
                )

        except Exception as e:
            print(f"Error in {filename}: {e}")

            if progress_callback:
                progress_callback(
                    f"📂 File {index}/32\n"
                    f"⚠️ Error while searching\n\n"
                    f"➡️ Starting next file..."
                )

        finally:
            gc.collect()

    return None
