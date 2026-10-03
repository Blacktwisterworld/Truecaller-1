import os
import gc
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

from config import HF_DATASET, HF_REPO_TYPE


# Dataset ki Parquet files
PARQUET_FILES = [
    f"idx_phone.{i}.parquet"
    for i in range(32)
]


def search_number(number):
    number = str(number).strip()

    for filename in PARQUET_FILES:
        local_file = None
        parquet_file = None

        try:
            print(f"Searching: {filename}")

            # Sirf current file download/cache hogi
            local_file = hf_hub_download(
                repo_id=HF_DATASET,
                filename=filename,
                repo_type=HF_REPO_TYPE,
            )

            parquet_file = pq.ParquetFile(local_file)

            # Row groups ko bhi ek-ek karke process karenge
            for batch in parquet_file.iter_batches(
                columns=[
                    "Number",
                    "Name",
                    "Address",
                    "Email",
                    "Gender",
                    "Carrier",
                ],
                batch_size=10000,
            ):
                data = batch.to_pydict()

                numbers = data["Number"]

                for index, value in enumerate(numbers):
                    if str(value).strip() == number:
                        result = {
                            "Number": value,
                            "Name": data["Name"][index],
                            "Address": data["Address"][index],
                            "Email": data["Email"][index],
                            "Gender": data["Gender"][index],
                            "Carrier": data["Carrier"][index],
                        }

                        del data
                        del batch
                        gc.collect()

                        return result

                del data
                del batch
                gc.collect()

        except Exception as e:
            print(f"Error in {filename}: {e}")

        finally:
            parquet_file = None
            gc.collect()

    return None
