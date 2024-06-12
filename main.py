from fastapi import FastAPI, HTTPException, status, File, UploadFile
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import qrcode
from io import BytesIO
from random import randrange
import base64
import os

app = FastAPI()

class QRCodeTextRequest(BaseModel):
    text: str

class QRCodeUserInfoRequest(BaseModel): 
    name: str
    surname: str
    company: str
    title: str
    phone: str
    email: str
    address: str

@app.post("/generate_qrcode_text", status_code=status.HTTP_201_CREATED)
async def generate_qrcode_text(qr_request: QRCodeTextRequest):
    text = qr_request.text
    img = qrcode.make(text)
    
    file_path = f"qrcode_text_{randrange(1000, 9999)}.png"
    img.save(file_path)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="QR code generation failed.")
    
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return StreamingResponse(img_byte_arr, media_type="image/png", headers={"Content-Disposition": f"inline; filename={file_path}"})

@app.post("/generate_qrcode_userinfo", status_code=status.HTTP_201_CREATED)
async def generate_qrcode_userinfo(qr_request: QRCodeUserInfoRequest):
    vcard = (
        f"BEGIN:VCARD\n"
        f"VERSION:3.0\n"
        f"N:{qr_request.surname};{qr_request.name}\n"
        f"FN:{qr_request.name} {qr_request.surname}\n"
        f"ORG:{qr_request.company}\n"
        f"TITLE:{qr_request.title}\n"
        f"EMAIL;PREF;INTERNET:{qr_request.email}\n"
        f"TEL;WORK;VOICE:{qr_request.phone}\n"
        f"ADR;WORK;PREF:;;{qr_request.address}\n"
        f"END:VCARD"
    )
    
    img = qrcode.make(vcard)
    
    file_path = f"qrcode_userinfo_{randrange(1000, 9999)}.png"
    img.save(file_path)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="QR code generation failed.")
    
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return StreamingResponse(img_byte_arr, media_type="image/png", headers={"Content-Disposition": f"inline; filename={file_path}"})


@app.post("/generate_qrcode_image", status_code=status.HTTP_201_CREATED)
async def generate_qrcode_image(file: UploadFile = File(...)):
    file_content = await file.read()
    
    base64_encoded_content = base64.b64encode(file_content).decode('utf-8')
    
    if len(base64_encoded_content) > 2953:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image is too large to encode as QR code.")
    
    img = qrcode.make(base64_encoded_content)
    
    file_path = f"qrcode_image_{randrange(1000, 9999)}.png"
    img.save(file_path)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="QR code generation failed.")
    
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return StreamingResponse(img_byte_arr, media_type="image/png", headers={"Content-Disposition": f"inline; filename={file_path}"})
