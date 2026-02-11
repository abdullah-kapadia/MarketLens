from fastapi import FastAPI
from fastapi.responses import FileResponse
from backend.schemas import AIRequest
from backend.ai_client import get_ai_report
from backend.pdf import generate_pdf

app = FastAPI(title="Market Lens Backend")

ALLOWED_SYMBOLS = {"OGDC", "PSO", "TRG", "KSE100"}

@app.post("/generate-report")
def generate_report(req: AIRequest):
    ai_data = get_ai_report(req.symbol)
    
    pdf_path = generate_pdf(
        symbol=ai_data["symbol"],
        headline=ai_data["headline"],
        chart_path=ai_data["chart_path"],
        commentary=ai_data["commentary"]
    )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{req.symbol}_Technical_Report.pdf"
    )