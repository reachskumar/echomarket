# Export Routes
# These routes handle exporting analysis results to PDF and CSV formats.


import io
import csv
import logging
from fpdf import FPDF
from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

def export_to_pdf(analysis_data: dict, ticker: str) -> StreamingResponse:
    # Builds a PDF report from analysis data for the given ticker
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        
        pdf.cell(0, 10, f"Stock Analysis Report: {ticker}", ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("Arial", size=10)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.cell(0, 5, f"Generated on: {timestamp}", ln=True)
        pdf.ln(5)
        
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Current Price Information", ln=True)
        pdf.set_font("Arial", size=10)
        price = analysis_data.get("price", "N/A")
        if price and price != "N/A":
            pdf.cell(0, 6, f"Current Price: ${price:.2f}", ln=True)
        else:
            pdf.cell(0, 6, "Current Price: Not available", ln=True)
        pdf.ln(3)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Sentiment Analysis", ln=True)
        pdf.set_font("Arial", size=10)
        sentiment = analysis_data.get("sentiment", "N/A")
        confidence = analysis_data.get("confidence", 0)
        pdf.cell(0, 6, f"Overall Sentiment: {sentiment}", ln=True)
        pdf.cell(0, 6, f"Confidence Level: {confidence:.2f}", ln=True)
        pdf.ln(3)
        
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "AI Recommendation", ln=True)
        pdf.set_font("Arial", size=10)
        recommendation = analysis_data.get("recommendation", "N/A")
        insight = analysis_data.get("insight", "No insight available")
        pdf.cell(0, 6, f"Recommendation: {recommendation}", ln=True)
        pdf.ln(2)
        pdf.cell(0, 6, "Reasoning:", ln=True)
        
        insight_words = insight.split()
        line = ""
        for word in insight_words:
            if len(line + word + " ") < 80:
                line += word + " "
            else:
                pdf.cell(0, 5, line.strip(), ln=True)
                line = word + " "
        if line:
            pdf.cell(0, 5, line.strip(), ln=True)
        pdf.ln(5)
        
        
        if "summary" in analysis_data and analysis_data["summary"]:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "Executive Summary", ln=True)
            pdf.set_font("Arial", size=10)
            summary = analysis_data["summary"]
            summary_words = summary.split()
            line = ""
            for word in summary_words:
                if len(line + word + " ") < 80:
                    line += word + " "
                else:
                    pdf.cell(0, 5, line.strip(), ln=True)
                    line = word + " "
            if line:
                pdf.cell(0, 5, line.strip(), ln=True)
        
        # Add disclaimer
        pdf.ln(10)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 4, "Disclaimer: This analysis is for informational purposes only and should not be", ln=True)
        pdf.cell(0, 4, "considered as financial advice. Always consult with a qualified financial advisor", ln=True)
        pdf.cell(0, 4, "before making investment decisions.", ln=True)
        
        # Convert PDF to bytes and return as streaming response
        pdf_output = io.BytesIO()
        pdf_content = pdf.output(dest='S').encode('latin-1')
        pdf_output.write(pdf_content)
        pdf_output.seek(0)
        filename = f"stock_analysis_{ticker}_{datetime.now().strftime('%Y%m%d')}.pdf"
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        # Handle errors and log them
        logger.error(f"PDF export failed for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")


def export_to_csv(analysis_data: dict, ticker: str) -> StreamingResponse:
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Ticker", ticker])
        writer.writerow(["Analysis Date", datetime.now().strftime("%Y-%m-%d")])
        writer.writerow(["Analysis Time", datetime.now().strftime("%H:%M:%S")])
        writer.writerow(["", ""])
        writer.writerow(["Current Price", f"${analysis_data.get('price', 'N/A')}"])
        writer.writerow(["", ""])
        writer.writerow(["Sentiment", analysis_data.get("sentiment", "N/A")])
        writer.writerow(["Sentiment Confidence", analysis_data.get("confidence", "N/A")])
        writer.writerow(["", ""])
        writer.writerow(["Recommendation", analysis_data.get("recommendation", "N/A")])
        writer.writerow(["Reasoning", analysis_data.get("insight", "N/A")])
        writer.writerow(["", ""])
        trend = analysis_data.get("trend", {})
        if trend:
            writer.writerow(["Trend Direction", trend.get("direction", "N/A")])
            writer.writerow(["Trend Strength", trend.get("strength", "N/A")])
            writer.writerow(["Risk Level", trend.get("risk", "N/A")])
            writer.writerow(["", ""])
        prices = analysis_data.get("prices", {})
        if prices:
            writer.writerow(["Historical Prices", ""])
            writer.writerow(["Date", "Price"])
            for date, price in sorted(prices.items()):
                writer.writerow([date, f"${price:.2f}"])
            writer.writerow(["", ""])
        news = analysis_data.get("news", [])
        if news:
            writer.writerow(["Recent News Headlines", ""])
            writer.writerow(["Title", "URL"])
            for article in news[:10]:
                title = article.get("title", "No title")
                url = article.get("url", "No URL")
                writer.writerow([title, url])
        if "summary" in analysis_data and analysis_data["summary"]:
            writer.writerow(["", ""])
            writer.writerow(["Executive Summary", analysis_data["summary"]])
        writer.writerow(["", ""])
        writer.writerow(["Disclaimer", "This analysis is for informational purposes only and should not be considered as financial advice."])
        # Convert CSV to bytes and return as streaming response
        csv_content = output.getvalue().encode('utf-8')
        output.close()
        filename = f"stock_analysis_{ticker}_{datetime.now().strftime('%Y%m%d')}.csv"
        return StreamingResponse(
            io.BytesIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        # Handle errors and log them
        logger.error(f"CSV export failed for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate CSV report") 
