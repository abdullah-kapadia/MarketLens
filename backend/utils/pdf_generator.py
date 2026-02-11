from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fpdf import FPDF, HTMLMixin
from jinja2 import Environment, FileSystemLoader, select_autoescape


class PDF(FPDF, HTMLMixin):
    pass


def _sanitize_text(text: str) -> str:
    """Replace Unicode characters with ASCII equivalents for PDF compatibility."""
    if not isinstance(text, str):
        text = str(text)
    
    replacements = {
        '\u2014': '--',  # em dash
        '\u2013': '-',   # en dash
        '\u2018': "'",   # left single quote
        '\u2019': "'",   # right single quote
        '\u201c': '"',   # left double quote
        '\u201d': '"',   # right double quote
        '\u2026': '...',  # ellipsis
        '\u00a0': ' ',   # non-breaking space
        '\u2022': '*',   # bullet
        '\u00b0': ' deg',  # degree symbol
        '\u00b1': '+/-',  # plus-minus
        '\u00d7': 'x',   # multiplication
        '\u00f7': '/',   # division
        '\u2192': '->',  # right arrow
        '\u2190': '<-',  # left arrow
        '\u2191': '^',   # up arrow
        '\u2193': 'v',   # down arrow
        '\u2212': '-',   # minus sign
        '\u221e': 'inf', # infinity
    }
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    
    # Remove any remaining non-ASCII characters (be aggressive)
    text = ''.join(char if ord(char) < 128 else ' ' for char in text)
    return text


def _template_env() -> Environment:
    templates_dir = Path(__file__).resolve().parents[1] / "templates"
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )


def _output_dir() -> Path:
    return Path(os.getenv("PDF_OUTPUT_DIR", "output/reports"))


def _sanitize_dict(data: Any) -> Any:
    """Recursively sanitize all strings in nested data structures."""
    if isinstance(data, str):
        return _sanitize_text(data)
    elif isinstance(data, dict):
        return {k: _sanitize_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_sanitize_dict(item) for item in data]
    elif isinstance(data, (int, float, bool, type(None))):
        return data
    else:
        return _sanitize_text(str(data))


def generate_pdf(report_data: dict, chart_result: dict, reasoning_trace: list) -> str:
    """Generate PDF with comprehensive error handling."""
    try:
        env = _template_env()
        template = env.get_template("report_simple.html")

        chart_base64 = chart_result.get("chart_base64", "")
        chart_config = report_data.get("chart_config", {})

        # Sanitize ALL data recursively
        report_data_clean = _sanitize_dict(report_data)
        reasoning_trace_clean = _sanitize_dict(reasoning_trace)

        html = template.render(
            ticker=chart_config.get("ticker", ""),
            generated_at=report_data_clean.get("generated_at", ""),
            current_price=report_data_clean.get("current_price", "N/A"),
            thesis=report_data_clean.get("thesis", ""),
            signal=report_data_clean.get("signal", ""),
            confidence=report_data_clean.get("confidence", ""),
            summary=report_data_clean.get("summary", ""),
            detailed_analysis=report_data_clean.get("detailed_analysis", {}),
            key_levels=report_data_clean.get("key_levels", {}),
            strategy=report_data_clean.get("strategy", {}),
            evidence_chain=report_data_clean.get("evidence_chain", []),
            risk_factors=report_data_clean.get("risk_factors", []),
            chart_base64=chart_base64,
            reasoning_trace=reasoning_trace_clean,
        )
        
        # Final sanitization of entire HTML
        html = _sanitize_text(html)

        output_dir = _output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)
        ticker = chart_config.get("ticker", "REPORT")
        timestamp = report_data_clean.get("generated_at", "").replace(":", "").replace("-", "").replace("Z", "").replace(".", "").replace("T", "")[:14]
        filename = f"MarketLens_{ticker}_{timestamp or 'latest'}.pdf"
        pdf_path = output_dir / filename

        # Use A4 page size with proper margins
        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Use helvetica (built-in, widely supported)
        pdf.set_font('helvetica', '', 11)
        
        pdf.write_html(html)
        pdf.output(str(pdf_path))
        
        print(f"[DEBUG] PDF generated successfully: {pdf_path}")
        return str(pdf_path)
    
    except Exception as e:
        print(f"[ERROR] PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        # Return empty path - report will still be saved without PDF
        return ""
