import gc
import time
import duckdb

from huggingface_hub import hf_hub_download

from config import HF_DATASET, HF_REPO_TYPE


# =========================
# Parquet Files
# =========================

PARQUET_FILES = [
    f"idx_phone.{i}.parquet"
    for i in range(32)
]


# =========================
# Search Number
# =========================

def search_number(number, progress_callback=None):

    number = str(number).strip()

    # Total search timer
    total_start = time.perf_counter()

    for index, filename in enumerate(PARQUET_FILES, start=1):

        file_start = time.perf_counter()

        local_file = None
        con = None

        try:

            # -------------------------
            # File starting
            # -------------------------

            if progress_callback:

                progress_callback(
                    f"📂 <b>File {index}/32</b>\n"
                    f"🔄 Opening <code>{filename}</code>..."
                )


            # -------------------------
            # Download / Cache File
            # -------------------------

            local_file = hf_hub_download(
                repo_id=HF_DATASET,
                filename=filename,
                repo_type=HF_REPO_TYPE,
            )


            # -------------------------
            # DuckDB
            # -------------------------

            con = duckdb.connect()


            if progress_callback:

                progress_callback(
                    f"📂 <b>File {index}/32</b>\n"
                    f"🔎 Searching Number...\n\n"
                    f"📄 <code>{filename}</code>"
                )


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


            # -------------------------
            # File Search Time
            # -------------------------

            file_time = time.perf_counter() - file_start


            # -------------------------
            # Match Found
            # -------------------------

            if result:

                total_time = (
                    time.perf_counter() - total_start
                )


                if progress_callback:

                    progress_callback(
                        f"📂 <b>File {index}/32</b>\n"
                        f"✅ <b>Match Found!</b>\n\n"
                        f"⏱️ File Time: "
                        f"{file_time:.2f}s"
                    )


                return {

                    "Number": result[0],

                    "Name": result[1],

                    "Address": result[2],

                    "Email": result[3],

                    "Gender": result[4],

                    "Carrier": result[5],

                    "matched_file": index,

                    "matched_filename": filename,

                    "file_time": file_time,

                    "search_time": total_time,

                    "files_checked": index,
                }


            # -------------------------
            # No Match
            # -------------------------

            if progress_callback:

                progress_callback(
                    f"📂 <b>File {index}/32</b>\n"
                    f"❌ No match\n\n"
                    f"⏱️ Time: {file_time:.2f}s\n"
                    f"➡️ Starting next file..."
                )


        except Exception as e:

            print(
                f"Error in {filename}: {e}"
            )


            if progress_callback:

                progress_callback(
                    f"📂 <b>File {index}/32</b>\n"
                    f"⚠️ Search error\n\n"
                    f"➡️ Starting next file..."
                )


        finally:

            if con:

                try:
                    con.close()

                except Exception:
                    pass


            gc.collect()


    # =========================
    # No Match in Any File
    # =========================

    total_time = (
        time.perf_counter() - total_start
    )


    return {

        "Number": number,

        "Name": None,

        "Address": None,

        "Email": None,

        "Gender": None,

        "Carrier": None,

        "matched_file": None,

        "matched_filename": None,

        "file_time": None,

        "search_time": total_time,

        "files_checked": len(PARQUET_FILES),

        "not_found": True,
    }
