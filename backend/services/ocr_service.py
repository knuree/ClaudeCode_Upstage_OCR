"""
OCR 서비스: Upstage Vision LLM + LangChain 연동

처리 흐름:
  업로드 파일 → 이미지 전처리(Base64) → LangChain Chain → 구조화 JSON 반환
"""

import base64
import io
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_upstage import ChatUpstage
from PIL import Image

SYSTEM_PROMPT = """당신은 영수증 OCR 전문가입니다.
이미지에서 아래 JSON 형식으로만 응답하세요. 다른 텍스트는 절대 포함하지 마세요.

{
  "store_name": "string",
  "receipt_date": "YYYY-MM-DD",
  "receipt_time": "HH:MM or null",
  "category": "식료품|외식|교통|쇼핑|의료|기타",
  "items": [{"name": "string", "quantity": 1, "unit_price": 0, "total_price": 0}],
  "subtotal": 0,
  "discount": 0,
  "tax": 0,
  "total_amount": 0,
  "payment_method": "string or null"
}

규칙:
- receipt_date 는 반드시 YYYY-MM-DD 형식
- category 는 위 6개 값 중 하나만 사용
- 숫자 필드는 정수(원화 기준), 알 수 없으면 0
- 알 수 없는 문자열 필드는 null
"""


def _image_to_base64(image_bytes: bytes, content_type: str) -> tuple[str, str]:
    """이미지 bytes → (base64 문자열, mime_type)"""
    if content_type == "application/pdf":
        from pdf2image import convert_from_bytes

        pages = convert_from_bytes(image_bytes, first_page=1, last_page=1)
        buf = io.BytesIO()
        pages[0].save(buf, format="JPEG")
        image_bytes = buf.getvalue()
        content_type = "image/jpeg"

    # 이미지 정규화 (RGBA → RGB 변환 등)
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return b64, "image/jpeg"


def parse_receipt(file_bytes: bytes, content_type: str) -> dict:
    """
    영수증 파일을 Upstage Vision LLM으로 파싱하여 구조화 JSON 반환.

    Args:
        file_bytes: 업로드된 파일의 raw bytes
        content_type: MIME 타입 (image/jpeg, image/png, application/pdf)

    Returns:
        파싱된 지출 정보 dict
    """
    b64, mime = _image_to_base64(file_bytes, content_type)

    llm = ChatUpstage(
        api_key=os.getenv("UPSTAGE_API_KEY"),
        model="solar-pro",  # vision 지원 모델
    )
    parser = JsonOutputParser()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=[
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64}"},
                },
                {"type": "text", "text": "이 영수증의 내용을 JSON으로 추출해 주세요."},
            ]
        ),
    ]

    chain = llm | parser
    result: dict = chain.invoke(messages)
    return result
