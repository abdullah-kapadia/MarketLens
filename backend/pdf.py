from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import date
import os

def generate_pdf(symbol, headline, chart_path, commentary):
    os.makedirs("outputs/reports", exist_ok=True)

    path = f"outputs/reports/{symbol}_{date.today()}.pdf"

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 40, "Weekly Technical Report | Pakistan Equities")

    c.setFont("Helvetica", 10)
    c.drawString(40, height - 60, f"Date: {date.today()}")
    c.drawString(40, height - 75, f"Stock: {symbol}")

    # Headline
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 105, headline)

    # Chart
    if os.path.exists(chart_path):
        c.drawImage(chart_path, 40, height - 430, width=520, height=300)

    # Commentary
    text = c.beginText(40, height - 460)
    text.setFont("Helvetica", 10)

    for line in commentary.split(". "):
        text.textLine(line.strip())

    c.drawText(text)

    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(40, 30, "For educational purposes only. Not investment advice.")

    c.save()
    return path