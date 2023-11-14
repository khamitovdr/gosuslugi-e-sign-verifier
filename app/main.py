from fastapi import FastAPI

from app.gosuslugi import GosUslugi

gosuslugi = GosUslugi()

# result, report = gosuslugi.check_signature("/home/hamit/Desktop/crypto/gosuslugi_selenium/file.pdf", "/home/hamit/Desktop/crypto/gosuslugi_selenium/file.pdf.sig")

app = FastAPI()


@app.get("/")
async def root(sig: bool):
    if sig:
        result, report = gosuslugi.check_signature("/home/app/web/app/data/file.pdf",
                                                   "/home/app/web/app/data/file.pdf.sig")
    else:
        result, report = gosuslugi.check_signature("/home/app/web/app/data/file.pdf",
                                                   "/home/app/web/app/data/wrong_file.pdf.sig")

    return result, report
