"""TODO.md: HTML email templates.

Table-based, inline-CSS layout (the only markup that renders consistently
across Outlook/Gmail/Apple Mail) -- no Jinja2 dependency added, an f-string
shell is enough for 3 short templates. User-controlled values (first_name,
contact_name) are escaped: unlike the old plain-text bodies, this content is
now rendered as HTML by mail clients, so an unescaped name is a stored-XSS
vector against whoever reads the email.
"""

from html import escape

_BASE = """\
<!DOCTYPE html>
<html lang="fr">
  <body style="margin:0;padding:0;background:#f4f4f5;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
      style="background:#f4f4f5;padding:24px 0;">
      <tr>
        <td align="center">
          <table role="presentation" width="480" cellpadding="0" cellspacing="0"
            style="background:#ffffff;border-radius:8px;overflow:hidden;">
            <tr>
              <td style="background:#111827;padding:20px 32px;">
                <span style="color:#ffffff;font-size:18px;font-weight:bold;">SYNCA CONF 2027</span>
              </td>
            </tr>
            <tr>
              <td style="padding:32px;color:#111827;font-size:15px;line-height:1.5;">
                {content}
              </td>
            </tr>
            <tr>
              <td style="padding:16px 32px;background:#f9fafb;color:#9ca3af;font-size:12px;">
                Vous recevez cet email suite à une action sur syncaconf2027.com.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""


def _render(content: str) -> str:
    return _BASE.format(content=content)


def registration_confirmed_email(first_name: str) -> str:
    return _render(
        f"<p>Bonjour {escape(first_name)},</p>"
        "<p>Votre inscription à <strong>SYNCA CONF 2027</strong> est confirmée.</p>"
        "<p>Votre billet vous sera envoyé par email dès la confirmation du paiement.</p>"
    )


def application_received_email(name: str, application_label: str) -> str:
    return _render(
        f"<p>Bonjour {escape(name)},</p>"
        f"<p>Nous avons bien reçu votre candidature <strong>{escape(application_label)}</strong> "
        "pour SYNCA CONF 2027.</p>"
        "<p>Notre équipe l'étudiera et reviendra vers vous prochainement.</p>"
    )


def otp_login_email(first_name: str, code: str) -> str:
    return _render(
        f"<p>Bonjour {escape(first_name)},</p>"
        "<p>Voici votre code de connexion à votre espace SYNCA CONF 2027 :</p>"
        f'<p style="font-size:28px;font-weight:bold;letter-spacing:4px;">{escape(code)}</p>'
        "<p>Ce code expire dans 10 minutes. Si vous n'êtes pas à l'origine de cette "
        "demande, ignorez cet email.</p>"
    )


def ticket_delivered_email(first_name: str, ticket_number: str, pdf_url: str) -> str:
    ref = escape(ticket_number)
    link_style = (
        "display:inline-block;background:#111827;color:#ffffff;"
        "text-decoration:none;padding:10px 20px;border-radius:6px;"
    )
    return _render(
        f"<p>Bonjour {escape(first_name)},</p>"
        f"<p>Voici votre billet pour SYNCA CONF 2027 — référence <strong>{ref}</strong>.</p>"
        f'<p><a href="{escape(pdf_url)}" style="{link_style}">Télécharger mon billet</a></p>'
    )


def waitlist_ticketing_open_email() -> str:
    return _render(
        "<p>Bonjour,</p>"
        "<p>La billetterie de <strong>SYNCA CONF 2027</strong> vient d'ouvrir.</p>"
        "<p>Tu étais inscrit·e sur notre liste d'attente : les places sont limitées, "
        "inscris-toi dès maintenant pour réserver ton pass.</p>"
    )


def waitlist_reminder_email() -> str:
    return _render(
        "<p>Bonjour,</p>"
        "<p>La billetterie de <strong>SYNCA CONF 2027</strong> est toujours ouverte.</p>"
        "<p>Tu es toujours sur notre liste d'attente et tu n'as pas encore réservé "
        "ton pass — les places sont limitées, inscris-toi dès maintenant.</p>"
    )
