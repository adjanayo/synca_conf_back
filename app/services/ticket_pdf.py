import io

import qrcode
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.services.storage import upload_file


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
    pdf = canvas.Canvas(buffer, pagesize=A5)
    width, height = A5

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(15 * mm, height - 20 * mm, "SYNCA CONF 2027")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(15 * mm, height - 30 * mm, f"Billet : {ticket_number}")
    pdf.drawString(15 * mm, height - 37 * mm, f"Participant : {attendee_name}")
    pdf.drawString(15 * mm, height - 44 * mm, f"Pass : {pass_type_name}")

    pdf.drawImage(
        ImageReader(io.BytesIO(qr_png)), 15 * mm, height - 100 * mm, width=50 * mm, height=50 * mm
    )
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


async def generate_and_upload_ticket_pdf(
    ticket_number: str, qr_code_hash: str, attendee_name: str, pass_type_name: str
) -> str:
    pdf_bytes = _render_ticket_pdf(ticket_number, qr_code_hash, attendee_name, pass_type_name)
    return await upload_file(pdf_bytes, f"{ticket_number}.pdf", "application/pdf")
