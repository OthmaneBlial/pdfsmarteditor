import json
import os
import uuid
import zipfile
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from api.deps import TEMP_DIR
from api.utils import persist_upload_file
from pdfsmarteditor.core.converter import PDFConverter
from pdfsmarteditor.core.manipulator import PDFManipulator

router = APIRouter(prefix="/api/tools", tags=["tools"])

# MIME Types
PDF_MIME = {"application/pdf"}
IMG_MIME = {"image/png", "image/jpeg", "image/jpg"}
HTML_MIME = {"text/html", "application/xhtml+xml"}
DOC_MIME = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}
PPT_MIME = {
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}
EXCEL_MIME = {
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


@router.post("/merge")
async def merge_documents(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 documents required")
    paths = [await persist_upload_file(f, PDF_MIME, "merge_") for f in files]
    out_path = os.path.join(TEMP_DIR, f"merged_{uuid.uuid4()}.pdf")
    PDFManipulator().merge_pdfs(paths, out_path)
    return FileResponse(out_path, filename="merged.pdf", media_type="application/pdf")


@router.post("/split")
async def split_document(file: UploadFile = File(...), page_ranges: str = Form(...)):
    path = await persist_upload_file(file, PDF_MIME, "split_")
    ranges = [r.strip() for r in page_ranges.split(",")]
    out_files = PDFManipulator().split_pdf(path, ranges, TEMP_DIR)

    if len(out_files) == 1:
        return FileResponse(
            out_files[0],
            filename=os.path.basename(out_files[0]),
            media_type="application/pdf",
        )

    zip_path = os.path.join(TEMP_DIR, f"split_{uuid.uuid4()}.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for f in out_files:
            zipf.write(f, os.path.basename(f))
    return FileResponse(
        zip_path, filename="split_files.zip", media_type="application/zip"
    )


@router.post("/compress")
async def compress_document(file: UploadFile = File(...), level: int = Form(4)):
    path = await persist_upload_file(file, PDF_MIME, "compress_")
    out_path = os.path.join(TEMP_DIR, f"compressed_{uuid.uuid4()}.pdf")
    PDFManipulator().compress_pdf(path, out_path, level)
    return FileResponse(
        out_path, filename="compressed.pdf", media_type="application/pdf"
    )


@router.post("/pdf-to-word")
async def pdf_to_word(file: UploadFile = File(...)):
    path = await persist_upload_file(file, PDF_MIME, "p2w_")
    out_path = os.path.join(TEMP_DIR, f"conv_{uuid.uuid4()}.docx")
    PDFConverter().pdf_to_word(path, out_path)
    return FileResponse(
        out_path,
        filename="converted.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.post("/pdf-to-ppt")
async def pdf_to_ppt(file: UploadFile = File(...)):
    path = await persist_upload_file(file, PDF_MIME, "p2p_")
    out_path = os.path.join(TEMP_DIR, f"conv_{uuid.uuid4()}.pptx")
    PDFConverter().pdf_to_ppt(path, out_path)
    return FileResponse(
        out_path,
        filename="converted.pptx",
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )


@router.post("/pdf-to-excel")
async def pdf_to_excel(file: UploadFile = File(...)):
    path = await persist_upload_file(file, PDF_MIME, "p2e_")
    out_path = os.path.join(TEMP_DIR, f"conv_{uuid.uuid4()}.xlsx")
    PDFConverter().pdf_to_excel(path, out_path)
    return FileResponse(
        out_path,
        filename="converted.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.post("/word-to-pdf")
async def word_to_pdf(file: UploadFile = File(...)):
    path = await persist_upload_file(file, DOC_MIME, "w2p_")
    out_path = PDFConverter().word_to_pdf(path, TEMP_DIR)
    return FileResponse(
        out_path, filename="converted.pdf", media_type="application/pdf"
    )


@router.post("/ppt-to-pdf")
async def ppt_to_pdf(file: UploadFile = File(...)):
    path = await persist_upload_file(file, PPT_MIME, "p2p_")
    out_path = PDFConverter().ppt_to_pdf(path, TEMP_DIR)
    return FileResponse(
        out_path, filename="converted.pdf", media_type="application/pdf"
    )


@router.post("/excel-to-pdf")
async def excel_to_pdf(file: UploadFile = File(...)):
    path = await persist_upload_file(file, EXCEL_MIME, "e2p_")
    out_path = PDFConverter().excel_to_pdf(path, TEMP_DIR)
    return FileResponse(
        out_path, filename="converted.pdf", media_type="application/pdf"
    )


@router.post("/pdf-to-jpg")
async def pdf_to_jpg(file: UploadFile = File(...)):
    path = await persist_upload_file(file, PDF_MIME, "p2j_")
    out_files = PDFConverter().pdf_to_jpg(path, TEMP_DIR)
    zip_path = os.path.join(TEMP_DIR, f"imgs_{uuid.uuid4()}.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for f in out_files:
            zipf.write(f, os.path.basename(f))
    return FileResponse(zip_path, filename="images.zip", media_type="application/zip")


@router.post("/img-to-pdf")
async def img_to_pdf(file: UploadFile = File(...)):
    path = await persist_upload_file(file, IMG_MIME, "i2p_")
    out_path = os.path.join(TEMP_DIR, f"conv_{uuid.uuid4()}.pdf")
    PDFConverter().jpg_to_pdf([path], out_path)
    return FileResponse(
        out_path, filename="converted.pdf", media_type="application/pdf"
    )


@router.post("/sign")
async def sign_pdf(
    file: UploadFile = File(...),
    signature_file: UploadFile = File(...),
    page_num: int = Form(...),
    x: int = Form(...),
    y: int = Form(...),
    width: int = Form(...),
    height: int = Form(50),
):
    doc_path = await persist_upload_file(file, PDF_MIME, "sign_d_")
    sig_path = await persist_upload_file(signature_file, IMG_MIME, "sign_s_")
    out_path = os.path.join(TEMP_DIR, f"signed_{uuid.uuid4()}.pdf")
    PDFManipulator().add_signature(
        doc_path, sig_path, out_path, page_num, x, y, width, height
    )
    return FileResponse(out_path, filename="signed.pdf", media_type="application/pdf")


@router.post("/watermark")
async def watermark_pdf(
    file: UploadFile = File(...),
    text: str = Form(...),
    opacity: float = Form(0.3),
    rotation: int = Form(45),
    font_size: int = Form(50),
    color_hex: str = Form("#000000"),
):
    path = await persist_upload_file(file, PDF_MIME, "wm_")
    out_path = os.path.join(TEMP_DIR, f"wm_{uuid.uuid4()}.pdf")
    color = tuple(int(color_hex.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4))
    PDFManipulator().add_watermark(
        path, text, out_path, opacity, rotation, font_size, color
    )
    return FileResponse(
        out_path, filename="watermarked.pdf", media_type="application/pdf"
    )


@router.post("/rotate")
async def rotate_pdf(
    file: UploadFile = File(...),
    rotation: int = Form(...),
    page_nums: Optional[str] = Form(None),
):
    path = await persist_upload_file(file, PDF_MIME, "rot_")
    out_path = os.path.join(TEMP_DIR, f"rot_{uuid.uuid4()}.pdf")
    nums = json.loads(page_nums) if page_nums else None
    PDFManipulator().rotate_pdf(path, out_path, rotation, nums)
    return FileResponse(out_path, filename="rotated.pdf", media_type="application/pdf")


@router.post("/html-to-pdf")
async def html_to_pdf(file: UploadFile = File(...)):
    path = await persist_upload_file(file, HTML_MIME, "h2p_")
    out_path = os.path.join(TEMP_DIR, f"conv_{uuid.uuid4()}.pdf")
    PDFConverter().html_to_pdf(path, out_path)
    return FileResponse(
        out_path, filename="converted.pdf", media_type="application/pdf"
    )


@router.post("/unlock")
async def unlock_pdf(file: UploadFile = File(...), password: str = Form(...)):
    path = await persist_upload_file(file, PDF_MIME, "unl_")
    out_path = os.path.join(TEMP_DIR, f"unl_{uuid.uuid4()}.pdf")
    try:
        PDFManipulator().unlock_pdf(path, password, out_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return FileResponse(out_path, filename="unlocked.pdf", media_type="application/pdf")


@router.post("/protect")
async def protect_pdf(file: UploadFile = File(...), password: str = Form(...)):
    path = await persist_upload_file(file, PDF_MIME, "pro_")
    out_path = os.path.join(TEMP_DIR, f"pro_{uuid.uuid4()}.pdf")
    PDFManipulator().protect_pdf(path, password, out_path)
    return FileResponse(
        out_path, filename="protected.pdf", media_type="application/pdf"
    )


@router.post("/organize")
async def organize_pdf(file: UploadFile = File(...), page_order: str = Form(...)):
    path = await persist_upload_file(file, PDF_MIME, "org_")
    order = json.loads(page_order)
    out_path = os.path.join(TEMP_DIR, f"org_{uuid.uuid4()}.pdf")
    PDFManipulator().organize_pdf(path, order, out_path)
    return FileResponse(
        out_path, filename="organized.pdf", media_type="application/pdf"
    )


@router.post("/pdf-to-pdfa")
async def pdf_to_pdfa(file: UploadFile = File(...)):
    path = await persist_upload_file(file, PDF_MIME, "pdfa_")
    out_path = os.path.join(TEMP_DIR, f"pdfa_{uuid.uuid4()}.pdf")
    PDFConverter().pdf_to_pdfa(path, out_path)
    return FileResponse(out_path, filename="pdfa.pdf", media_type="application/pdf")


@router.post("/repair")
async def repair_pdf(file: UploadFile = File(...)):
    path = await persist_upload_file(file, PDF_MIME, "rep_")
    out_path = os.path.join(TEMP_DIR, f"rep_{uuid.uuid4()}.pdf")
    try:
        PDFManipulator().repair_pdf(path, out_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return FileResponse(out_path, filename="repaired.pdf", media_type="application/pdf")


@router.post("/page-numbers")
async def add_page_numbers(
    file: UploadFile = File(...), position: str = Form("bottom-center")
):
    path = await persist_upload_file(file, PDF_MIME, "pnum_")
    out_path = os.path.join(TEMP_DIR, f"num_{uuid.uuid4()}.pdf")
    PDFManipulator().add_page_numbers(path, out_path, position)
    return FileResponse(out_path, filename="numbered.pdf", media_type="application/pdf")


@router.post("/scan-to-pdf")
async def scan_to_pdf(files: List[UploadFile] = File(...), enhance: bool = Form(True)):
    paths = [await persist_upload_file(f, IMG_MIME, "scan_") for f in files]
    out_path = os.path.join(TEMP_DIR, f"scan_{uuid.uuid4()}.pdf")
    PDFConverter().scan_to_pdf(paths, out_path, enhance)
    return FileResponse(out_path, filename="scanned.pdf", media_type="application/pdf")


@router.post("/ocr")
async def ocr_pdf(file: UploadFile = File(...), lang: str = Form("eng")):
    path = await persist_upload_file(file, PDF_MIME, "ocr_")
    out_path = os.path.join(TEMP_DIR, f"ocr_{uuid.uuid4()}.pdf")
    PDFConverter().ocr_pdf(path, out_path, lang)
    return FileResponse(
        out_path, filename="ocr_result.pdf", media_type="application/pdf"
    )


@router.post("/compare")
async def compare_pdfs(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    p1 = await persist_upload_file(file1, PDF_MIME, "cmp1_")
    p2 = await persist_upload_file(file2, PDF_MIME, "cmp2_")
    out_path = os.path.join(TEMP_DIR, f"cmp_{uuid.uuid4()}.pdf")
    PDFManipulator().compare_pdfs(p1, p2, out_path)
    return FileResponse(
        out_path, filename="comparison_diff.pdf", media_type="application/pdf"
    )
