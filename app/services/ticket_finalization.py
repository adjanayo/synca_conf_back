from loguru import logger

from app.core.database import AsyncSessionLocal
from app.models import PassType, Ticket, User
from app.services.email_service import send_email
from app.services.email_templates import ticket_delivered_email
from app.services.ticket_pdf import generate_and_upload_ticket_pdf


async def finalize_ticket(ticket_id: int) -> None:
    """Generate the ticket's PDF+QR, upload it, and email it.

    Runs as a BackgroundTask after the webhook's response is sent, using
    its own DB session (the request-scoped one is already closed by then).
    Deliberately separate from the atomic payment+ticket transaction (5.5)
    -- losing/retrying a PDF upload is fine, losing the ticket record isn't,
    so the slow external I/O (B2 upload, Resend) doesn't hold that
    transaction open.
    """
    async with AsyncSessionLocal() as db:
        ticket = await db.get(Ticket, ticket_id)
        if ticket is None or ticket.pdf_url is not None:
            return  # already finalized, or the ticket vanished -- no-op

        user = await db.get(User, ticket.user_id)
        pass_type = await db.get(PassType, ticket.pass_type_id)
        if user is None or pass_type is None:
            logger.bind(channel="payment").warning(
                f"Impossible de finaliser le ticket {ticket.id} : user/pass_type manquant"
            )
            return

        attendee_name = f"{user.first_name} {user.last_name}"
        pdf_url = await generate_and_upload_ticket_pdf(
            ticket.ticket_number, ticket.qr_code_hash, attendee_name, pass_type.name
        )

        ticket.pdf_url = pdf_url
        await db.commit()

        await send_email(
            to=user.email,
            subject="Votre billet — SYNCA CONF 2027",
            body=ticket_delivered_email(user.first_name, ticket.ticket_number, pdf_url),
        )
        logger.bind(channel="payment").info(f"Ticket {ticket.ticket_number} finalisé et envoyé")
