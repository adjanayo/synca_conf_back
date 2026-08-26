import io

import qrcode
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.services.storage import upload_file

# TODO.md: ticket is a wide strip, not a full A4/A5 page -- 210mm x 50mm
# (fits a standard envelope window / thermal-printer-friendly format).
_TICKET_WIDTH = 210 * mm
_TICKET_HEIGHT = 50 * mm
_QR_SIZE = 38 * mm
_MARGIN = 8 * mm


def _render_qr_png(data: str) -> bytes:
    img = qrcode.make(data)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def _render_ticket_pdf(
    ticket_number: str, qr_code_hash: str, attendee_name: str, pass_type_name: str
) -> bytes:
    qr_png = _render_qr_png(qr_code_hash)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(_TICKET_WIDTH, _TICKET_HEIGHT))

    # QR block, right-aligned, vertically centered in the strip.
    qr_x = _TICKET_WIDTH - _MARGIN - _QR_SIZE
    qr_y = (_TICKET_HEIGHT - _QR_SIZE) / 2
    pdf.drawImage(
        ImageReader(io.BytesIO(qr_png)), qr_x, qr_y, width=_QR_SIZE, height=_QR_SIZE
    )

    # Dashed perforation line separating the info block from the QR stub.
    pdf.setDash(2, 2)
    pdf.line(qr_x - _MARGIN, 0, qr_x - _MARGIN, _TICKET_HEIGHT)
    pdf.setDash()

    # Text block, left-aligned within the remaining width.
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(_MARGIN, _TICKET_HEIGHT - 14 * mm, "SYNCA CONF 2027")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(_MARGIN, _TICKET_HEIGHT - 23 * mm, f"Billet : {ticket_number}")
    pdf.drawString(_MARGIN, _TICKET_HEIGHT - 30 * mm, f"Participant : {attendee_name}")
    pdf.drawString(_MARGIN, _TICKET_HEIGHT - 37 * mm, f"Pass : {pass_type_name}")

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


async def generate_and_upload_ticket_pdf(
    ticket_number: str, qr_code_hash: str, attendee_name: str, pass_type_name: str
) -> str:
    pdf_bytes = _render_ticket_pdf(ticket_number, qr_code_hash, attendee_name, pass_type_name)
    return await upload_file(pdf_bytes, f"{ticket_number}.pdf", "application/pdf")
