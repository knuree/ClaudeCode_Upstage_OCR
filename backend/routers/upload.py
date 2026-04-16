from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.services import ocr_service, storage_service

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload")
async def upload_receipt(file: UploadFile = File(...)):
    """영수증 업로드 → OCR 파싱 → 파싱 결과 반환 (저장은 /expenses POST로 분리)"""
    # 파일 형식 검증
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. (허용: JPG, PNG, PDF) 수신: {file.content_type}",
        )

    file_bytes = await file.read()

    # 파일 크기 검증
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기가 10MB를 초과합니다.")

    # OCR 파싱
    try:
        parsed = ocr_service.parse_receipt(file_bytes, file.content_type)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"영수증 파싱에 실패했습니다. 이미지를 확인하고 다시 시도해 주세요. ({e})",
        )

    # UUID·created_at 부여 후 저장
    saved = storage_service.append_expense(parsed)
    return saved
