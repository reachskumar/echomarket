from fastapi import APIRouter, Response
from reportlab.pdfgen import canvas
import io

router = APIRouter()

@router.post("/export/pdf")
async def export_pdf(data: dict):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    
    pdf.setFont("Helvetica", 12)
    y = 800

    pdf.drawString(100, y, f"EchoMarket Financial Report - {data.get('ticker', 'N/A')}")
    y -= 30

    for key, value in data.items():
        if key != "trend_image_base64":
            pdf.drawString(80, y, f"{key.capitalize()}: {value}")
            y -= 20
            if y < 50:
                pdf.showPage()
                y = 800

    pdf.save()
    buffer.seek(0)
    
    return Response(buffer.read(), media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename={data.get('ticker', 'report')}.pdf"})
