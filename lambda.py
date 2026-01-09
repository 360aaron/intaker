import boto3
import io
from typing import List, Tuple, Optional

import polars as pl

CSV_SCHEMA = pl.Schema({
    "id": pl.Int64,
    "name": pl.Utf8,
    "amount": pl.Float64,
})

def is_utf8_encoding(raw_bytes: bytes) -> bool:
    """Check that file is UTF-8 encoded."""
    try:
        raw_bytes.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def is_non_empty(raw_bytes: bytes) -> bool:
    """Check that file is not empty (after stripping whitespace)."""
    return len(raw_bytes.strip()) > 0


def is_expected_format(filename: str) -> str:
    """Check that file is in expected format (CSV)."""
    if filename.endswith(".csv"):
        return True
    return False


def is_expected_schema(
        df: pl.DataFrame, schema: pl.Schema
    ) -> Tuple[bool, Optional[str]]:
    """Check that incomding data matches expected schema."""
    try:
        df = df.cast(CSV_SCHEMA)
    except Exception as e:
        return False, str(e)
    return True, None


def handler(event, context):
    """AWS Lambda handler function."""
    filename = event.get("filename", None)
    file_bytes: List[int] = event["file_bytes"]
    file_content = bytes(file_bytes)
    if not is_expected_format(filename):
        return {"statusCode": 400, "body": "Only CSV files are accepted."}
    if not is_non_empty(file_content):
        return {"statusCode": 400, "body": "File is empty."}
    if not is_utf8_encoding(file_content):
        return {"statusCode": 400, "body": "File encoding is not UTF-8."}
    try:
        csv_text = file_content.decode("utf-8")
        df = pl.read_csv(io.StringIO(csv_text))
    except Exception as e:
        return {"statusCode": 400, "body": f"Error reading CSV: {str(e)}"}
    valid_schema, error_msg = is_expected_schema(df, CSV_SCHEMA)
    if not valid_schema:
        return {"statusCode": 400, "body": f"Schema validation failed: {error_msg}"}
    try:
        s3_client = boto3.client("s3")
        s3_client.put_object(
            Bucket="g360-lower-glue-job-live-avail-producer",
            Key=f"intaker/{filename}",
            Body=file_content,
            ContentType="text/csv",
        )
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error uploading to S3: {str(e)}"
        }
    return {"statusCode": 200, "body": "File validated & uploaded."}
