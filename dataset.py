import gc
import duckdb

from huggingface_hub import hf_hub_download

from config import HF_DATASET, HF_REPO_TYPE


# Total 32 Parquet files
PARQUET_FILES = [
    f"idx_phone.{i}.parquet"
    for i in range(32)
]


def search_number(number, progress_callback=None):
    number = str(number).strip()

    for index, filename in enumerate(PARQUET_FILES, start=1):

        local_file = None
        con = None

        try:
            # Telegram par current file ka status
            if progress_callback:
                progress_callback(
                    f"📂 File {index}/32\n"
                    f"⏳ Searching {filename}..."
                )

            # Current Parquet file download/cache
            local_file = hf_hub_download(
                repo_id=HF_DATASET,
                filename=filename,
                repo_type=HF_REPO_TYPE,
            )

            # DuckDB connection
            con = duckdb.connect()

            # Sirf required columns read karo
            query = """
                SELECT
                    Number,
                    Name,
                    Address,
                    Email,
                    Gender,
                    Carrier
                FROM read_parquet(?)
                WHERE CAST(Number AS VARCHAR) = ?
                LIMIT 1
            """

            result = con.execute(
                query,
                [local_file, number]
            ).fetchone()

            # Match mil gaya
            if result:

                if progress_callback:
                    progress_callback(
                        f"📂 File {index}/32\n"
                        f"✅ Match found!\n"
                        f"📥 Loading result..."
                    )

                # Exact column mapping
                data = {
                    "Number": result[0],
                    "Name": result[1],
                    "Address": result[2],
                    "Email": result[3],
                    "Gender": result[4],
                    "Carrier": result[5],
                }

                return data

            # Is file me match nahi mila
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

            if con:
                try:
                    con.close()
                except Exception:
                    pass

            gc.collect()

    # 32 files search hone ke baad bhi match nahi mila
    return None
