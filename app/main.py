import os

from fastapi import FastAPI, UploadFile
from pydantic import BaseModel

from app.gosuslugi import GosUslugi


app = FastAPI()

gosuslugi = GosUslugi()

class SignatureReport(BaseModel):
    is_valid: bool
    report: dict[str, str]
    holder_info: dict[str, str]
    holder_inn: str


@app.post("/verify-signature", response_model=SignatureReport)
async def verify_signature(file: UploadFile, signature: UploadFile):
    """
    Verify signature
    """
    try:
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as f:
            data = await file.read()
            f.write(data)

        sig_path = f"/tmp/{signature.filename}"
        with open(sig_path, "wb") as f:
            data = await signature.read()
            f.write(data)

        is_valid, report = gosuslugi.check_signature(file_path, sig_path)
        holder_info = report.pop("certificate_info", {})

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(sig_path):
            os.remove(sig_path)

    return SignatureReport(is_valid=is_valid, report=report, holder_info=holder_info, holder_inn=holder_info.get("ИННЮЛ"))
