"""faqs.manage permission and seed FAQ content

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-09-03 09:30:00.000000

"""
import datetime
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f5a6b7c8d9e0'
down_revision: str | Sequence[str] | None = 'e4f5a6b7c8d9'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NEW_PERMISSION_CODES = [
    'faqs.manage',
]

# Contenu FAQ historique de data/faq.ts (brief-and-style-guide-main), gelé
# ici avec les valeurs event-settings/campaign-window "event" en vigueur au
# moment de la migration ("Synca Conf 2027", "18–20 Août 2027", "Dakar,
# Sénégal") -- désormais éditable uniquement depuis le dashboard admin, plus
# de template au runtime côté front.
FAQ_CATEGORIES = [
    {
        "name": "Général",
        "items": [
            (
                "Qu'est-ce que Synca Conf Dakar 2027 ?",
                "Synca Conf 2027 est l'une des principales conférences technologiques d'Afrique, "
                "organisée par Synca. Elle réunit décideurs institutionnels, dirigeants d'entreprises, "
                "investisseurs, chercheurs, formateurs et jeunes talents autour de la Cybersécurité, "
                "du Cloud, de la Fintech et de l'Edtech.",
            ),
            (
                "Quel est le thème de cette édition ?",
                "« Former pour l'économie réelle : combler le fossé entre éducation, compétences et "
                "emploi dans la Tech en Afrique ».",
            ),
            (
                "Quand et où se déroule l'événement ?",
                "Du 18–20 Août 2027, à Dakar, Sénégal.",
            ),
            (
                "Qui organise Synca Conf ?",
                "Synca Conf est organisée par Synca, un écosystème panafricain dédié à la technologie, "
                "aux compétences numériques et à l'innovation, mis en place par des jeunes convaincus "
                "que l'Afrique doit construire elle-même les solutions à ses propres défis. L'édition "
                "2027 est co-organisée avec Women In Tech Sénégal.",
            ),
            (
                "Quels sont les objectifs chiffrés de cette édition ?",
                "+ 1 800 participants, + 5 pays représentés, + 300 entreprises présentes, + 3 accords "
                "de partenariat signés, et + 100 offres d'emploi générées.",
            ),
            (
                "Quel est le budget prévisionnel de l'événement ?",
                "Le budget prévisionnel est estimé entre 55 et 60 millions de FCFA en coût totalement "
                "financier.",
            ),
            (
                "Qui peut participer à Synca Conf ?",
                "L'événement s'adresse aux décideurs institutionnels, dirigeants d'entreprises, "
                "investisseurs, chercheurs, formateurs, startups, étudiants et jeunes talents tech — "
                "sénégalais et panafricains.",
            ),
        ],
    },
    {
        "name": "Programme",
        "items": [
            (
                "Quels sont les 4 Summits thématiques ?",
                "Cybersécurité, Data & IA (Summit prioritaire de l'édition) · Cloud, Infrastructures "
                "de souveraineté numérique · Fintech, Innovation & Digital Leadership · Edtech, "
                "Learning & RH Technologies.",
            ),
            (
                "Quels formats sont proposés pendant les 3 jours ?",
                "Keynotes, panels & tables rondes, conférences, masterclasses, stands d'exposition, "
                "visites d'entreprises, Executive Roundtable, Synca Conf Entreprises Tours, et le "
                "Hackathon Interuniversitaire.",
            ),
            (
                "Qu'est-ce que l'Executive Roundtable ?",
                "Une table ronde restreinte réunissant dirigeants et décideurs autour d'enjeux "
                "stratégiques, dans un format confidentiel — réservée aux détenteurs du Pass Executive.",
            ),
            (
                "Qu'est-ce que le Synca Conf Entreprises Tours ?",
                "Un programme de visites de terrain (datacenters, entreprises technologiques "
                "partenaires) réservé à une délégation restreinte de dirigeants et d'experts "
                "internationaux.",
            ),
            (
                "Comment sont sélectionnés les intervenants et speakers ?",
                "L'équipe Synca invite des profils reconnus dans chaque domaine (cybersécurité, cloud, "
                "fintech, edtech, marketing digital…), en cohérence avec les thématiques des Summits. "
                "Toute personne intéressée peut aussi se manifester auprès de l'équipe organisatrice.",
            ),
            (
                "Les masterclasses donnent-elles lieu à un contenu à emporter ?",
                "Oui. Chaque masterclass Synca Conf a pour finalité de produire un livrable concret "
                "pour les participants (document, plan d'action, prototype…), et non un simple contenu "
                "passif.",
            ),
        ],
    },
    {
        "name": "Billetterie",
        "items": [
            (
                "Quels types de billets sont disponibles ?",
                "Un billet gratuit (réservé aux étudiants et invités), le Pass Pro, le Pass Premium, "
                "le Pass Executive, ainsi qu'un billet en ligne pour suivre l'événement à distance.",
            ),
            (
                "Quels sont les avantages de chaque billet ?",
                "Le Pro donne accès aux 3 jours, conférences, panels et à l'espace exposition. Le "
                "Premium ajoute le déjeuner, une masterclass au choix et le Networking Lounge. "
                "L'Executive ajoute l'Executive Lounge, le dîner de clôture, le Synca Conf Entreprises "
                "Tours et une session de négociation de partenariats.",
            ),
            (
                "Existe-t-il des billets gratuits ?",
                "Oui, un quota de billets gratuits est réservé aux étudiants ainsi qu'aux speakers, "
                "bénévoles, partenaires institutionnels, invités, communautés Tech, médias et "
                "partenaires universitaires.",
            ),
            (
                "Comment fonctionne le tarif Early Bird ?",
                "Un nombre limité de billets Pro, Premium et Executive est proposé à tarif réduit. Le "
                "tarif Early Bird s'applique jusqu'à épuisement du quota dédié ou jusqu'à une date "
                "limite, selon la première des deux conditions atteintes.",
            ),
            (
                "Existe-t-il un billet en ligne pour suivre l'événement à distance ?",
                "Oui, un billet en ligne donne accès à la diffusion en streaming des keynotes, panels "
                "et conférences, avec replay disponible, pour les personnes ne pouvant se déplacer à "
                "Dakar.",
            ),
            (
                "Comment fonctionne le quota ambassadeurs ?",
                "Les ambassadeurs Synca disposent d'un quota de billets à distribuer via un code "
                "dédié, prélevé sur les quotas existants (Pro, Premium, Executive) et non ajouté en "
                "supplément.",
            ),
            (
                "Le billet inclut-il l'hébergement ou le transport ?",
                "Non, sauf dispositif spécifique — comme pour les leads de communautés Tech "
                "sélectionnés au programme Synca Community Certified, ou les équipes universitaires "
                "du Hackathon, qui bénéficient d'une prise en charge logistique partielle.",
            ),
        ],
    },
    {
        "name": "Hackathon",
        "items": [
            (
                "En quoi consiste le Hackathon ?",
                "Le Synca Cyber Challenge réunit des équipes d'étudiants autour de la conception de "
                "solutions de cybersécurité accessibles aux TPE, PME et MPME africaines, lors d'une "
                "compétition de 48h en présentiel pendant la conférence.",
            ),
            (
                "Qui peut y participer ?",
                "Des équipes d'étudiants inscrites par leur université, dans le cadre d'un partenariat "
                "universitaire officiellement signé avec Synca.",
            ),
            (
                "Comment une université peut-elle inscrire ses équipes ?",
                "En signant un partenariat universitaire avec Synca, puis en constituant ses équipes "
                "une fois les thématiques transmises par l'équipe Synca.",
            ),
            (
                "Combien d'équipes une université peut-elle inscrire ?",
                "Deux équipes de 3 étudiants chacune, soit 6 candidats au total, chaque équipe "
                "travaillant sur un projet distinct.",
            ),
            (
                "Comment se déroule la préparation avant le Hackathon ?",
                "Les équipes bénéficient d'un mois de préparation encadrée avant le début du "
                "Hackathon, qui se tient ensuite sur 48h pendant les 3 jours de la conférence.",
            ),
            (
                "Quelles sont les récompenses ?",
                "Un Grand Prix pour la 1ère équipe (dotation cloud & cybersécurité, incubation, "
                "visibilité), des dotations pour les 2e et 3e équipes, ainsi que des prix spéciaux "
                "(Impact PME, Innovation, Coup de Cœur du Jury).",
            ),
            (
                "Qu'est-ce que le Synca Pedagogy Award ?",
                "Un prix attribué directement à l'université de l'équipe gagnante, récompensant la "
                "meilleure méthodologie pédagogique, l'innovation pédagogique et la disposition de "
                "ressources opérationnelles adéquates pour la formation Tech.",
            ),
        ],
    },
    {
        "name": "Universités",
        "items": [
            (
                "Comment une université devient-elle partenaire de Synca Conf ?",
                "En signant un partenariat universitaire officiel avec Synca, incluant la lettre "
                "d'engagement de sa direction.",
            ),
            (
                "Qu'est-ce que Synca Community Certified ?",
                "Un programme de structuration et de gouvernance des communautés Tech africaines, "
                "intégré au programme officiel de Synca Conf, à travers un atelier co-organisé avec "
                "des experts, ouvert à toutes les communautés Tech africaines.",
            ),
            (
                "Quelles sont les conditions de participation à Synca Community Certified ?",
                "Être fondateur ou co-fondateur d'une communauté Tech, disposer d'une activité "
                "documentée sur les 12 derniers mois, être disponible sur les 3 jours de la "
                "conférence, et s'engager à restituer les apprentissages à sa communauté.",
            ),
            (
                "Quels dispositifs facilitent la participation des leads de communautés et des "
                "universités ?",
                "Une prise en charge logistique partielle (hébergement et mobilité sur Dakar — le "
                "billet d'avion restant à la charge du lead), un billet d'accès aux 3 jours de "
                "conférence, et la participation aux visites d'entreprises de l'écosystème sénégalais.",
            ),
            (
                "Quelle est la date limite pour candidater ?",
                "La date limite de candidature est fixée au 31 décembre 2026, pour une annonce des "
                "candidats retenus à la mi-janvier 2027.",
            ),
            (
                "Les universités doivent-elles contribuer financièrement au Hackathon ?",
                "Oui, chaque université met à disposition un fonds destiné à la prise en charge "
                "logistique de ses candidats (restauration, sécurité), avec un versement de 40 % des "
                "frais attendus une fois le partenariat confirmé.",
            ),
        ],
    },
    {
        "name": "Sponsoring",
        "items": [
            (
                "Quels sont les paliers de sponsoring disponibles ?",
                "Quatre paliers, du Bronze au Titre, chacun avec des avantages progressifs : "
                "visibilité, prise de parole, stand d'exposition, accès à l'Executive Roundtable et "
                "au Synca Conf Entreprises Tours.",
            ),
            (
                "Existe-t-il des options de partenariat au-delà des paliers fixes ?",
                "Oui — naming d'un Summit, masterclass dédiée, side event, partenariat Hackathon, "
                "partenariat Job Dating, prix Synca Conf Awards, stand additionnel, ou slot de "
                "présentation de recherche.",
            ),
            (
                "Comment devenir partenaire média ou communautaire ?",
                "Via un partenariat d'échange de visibilité (couverture de l'événement, interviews, "
                "visibilité croisée) plutôt qu'un sponsoring financier classique — à discuter "
                "directement avec l'équipe Partenariats.",
            ),
            (
                "Une entreprise peut-elle intégrer sa solution technique à l'événement ?",
                "Oui, notamment pour des solutions de paiement ou d'infrastructure (ex. billetterie), "
                "sur la base d'un partenariat technique dédié, en complément ou non d'un palier de "
                "sponsoring.",
            ),
            (
                "Qui contacter pour un partenariat ?",
                "Astou Diakhate, Responsable Sponsoring & Partenariats — "
                "astou.diakhate@sync-africa.com — +221 77 150 07 43.",
            ),
        ],
    },
    {
        "name": "Exposition",
        "items": [
            (
                "Comment inscrire mon entreprise à l'espace exposition ?",
                "Via le formulaire d'inscription exposants, qui couvre l'entreprise, le contact "
                "référent, le type de stand souhaité et les besoins logistiques.",
            ),
            (
                "Quels types de stands sont proposés ?",
                "Standard, Premium ou mutualisé, selon le niveau de visibilité souhaité.",
            ),
            (
                "L'exposition est-elle réservée aux sponsors ?",
                "Non — un stand peut être associé à un palier de sponsoring ou souscrit "
                "indépendamment, selon les disponibilités.",
            ),
        ],
    },
    {
        "name": "Ambassadeurs",
        "items": [
            (
                "Qu'est-ce que le programme Ambassadeurs Synca Conf ?",
                "Un programme bénévole permettant à des passionnés de tech de relayer l'événement, "
                "mobiliser leur réseau et représenter Synca Conf localement.",
            ),
            (
                "Qui peut devenir ambassadeur ?",
                "Toute personne passionnée de technologie ou d'innovation, active sur les réseaux "
                "sociaux ou dans une communauté, basée en Afrique ou dans la diaspora.",
            ),
            (
                "Quels sont les avantages du statut d'ambassadeur ?",
                "Badge d'accès à l'événement, certificat officiel, accès privilégié au réseau des "
                "partenaires, kit ambassadeur, et opportunité de devenir référent local pour les "
                "prochaines éditions.",
            ),
            (
                "Comment candidater ?",
                "Via le formulaire de candidature Ambassadeurs, disponible sur les canaux officiels "
                "de Synca Conf.",
            ),
        ],
    },
    {
        "name": "Synca Builders",
        "items": [
            (
                "Qu'est-ce que Synca Builders ?",
                "Un programme réunissant les acteurs de l'écosystème (devs, marketeurs, designers…) "
                "qui contribuent directement aux projets de Synca, sur la base d'un engagement annuel.",
            ),
            (
                "Qui peut rejoindre le programme ?",
                "Toute personne active dans l'écosystème tech ou digital africain, disposant d'un "
                "portfolio ou de réalisations vérifiables, sur l'un des 5 tracks : Tech & Dev, Design "
                "& UX, Marketing & Growth, Contenu & Communauté, Partenariats & Ops.",
            ),
            (
                "Quel est le niveau d'engagement demandé ?",
                "5 à 10 heures par mois, la participation à au moins un projet majeur de l'année, et "
                "la présence aux points de suivi mensuels et au Synca Builders Summit.",
            ),
            (
                "Qu'est-ce que le Synca Builders Summit ?",
                "Une rencontre annuelle, en décembre, dédiée au bilan des contributions de l'année et "
                "à l'annonce des nouveaux projets de l'écosystème Synca.",
            ),
        ],
    },
    {
        "name": "Infos pratiques",
        "items": [
            (
                "Ai-je besoin d'un visa pour me rendre à Dakar ?",
                "Cela dépend de votre nationalité. Nous recommandons de vous renseigner directement "
                "auprès de l'ambassade ou du consulat du Sénégal de votre pays de résidence, ainsi "
                "que sur le site officiel des autorités sénégalaises.",
            ),
            (
                "L'hébergement est-il inclus dans mon billet ?",
                "Non, sauf pour les participants bénéficiant d'un dispositif spécifique (leads de "
                "communautés retenus, équipes universitaires du Hackathon).",
            ),
            (
                "Comment contacter l'équipe organisatrice ?",
                "Astou Diakhate — Sponsoring & Partenariats — astou.diakhate@sync-africa.com — "
                "+221 77 150 07 43. Rolle TINDJIETE — Fondateur, Synca — rolle.tindjiete@sync-africa.com "
                "— +228 70 48 41 64.",
            ),
        ],
    },
]


def upgrade() -> None:
    """Upgrade schema."""
    permissions_table = sa.table(
        'permissions', sa.column('id', sa.Integer), sa.column('code', sa.String)
    )
    roles_table = sa.table('roles', sa.column('id', sa.Integer), sa.column('name', sa.String))
    role_permissions_table = sa.table(
        'role_permissions',
        sa.column('role_id', sa.Integer),
        sa.column('permission_id', sa.Integer),
    )

    op.bulk_insert(permissions_table, [{'code': code} for code in NEW_PERMISSION_CODES])

    connection = op.get_bind()
    superadmin_id = connection.execute(
        sa.select(roles_table.c.id).where(roles_table.c.name == 'superadmin')
    ).scalar_one()
    new_permission_ids = connection.execute(
        sa.select(permissions_table.c.id).where(
            permissions_table.c.code.in_(NEW_PERMISSION_CODES)
        )
    ).scalars().all()
    op.bulk_insert(
        role_permissions_table,
        [
            {'role_id': superadmin_id, 'permission_id': pid}
            for pid in new_permission_ids
        ],
    )

    faq_categories_table = sa.table(
        'faq_categories', sa.column('id', sa.Integer), sa.column('name', sa.String)
    )
    faqs_table = sa.table(
        'faqs',
        sa.column('id', sa.Integer),
        sa.column('category_id', sa.Integer),
        sa.column('question', sa.Text),
        sa.column('answer', sa.Text),
        sa.column('sort_order', sa.Integer),
        sa.column('created_at', sa.DateTime),
    )

    now = datetime.datetime.utcnow()
    for category in FAQ_CATEGORIES:
        result = connection.execute(
            faq_categories_table.insert().values(name=category['name'])
        )
        category_id = result.lastrowid
        op.bulk_insert(
            faqs_table,
            [
                {
                    'category_id': category_id,
                    'question': question,
                    'answer': answer,
                    'sort_order': i,
                    'created_at': now,
                }
                for i, (question, answer) in enumerate(category['items'])
            ],
        )


def downgrade() -> None:
    """Downgrade schema."""
    connection = op.get_bind()
    faq_categories_table = sa.table(
        'faq_categories', sa.column('id', sa.Integer), sa.column('name', sa.String)
    )
    category_names = [category['name'] for category in FAQ_CATEGORIES]
    category_ids = connection.execute(
        sa.select(faq_categories_table.c.id).where(
            faq_categories_table.c.name.in_(category_names)
        )
    ).scalars().all()

    if category_ids:
        connection.execute(
            sa.text("DELETE FROM faqs WHERE category_id IN :ids").bindparams(
                sa.bindparam('ids', expanding=True)
            ),
            {'ids': category_ids},
        )
        connection.execute(
            sa.text("DELETE FROM faq_categories WHERE id IN :ids").bindparams(
                sa.bindparam('ids', expanding=True)
            ),
            {'ids': category_ids},
        )

    permissions_table = sa.table(
        'permissions', sa.column('id', sa.Integer), sa.column('code', sa.String)
    )
    permission_ids = connection.execute(
        sa.select(permissions_table.c.id).where(
            permissions_table.c.code.in_(NEW_PERMISSION_CODES)
        )
    ).scalars().all()

    if permission_ids:
        connection.execute(
            sa.text(
                "DELETE FROM role_permissions WHERE permission_id IN :ids"
            ).bindparams(sa.bindparam('ids', expanding=True)),
            {'ids': permission_ids},
        )
        connection.execute(
            sa.text("DELETE FROM permissions WHERE id IN :ids").bindparams(
                sa.bindparam('ids', expanding=True)
            ),
            {'ids': permission_ids},
        )
