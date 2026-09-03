import io

import qrcode
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.services.storage import upload_file

# TODO.md: ticket is a wide strip, not a full A4/A5 page -- 210mm x 50mm
# (fits a standard envelope window / thermal-printer-friendly format).
_TICKET_WIDTH = 210 * mm
_TICKET_HEIGHT = 50 * mm
_HEADER_HEIGHT = 12 * mm
_QR_SIZE = 32 * mm
_MARGIN = 8 * mm

# Same palette as the HTML email shell (app/services/email_templates.py) --
# dark header band + amber accent, so a printed ticket and the email that
# delivered it read as the same brand.
_COLOR_DARK = colors.HexColor("#111827")
_COLOR_ACCENT = colors.HexColor("#f59e0b")
_COLOR_ACCENT_LIGHT = colors.HexColor("#fef3c7")


def _render_qr_png(data: str) -> bytes:
    img = qrcode.make(data)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def _render_ticket_pdf(
    ticket_number: str,
    qr_code_hash: str,
    attendee_name: str,
    pass_type_name: str,
    event_name: str,
    venue: str,
) -> bytes:
    qr_png = _render_qr_png(qr_code_hash)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(_TICKET_WIDTH, _TICKET_HEIGHT))

    # Dark header band with the amber accent rule underneath.
    pdf.setFillColor(_COLOR_DARK)
    pdf.rect(0, _TICKET_HEIGHT - _HEADER_HEIGHT, _TICKET_WIDTH, _HEADER_HEIGHT, stroke=0, fill=1)
    pdf.setFillColor(_COLOR_ACCENT)
    pdf.rect(
        0, _TICKET_HEIGHT - _HEADER_HEIGHT - 1.5 * mm, _TICKET_WIDTH, 1.5 * mm, stroke=0, fill=1
    )
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(_MARGIN, _TICKET_HEIGHT - _HEADER_HEIGHT + 3.5 * mm, event_name.upper())

    # QR block, right-aligned, on a light amber tile.
    tile_size = _QR_SIZE + 4 * mm
    tile_x = _TICKET_WIDTH - _MARGIN - tile_size
    tile_y = (_TICKET_HEIGHT - _HEADER_HEIGHT - 1.5 * mm - tile_size) / 2
    pdf.setFillColor(_COLOR_ACCENT_LIGHT)
    pdf.roundRect(tile_x, tile_y, tile_size, tile_size, 2 * mm, stroke=0, fill=1)
    pdf.drawImage(
        ImageReader(io.BytesIO(qr_png)),
        tile_x + 2 * mm,
        tile_y + 2 * mm,
        width=_QR_SIZE,
        height=_QR_SIZE,
    )

    # Dashed perforation line separating the info block from the QR stub.
    pdf.setStrokeColor(colors.HexColor("#d1d5db"))
    pdf.setDash(2, 2)
    pdf.line(tile_x - _MARGIN, 0, tile_x - _MARGIN, _TICKET_HEIGHT - _HEADER_HEIGHT - 1.5 * mm)
    pdf.setDash()

    # Text block, left-aligned within the remaining width, below the header.
    pdf.setFillColor(_COLOR_DARK)
    pdf.setFont("Helvetica", 10)
    line_y = _TICKET_HEIGHT - _HEADER_HEIGHT - 1.5 * mm - 7 * mm
    for label, value in (
        ("Billet", ticket_number),
        ("Participant", attendee_name),
        ("Pass", pass_type_name),
        ("Lieu", venue),
    ):
        pdf.drawString(_MARGIN, line_y, f"{label} : {value}")
        line_y -= 6.5 * mm

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


async def generate_and_upload_ticket_pdf(
    ticket_number: str,
    qr_code_hash: str,
    attendee_name: str,
    pass_type_name: str,
    event_name: str,
    venue: str,
) -> str:
    pdf_bytes = _render_ticket_pdf(
        ticket_number, qr_code_hash, attendee_name, pass_type_name, event_name, venue
    )
    return await upload_file(pdf_bytes, f"{ticket_number}.pdf", "application/pdf")
