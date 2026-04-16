# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Receipt Expense Tracker — a lightweight web app that uploads receipt images/PDFs, parses them via **Upstage Vision LLM** (through LangChain), and stores structured expense data in a JSON file. No database is used.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite 5 + TailwindCSS 3 + Axios |
| Backend | Python FastAPI 0.111 + LangChain 0.2 |
| OCR | Upstage `document-digitization-vision` via `langchain-upstage` |
| Image processing | Pillow + pdf2image (requires Poppler) |
| Storage | `backend/data/expenses.json` (JSON array, append-only) |
| Deployment | Vercel (frontend static build + backend serverless via Mangum) |

## Project Structure

```
receipt-tracker/
├── frontend/
│   ├── src/
│   │   ├── pages/          # Dashboard.jsx, UploadPage.jsx, ExpenseDetail.jsx
│   │   ├── components/     # DropZone, ParsePreview, ExpenseCard, SummaryCard,
│   │   │                   # FilterBar, Badge, Modal, Toast, ProgressBar, Header
│   │   └── api/axios.js    # Axios instance (baseURL from VITE_API_BASE_URL)
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── main.py             # FastAPI app entry point, CORS, router registration
│   ├── routers/
│   │   ├── upload.py       # POST /api/upload — file validation + OCR pipeline
│   │   ├── expenses.py     # GET/DELETE/PUT /api/expenses[/{id}]
│   │   └── summary.py      # GET /api/summary
│   ├── services/
│   │   ├── ocr_service.py  # LangChain Chain: image→Base64→ChatUpstage→JsonOutputParser
│   │   └── storage_service.py  # load/save/append expenses.json
│   ├── data/expenses.json  # Persisted expense records (JSON array)
│   └── requirements.txt
└── vercel.json
```

## Development Commands

### Backend

```bash
# Create and activate virtual environment
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
# or: venv\Scripts\activate    # Windows CMD

# Install dependencies
pip install -r backend/requirements.txt

# Run dev server (from project root)
uvicorn backend.main:app --reload
# Swagger UI: http://localhost:8000/docs
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
# App: http://localhost:5173

# Build for production
npm run build
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `UPSTAGE_API_KEY` | Yes | Upstage API key — backend only |
| `VITE_API_BASE_URL` | No | Backend base URL (defaults to `http://localhost:8000`) |
| `DATA_FILE_PATH` | No | Override path for expenses.json (auto-set to `/tmp/expenses.json` when `VERCEL=1`) |

Copy `.env` to the project root for local development. For Vercel, set `UPSTAGE_API_KEY` in the Vercel dashboard only.

## Architecture Notes

### OCR Pipeline

Upload flow: `POST /api/upload` → file validation (MIME type, 10MB limit) → `ocr_service.parse_receipt()` → PIL/pdf2image converts to Base64 → LangChain chain (`ChatUpstage` + `PromptTemplate` + `JsonOutputParser`) → structured JSON → UUID assigned → appended to `expenses.json` → returned to frontend.

The system prompt instructs the LLM to return **only** a JSON object matching the expense schema (no extra text). The category must be one of: `식료품|외식|교통|쇼핑|의료|기타`.

### Data Persistence on Vercel

Vercel serverless functions do not persist the file system between invocations. The MVP strategy is `localStorage` on the client as a fallback. For reliable persistence, deploy the backend to Railway/Render, or migrate to Vercel KV / Supabase.

### Expense JSON Schema

```json
{
  "id": "uuid-v4",
  "created_at": "ISO-8601 UTC",
  "store_name": "string",
  "receipt_date": "YYYY-MM-DD",
  "receipt_time": "HH:MM | null",
  "category": "식료품|외식|교통|쇼핑|의료|기타",
  "items": [{ "name": "", "quantity": 0, "unit_price": 0, "total_price": 0 }],
  "subtotal": 0,
  "discount": 0,
  "tax": 0,
  "total_amount": 0,
  "payment_method": "string | null",
  "raw_image_path": "uploads/..."
}
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/upload` | Upload receipt, run OCR, return parsed JSON |
| `GET` | `/api/expenses` | List expenses; query params: `from`, `to` (YYYY-MM-DD) |
| `DELETE` | `/api/expenses/{id}` | Delete by UUID; 404 if not found |
| `PUT` | `/api/expenses/{id}` | Partial update by UUID |
| `GET` | `/api/summary` | Totals + category breakdown; query param: `month` (YYYY-MM) |

### Frontend Routing

Three pages via React Router:
- `/` — Dashboard (SummaryCard + FilterBar + ExpenseCard grid)
- `/upload` — UploadPage (DropZone → ProgressBar → ParsePreview)
- `/expense/:id` — ExpenseDetail (ReceiptImage + EditForm + delete Modal)

### Styling Conventions

- **Primary color**: `indigo-600` / `indigo-700` for CTA buttons, links
- **Category badge colors**: green=식료품, orange=외식, blue=교통, purple=쇼핑, red=의료, gray=기타
- **Font**: Pretendard (CDN) with Noto Sans KR fallback
- Custom Tailwind animations (`slide-up`, `scale-in`, `fade-in`) must be registered in `tailwind.config.js` keyframes
- Layout max-width: `max-w-4xl mx-auto`; ExpenseList grid: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`
