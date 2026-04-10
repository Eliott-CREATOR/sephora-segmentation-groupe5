"""
components.py — Sephora HTML Component Library
Fonctions retournant du HTML stylisé pour st.markdown(unsafe_allow_html=True)
"""

import os
import base64

GOLD    = "#C9A84C"
RED     = "#CC0033"
GREEN   = "#2EC4B6"
DARK_BG = "#0D0D0D"
BORDER  = "#1A1A1A"

# ── PERSONA AVATARS SVG ────────────────────────────────────────────────────────

PERSONA_AVATARS = {
    0: """<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
        <circle cx="40" cy="28" r="14" fill="#C9A84C" opacity="0.9"/>
        <path d="M20 65 Q40 45 60 65" fill="#C9A84C" opacity="0.7"/>
        <path d="M28 20 L32 14 L40 18 L48 14 L52 20 L28 20Z" fill="#F5F0EB" opacity="0.9"/>
        <circle cx="40" cy="28" r="5" fill="#0A0A0A"/>
    </svg>""",

    1: """<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
        <circle cx="40" cy="28" r="13" fill="#FF6B9D" opacity="0.9"/>
        <path d="M22 65 Q40 48 58 65" fill="#FF6B9D" opacity="0.7"/>
        <text x="15" y="25" font-size="8" fill="#C9A84C" opacity="0.8">✦</text>
        <text x="55" y="20" font-size="6" fill="#C9A84C" opacity="0.6">✦</text>
        <text x="58" y="45" font-size="5" fill="#C9A84C" opacity="0.5">✦</text>
    </svg>""",

    2: """<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
        <circle cx="40" cy="28" r="14" fill="#444" opacity="0.8"/>
        <path d="M20 65 Q40 55 60 65" fill="#444" opacity="0.6"/>
        <text x="50" y="22" font-size="7" fill="#666" opacity="0.9">z</text>
        <text x="55" y="16" font-size="9" fill="#666" opacity="0.7">z</text>
        <text x="61" y="10" font-size="11" fill="#666" opacity="0.5">z</text>
    </svg>""",

    3: """<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
        <circle cx="40" cy="28" r="14" fill="#E8B4A0" opacity="0.9"/>
        <path d="M22 65 Q40 47 58 65" fill="#E8B4A0" opacity="0.7"/>
        <rect x="50" y="10" width="20" height="14" rx="2" fill="#CC0033" opacity="0.9"/>
        <text x="53" y="21" font-size="9" fill="white" font-weight="bold">%</text>
    </svg>""",

    4: """<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
        <circle cx="40" cy="28" r="14" fill="#2EC4B6" opacity="0.9"/>
        <path d="M22 65 Q40 47 58 65" fill="#2EC4B6" opacity="0.7"/>
        <circle cx="28" cy="15" r="4" fill="#C9A84C" opacity="0.8"/>
        <circle cx="52" cy="15" r="4" fill="#C9A84C" opacity="0.8"/>
        <line x1="32" y1="15" x2="48" y2="15" stroke="#C9A84C" stroke-width="1.5" opacity="0.8"/>
    </svg>""",

    5: """<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
        <circle cx="40" cy="28" r="14" fill="#7CB99A" opacity="0.9"/>
        <path d="M22 65 Q40 47 58 65" fill="#7CB99A" opacity="0.7"/>
        <path d="M55 8 Q65 18 55 28 Q45 18 55 8Z" fill="#2EC4B6" opacity="0.8"/>
    </svg>""",

    6: """<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
        <circle cx="40" cy="28" r="14" fill="#9B7FD4" opacity="0.9"/>
        <path d="M22 65 Q40 47 58 65" fill="#9B7FD4" opacity="0.7"/>
        <rect x="50" y="14" width="12" height="16" rx="2" fill="#C9A84C" opacity="0.8"/>
        <rect x="53" y="10" width="6" height="5" rx="1" fill="#C9A84C" opacity="0.6"/>
    </svg>""",

    7: """<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
        <circle cx="40" cy="28" r="13" fill="#B0A090" opacity="0.8"/>
        <path d="M24 65 Q40 50 56 65" fill="#B0A090" opacity="0.6"/>
        <rect x="50" y="12" width="14" height="14" rx="1" fill="none" stroke="#C9A84C" stroke-width="1.5" opacity="0.7"/>
        <text x="54" y="22" font-size="7" fill="#C9A84C" opacity="0.7">cal</text>
    </svg>""",

    8: """<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
        <circle cx="40" cy="28" r="14" fill="#C9A84C" opacity="1"/>
        <path d="M18 65 Q40 42 62 65" fill="#C9A84C" opacity="0.8"/>
        <path d="M40 8 L48 16 L40 26 L32 16Z" fill="white" opacity="0.9"/>
        <line x1="32" y1="16" x2="48" y2="16" stroke="#C9A84C" stroke-width="1"/>
    </svg>""",
}


# ── COMPONENT FUNCTIONS ────────────────────────────────────────────────────────

def kpi_card(label: str, value: str, delta: str = "",
             variant: str = "default", animated: bool = True) -> str:
    """
    Carte KPI Sephora.
    variant: 'default' | 'danger' | 'success'
    """
    colors = {
        "default": (GOLD,   GOLD   + "33"),
        "danger":  (RED,    RED    + "33"),
        "success": (GREEN,  GREEN  + "33"),
    }
    val_color, _ = colors.get(variant, colors["default"])
    pulse = "animation: pulseGold 2s infinite;" if animated else ""

    delta_html = ""
    if delta:
        d_color = GREEN if "+" in delta else RED
        arrow   = "↑" if "+" in delta else "↓"
        delta_html = (
            f'<div style="font-family:\'DM Mono\',monospace;font-size:0.65rem;'
            f'color:{d_color};margin-top:0.4rem;letter-spacing:0.1em">'
            f'{arrow} {delta}</div>'
        )

    return f"""
    <div class="kpi-card {variant}" style="{pulse}border-top-color:{val_color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="color:{val_color}">{value}</div>
        {delta_html}
    </div>"""


def persona_avatar_html(cluster_id: int, size: int = 80,
                        persona_color: str = GOLD) -> str:
    """Avatar SVG animé pour un cluster."""
    svg = PERSONA_AVATARS.get(cluster_id, PERSONA_AVATARS[0])
    float_duration = 2.5 + cluster_id * 0.3
    return f"""
    <div style="
        width:{size}px; height:{size}px; margin:0 auto 1rem;
        animation: personaFloat {float_duration}s ease-in-out infinite;
        filter: drop-shadow(0 4px 12px {persona_color}40);
    ">
        {svg}
    </div>"""


def product_image_card(image_path: str, label: str,
                       metric: str = "", color: str = GOLD) -> str:
    """
    Carte image produit Sephora.
    image_path : nom de fichier dans app/assets/
    """
    full_path = os.path.join(os.path.dirname(__file__), "assets", image_path)
    if os.path.exists(full_path):
        with open(full_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = image_path.split(".")[-1].lower()
        mime_map = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png",
                    "webp": "webp", "avif": "avif", "gif": "gif"}
        mime = mime_map.get(ext, "jpeg")
        img_src = f"data:image/{mime};base64,{b64}"
    else:
        img_src = ""

    metric_html = (
        f'<div style="font-family:\'DM Mono\',monospace;font-size:0.7rem;'
        f'color:{color};letter-spacing:0.1em;margin-top:0.5rem">{metric}</div>'
        if metric else ""
    )

    return f"""
    <div style="
        background:{DARK_BG}; border:1px solid {BORDER};
        padding:1rem; text-align:center;
        transition: all 0.4s ease; cursor:pointer;
        animation: fadeInUp 0.6s ease forwards;
    " onmouseover="this.style.borderColor='{color}';this.style.transform='translateY(-3px)'"
       onmouseout="this.style.borderColor='{BORDER}';this.style.transform='none'">
        {'<img src="' + img_src + '" style="width:100%;max-height:140px;object-fit:contain;animation:productReveal 0.8s ease forwards;filter:drop-shadow(0 4px 16px rgba(0,0,0,0.6));" alt="' + label + '"/>' if img_src else '<div style="height:80px;background:#111;display:flex;align-items:center;justify-content:center;color:#333;font-size:0.6rem;font-family:DM Mono,monospace;">NO IMAGE</div>'}
        <div style="font-family:'Jost',sans-serif;font-size:0.75rem;
                    color:#888;margin-top:0.7rem;letter-spacing:0.05em">
            {label}
        </div>
        {metric_html}
    </div>"""


def section_header(title: str, subtitle: str = "",
                   accent: str = GOLD) -> str:
    """En-tête de section avec barre d'accentuation."""
    sub_html = (
        f'<p style="font-family:\'Lato\',sans-serif;font-size:0.8rem;'
        f'color:#666;letter-spacing:0.08em;margin-top:0.3rem">{subtitle}</p>'
        if subtitle else ""
    )
    return f"""
    <div style="margin:2rem 0 1.5rem; animation: slideInLeft 0.5s ease forwards">
        <div style="display:flex;align-items:center;gap:1rem">
            <div style="width:3px;height:2rem;background:{accent};flex-shrink:0"></div>
            <div>
                <h2 style="font-family:'Jost',sans-serif;font-weight:400;
                           font-size:1.4rem;color:#F5F0EB;letter-spacing:0.06em;
                           font-style:italic;margin:0;border:none;padding:0">
                    {title}
                </h2>
                {sub_html}
            </div>
        </div>
        <div style="height:1px;background:linear-gradient(90deg,{accent}40,transparent);
                    margin-top:0.8rem"></div>
    </div>"""


def versus_box(label: str, our_value: str, rfm_value: str,
               delta: str = "", our_label: str = "Notre système",
               rfm_label: str = "RFM Sephora actuel") -> str:
    """Boîte de comparaison Notre système vs RFM."""
    return f"""
    <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:0;
                border:1px solid {BORDER};margin:0.5rem 0;
                animation:fadeInUp 0.6s ease forwards">
        <div style="background:{DARK_BG};padding:1.2rem;border-right:1px solid {BORDER}">
            <div style="font-family:'DM Mono',monospace;font-size:0.55rem;
                        letter-spacing:0.2em;color:{GOLD};text-transform:uppercase;
                        margin-bottom:0.5rem">{our_label}</div>
            <div style="font-family:'Jost',sans-serif;font-size:1.8rem;
                        color:{GOLD};font-weight:300">{our_value}</div>
            <div style="font-size:0.7rem;color:#444;margin-top:0.3rem">{label}</div>
        </div>
        <div style="background:#050505;padding:1.2rem;display:flex;
                    align-items:center;justify-content:center;min-width:60px">
            <div style="font-family:'DM Mono',monospace;font-size:0.6rem;
                        color:#333;letter-spacing:0.1em">VS</div>
        </div>
        <div style="background:#090909;padding:1.2rem;border-left:1px solid {BORDER}">
            <div style="font-family:'DM Mono',monospace;font-size:0.55rem;
                        letter-spacing:0.2em;color:#444;text-transform:uppercase;
                        margin-bottom:0.5rem">{rfm_label}</div>
            <div style="font-family:'Jost',sans-serif;font-size:1.8rem;
                        color:#444;font-weight:300;text-decoration:line-through">{rfm_value}</div>
            <div style="font-size:0.7rem;color:#333;margin-top:0.3rem">{label}</div>
        </div>
    </div>"""


def alert_banner(message: str, severity: str = "danger",
                 icon: str = "") -> str:
    """Bannière d'alerte stylisée."""
    configs = {
        "danger":  (RED,   RED   + "15", "⚠"),
        "warning": (GOLD,  GOLD  + "15", "◈"),
        "success": (GREEN, GREEN + "15", "✓"),
    }
    color, bg, default_icon = configs.get(severity, configs["danger"])
    used_icon = icon or default_icon
    anim = "animation: blinkRed 2s infinite;" if severity == "danger" else ""
    return f"""
    <div style="background:{bg};border-left:3px solid {color};
                padding:1rem 1.2rem;margin:0.8rem 0;
                display:flex;align-items:center;gap:0.8rem;{anim}">
        <span style="color:{color};font-size:1rem;{anim}">{used_icon}</span>
        <span style="font-family:'Jost',sans-serif;font-size:0.8rem;
                     color:#F5F0EB;letter-spacing:0.03em">{message}</span>
    </div>"""


def crm_action_card(action_dict: dict, n_clients: int,
                    ca_recoverable: float) -> str:
    """Carte d'action CRM avec KPIs et ROI."""
    color = action_dict.get("color", GOLD)
    avg_basket_recovery = action_dict.get("avg_basket_recovery",
                                          ca_recoverable / max(n_clients, 1))
    retention_48h = action_dict.get("retention_48h", 0.18)
    retention_30d = action_dict.get("retention_30d", 0.32)
    cost_per_client = action_dict.get("cost_per_client", 3.5)

    savings_48h = n_clients * retention_48h * avg_basket_recovery
    savings_30d = n_clients * retention_30d * avg_basket_recovery
    cost        = n_clients * cost_per_client
    roi         = savings_30d / cost if cost > 0 else 0
    gain_delta  = savings_48h - savings_30d * 0.6

    label    = action_dict.get("label", "Action CRM")
    channels = action_dict.get("canal", action_dict.get("channels", "Email + SMS"))
    action   = action_dict.get("action", "—")

    return f"""
    <div style="background:{DARK_BG};border:1px solid {BORDER};
                border-left:3px solid {color};padding:1.5rem;
                animation:fadeInUp 0.5s ease forwards">
        <div style="font-family:'DM Mono',monospace;font-size:0.6rem;
                    letter-spacing:0.2em;color:{color};text-transform:uppercase;
                    margin-bottom:1rem">{label}</div>
        <div style="background:{color}18;padding:0.5rem 0.8rem;
                    display:inline-block;margin-bottom:1rem">
            <span style="font-family:'DM Mono',monospace;font-size:0.65rem;
                         color:{color};letter-spacing:0.15em">
                {channels}
            </span>
        </div>
        <p style="font-family:'Jost',sans-serif;font-size:0.8rem;
                  color:#AAA;line-height:1.6;margin-bottom:1rem">
            {action}
        </p>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;
                    gap:0.8rem;border-top:1px solid {BORDER};padding-top:1rem">
            <div>
                <div class="kpi-label">Clients ciblés</div>
                <div style="font-family:'DM Mono',monospace;font-size:1rem;
                            color:{color}">{n_clients:,}</div>
            </div>
            <div>
                <div class="kpi-label">Économie 48h</div>
                <div style="font-family:'DM Mono',monospace;font-size:1rem;
                            color:{GREEN}">{savings_48h:,.0f} €</div>
            </div>
            <div>
                <div class="kpi-label">ROI net</div>
                <div style="font-family:'DM Mono',monospace;font-size:1rem;
                            color:{color}">{roi:.1f}x</div>
            </div>
        </div>
        <div style="margin-top:1rem;padding:0.6rem;background:{color}10;
                    border:1px dashed {color}40;text-align:center">
            <span style="font-family:'DM Mono',monospace;font-size:0.6rem;
                         color:{color};letter-spacing:0.1em">
                GAIN INTERVENTION RAPIDE (48H VS 30J) : +{gain_delta:,.0f} €
            </span>
        </div>
    </div>"""


# ── MARKETING PLAYBOOK ─────────────────────────────────────────────────────────
# 3 recommandations par cluster — cohérentes avec les profils Sephora.
# Chaque entrée : titre, priorite, canal, timing, segment_cible, message,
#                 kpis_cibles, budget_estime, roi_estime, outils, tag, color

MARKETING_PLAYBOOK = {
    0: [  # Cluster 0 — Clientèle standard, potentiel d'upgrade
        {
            "titre": "Réactivation Email Automation",
            "priorite": "HAUTE",
            "canal": "Email",
            "timing": "J+0 → J+7 → J+14",
            "segment_cible": "Clients inactifs >90j",
            "message": "Séquence 3 emails : teaser exclusivité → offre personnalisée -15% → last chance urgence",
            "kpis_cibles": "Taux ouverture >28% | CTR >4.5% | Conversion >2%",
            "budget_estime": "1.2 € / client",
            "roi_estime": "8x",
            "outils": "Salesforce Marketing Cloud · Adobe Campaign",
            "tag": "RETENTION",
            "color": RED,
        },
        {
            "titre": "Programme Fidélité — Niveau Bronze→Silver",
            "priorite": "MOYENNE",
            "canal": "App Mobile + Email",
            "timing": "Dès 2e achat · rappel à J+30",
            "segment_cible": "Clients 1–3 achats",
            "message": "Incentiver la montée en gamme : double points pendant 30j, accès early sale, beauty gift à 150€ d'achats",
            "kpis_cibles": "Upgrade rate >15% | Fréquence +0.8 achat",
            "budget_estime": "2.5 € / client",
            "roi_estime": "6x",
            "outils": "Braze · Loyalty Lion · Segment.io",
            "tag": "UPGRADE",
            "color": GOLD,
        },
        {
            "titre": "SEO & Contenu Beauté Ciblé",
            "priorite": "LONG TERME",
            "canal": "SEO / Blog / YouTube",
            "timing": "Contenu evergreen + pics saisonniers",
            "segment_cible": "Prospects + clients early-stage",
            "message": "Tutoriels beauté personnalisés selon axe dominant · mots-clés longue traîne par persona",
            "kpis_cibles": "Trafic organique +25% | Temps session >4min | Rebond <40%",
            "budget_estime": "500 € / mois (production)",
            "roi_estime": "15x sur 12 mois",
            "outils": "SEMrush · Contentsquare · Google Search Console",
            "tag": "ACQUISITION",
            "color": GREEN,
        },
    ],

    1: [  # Cluster 1 — VIP / Haute valeur
        {
            "titre": "Programme Beauty Elite — Événements Exclusifs",
            "priorite": "HAUTE",
            "canal": "Invitation physique + Email premium",
            "timing": "Mensuel — 1 événement / mois",
            "segment_cible": "Top 5% CA — VIP confirmés",
            "message": "Invitations masterclass privées avec directrices artistiques, avant-premières collections, accès backstage. Personnalisation extrême : prénom + historique achats dans chaque communication.",
            "kpis_cibles": "Taux réponse invitation >60% | Spend event +40% | NPS >85",
            "budget_estime": "25 € / client / événement",
            "roi_estime": "22x",
            "outils": "Salesforce · Eventbrite VIP · Adobe Personalization",
            "tag": "RETENTION VIP",
            "color": GOLD,
        },
        {
            "titre": "Concierge Beauté Dédié",
            "priorite": "HAUTE",
            "canal": "WhatsApp Business · Téléphone",
            "timing": "Proactif — 72h après dernier achat",
            "segment_cible": "VIP CA > 800€ / an",
            "message": "Conseillère beauté attitrée, recommandations proactives nouveautés, réservation services exclusifs, early access ventes privées. Objectif : relation one-to-one.",
            "kpis_cibles": "CSAT >9/10 | Réachat <30j | CLV +35%",
            "budget_estime": "8 € / client / mois",
            "roi_estime": "18x",
            "outils": "Salesforce Service Cloud · Twilio · Zendesk",
            "tag": "HIGH-TOUCH",
            "color": GOLD,
        },
        {
            "titre": "Cross-sell Sélectif Premium",
            "priorite": "MOYENNE",
            "canal": "Email 1:1 + App",
            "timing": "Post-achat J+3 · récurrence mensuelle",
            "segment_cible": "VIP mono-axe (ex: fragrance pure)",
            "message": "Recommandation d'extension gamme basée sur l'IA : si VIP fragrance → proposer soins corps assortis. Taux de succès cross-sell VIP = 3× supérieur à la moyenne.",
            "kpis_cibles": "Cross-sell rate >22% | AOV +60€",
            "budget_estime": "0.8 € / communication",
            "roi_estime": "28x",
            "outils": "Algolia Recommend · Dynamic Yield · Nosto",
            "tag": "CROSS-SELL",
            "color": GREEN,
        },
    ],

    2: [  # Cluster 2 — Clientèle dormante / à risque churn
        {
            "titre": "Séquence Win-Back — Last Chance",
            "priorite": "HAUTE",
            "canal": "Email + SMS",
            "timing": "Déclencheur : inactivité >120j",
            "segment_cible": "Clients dormants recency >120j",
            "message": "Email 1 : 'Tu nous manques' + top picks personnalisés. Email 2 (J+5) : offre -20% valable 72h. SMS (J+8) : last chance avec code urgence. Arrêt automatique si réachat.",
            "kpis_cibles": "Win-back rate >8% | ROI campagne >5x",
            "budget_estime": "1.8 € / client",
            "roi_estime": "5x",
            "outils": "Klaviyo · Mailchimp · Twilio SMS",
            "tag": "WIN-BACK",
            "color": RED,
        },
        {
            "titre": "Enquête Motif Inactivité",
            "priorite": "MOYENNE",
            "canal": "Email court + Survey in-app",
            "timing": "J+90 inactivité — 1 seul envoi",
            "segment_cible": "Dormants 90–150j (récupérables)",
            "message": "Survey 3 questions max : pourquoi l'arrêt ? → prix / assortiment / expérience. Offre de bienvenue retour conditionnée au feedback. Données CRM enrichies.",
            "kpis_cibles": "Taux réponse survey >15% | Data enrichment +40%",
            "budget_estime": "0.5 € / client",
            "roi_estime": "4x (via data)",
            "outils": "Typeform · HubSpot · Google Analytics 4",
            "tag": "INSIGHT",
            "color": GOLD,
        },
        {
            "titre": "Retargeting Paid — Réactivation Digitale",
            "priorite": "LONG TERME",
            "canal": "Meta Ads · Google Display · Pinterest",
            "timing": "Audiences lookalike — continu",
            "segment_cible": "Dormants identifiés + lookalike",
            "message": "Retargeting dynamique avec produits vus/achetés. Séquence d'ads progressive : awareness → consideration → conversion. Exclusion des win-back actifs pour éviter la surpression.",
            "kpis_cibles": "ROAS >4 | CPA <12€ | Fréquence <3/semaine",
            "budget_estime": "3–5 € / client réactivé",
            "roi_estime": "7x",
            "outils": "Meta Business · Google Ads · Meta Pixel",
            "tag": "PAID MEDIA",
            "color": GREEN,
        },
    ],

    3: [  # Cluster 3 — GenZ / Exploratrices jeunes
        {
            "titre": "Stratégie Influenceur & UGC",
            "priorite": "HAUTE",
            "canal": "TikTok · Instagram Reels · YouTube Shorts",
            "timing": "Continu — peaks lundi 19h et samedi 11h",
            "segment_cible": "GenZ 15–25 ans · forte entropie marques",
            "message": "Partenariats micro-influenceurs (10K–100K abonnés) alignés sur les marques du cluster. Encourager l'UGC avec hashtag dédié + récompense points. GRWM (Get Ready With Me) avec produits Sephora.",
            "kpis_cibles": "Reach +300K/mois | Engagement rate >5% | UGC volume +200%",
            "budget_estime": "15K€ / campagne influenceur",
            "roi_estime": "12x (earned media)",
            "outils": "Kolsquare · Upfluence · Bazaarvoice",
            "tag": "INFLUENCE",
            "color": RED,
        },
        {
            "titre": "Beauty Box Découverte Mensuelle",
            "priorite": "HAUTE",
            "canal": "Subscription · App",
            "timing": "Abonnement mensuel · personnalisation trimestrielle",
            "segment_cible": "GenZ à forte diversité marques (ICB >70)",
            "message": "Box 5 produits surprise alignée sur préférences IA (axe + marques tendance). Prix : 18€/mois avec valeur perçue 45€+. Gamification : défi 'rate ton look' pour double points.",
            "kpis_cibles": "Abonnement rate >12% | Churn box <8%/mois | ICB uplift +15pts",
            "budget_estime": "3 € / box (marge nette après produits)",
            "roi_estime": "9x sur 6 mois",
            "outils": "Recharge Subscriptions · Shopify · Loyaltylion",
            "tag": "SUBSCRIPTION",
            "color": GOLD,
        },
        {
            "titre": "Gamification In-App — Beauty Challenges",
            "priorite": "MOYENNE",
            "canal": "App Mobile · Push Notifications",
            "timing": "Challenges hebdomadaires · live events",
            "segment_cible": "Utilisateurs app actifs 15–30 ans",
            "message": "Défis beauté hebdomadaires (ex: '3 looks avec 1 palette'), badges collectors, classements communautaires. Récompenses : points doublés, accès early drops, stickers exclusifs.",
            "kpis_cibles": "DAU app +40% | Session duration +3min | Push opt-in >60%",
            "budget_estime": "0.2 € / utilisateur actif",
            "roi_estime": "11x",
            "outils": "Braze Gamification · Firebase · OneSignal",
            "tag": "GAMIFICATION",
            "color": GREEN,
        },
    ],

    4: [  # Cluster 4 — Sensibles aux promotions / Opportunistes
        {
            "titre": "Flash Sales Ciblées — Fenêtres 24h",
            "priorite": "HAUTE",
            "canal": "Email + App Push",
            "timing": "Jeudi 18h (veille week-end) · durée 24h max",
            "segment_cible": "Clients discount_rate >20%",
            "message": "Offre flash exclusive 24h sur l'axe préféré du client. Countdown timer dans l'email. Urgence renforcée par 'X personnes regardent ce produit'. Progressive discount : -15% → -20% les 6 dernières heures.",
            "kpis_cibles": "Taux ouverture email >35% | Conversion >6% | AOV maint. >60€",
            "budget_estime": "15% remise max · 0.5€ opérationnel",
            "roi_estime": "6x",
            "outils": "Klaviyo · Dynamic Yield · Fastly CDN",
            "tag": "PROMO CIBLÉE",
            "color": RED,
        },
        {
            "titre": "Programme Anti-Cannibalisation",
            "priorite": "MOYENNE",
            "canal": "A/B Test Email",
            "timing": "Continu — test & learn mensuel",
            "segment_cible": "Promo-sensibles risquant l'achat plein prix 0%",
            "message": "Tester des incentives non-prix (early access, personnalisation, expérience) pour réduire la dépendance aux remises. Objectif : déplacer 15% des acheteurs promo vers achat plein prix.",
            "kpis_cibles": "discount_rate -3pp sur 6 mois | Marge +4pp",
            "budget_estime": "0.3 € / test / client",
            "roi_estime": "10x (via marge récupérée)",
            "outils": "Optimizely · VWO · Salesforce A/B",
            "tag": "MARGE",
            "color": GOLD,
        },
        {
            "titre": "Cross-sell Complémentaires Hors Promo",
            "priorite": "LONG TERME",
            "canal": "Email personnalisé · Recommandation on-site",
            "timing": "Post-achat J+1 · recommandation J+7",
            "segment_cible": "Promo-sensibles avec mono-achat récent",
            "message": "Après achat promo, recommander produit complémentaire plein prix avec valeur démontrée. Ex : fond de teint en promo → recommander pinceau assorti plein tarif avec tutoriel.",
            "kpis_cibles": "Attach rate >18% | AOV bundle +35€",
            "budget_estime": "0.4 € / recommandation",
            "roi_estime": "8x",
            "outils": "Nosto · Algolia · Salesforce Recommendations",
            "tag": "CROSS-SELL",
            "color": GREEN,
        },
    ],

    5: [  # Cluster 5 — Loyalistes Fragrance/Selective
        {
            "titre": "Programme Connaisseur — Parfum Premium",
            "priorite": "HAUTE",
            "canal": "Email éditorial + Invitation physique",
            "timing": "Nouveau lancement + anniversaire client",
            "segment_cible": "Loyalistes FRAGRANCE · pct_selective >60%",
            "message": "Newsletter mensuelle 'Les Voûtes Olfactives' : storytelling maison de parfum, rencontre créateur, coffret exclusif numéroté. Invitation soirée olfactive en boutique sélective.",
            "kpis_cibles": "Open rate >42% | Achat exclusif >30% | Panier moy. +80€",
            "budget_estime": "4 € / client / mois",
            "roi_estime": "20x",
            "outils": "Klaviyo Premium · Eventbrite · Salesforce",
            "tag": "EXCLUSIVITÉ",
            "color": GOLD,
        },
        {
            "titre": "Éditions Limitées & Numérotées",
            "priorite": "HAUTE",
            "canal": "Email 1:1 + Boutique physique",
            "timing": "Avant lancement public — 48h d'avance",
            "segment_cible": "VIP Fragrance (CA fragrance >500€/an)",
            "message": "Accès prioritaire aux éditions limitées des maisons sélectives. Personnalisation du coffret (gravure, message), livraison premium. Sentiment de rareté absolue.",
            "kpis_cibles": "Sell-out <48h | Prix premium accepté | NPS >90",
            "budget_estime": "6 € / client (curation + logistique)",
            "roi_estime": "25x",
            "outils": "Shopify Plus · ShipBob Premium · Salesforce Commerce",
            "tag": "RARETÉ",
            "color": GOLD,
        },
        {
            "titre": "Extension Selective → Skincare Premium",
            "priorite": "LONG TERME",
            "canal": "Email éducatif · Consultation en boutique",
            "timing": "Post-achat fragrance J+14",
            "segment_cible": "Mono-axe fragrance avec tenure >180j",
            "message": "Initier les loyalistes fragrance au skincare des mêmes maisons (La Mer, Sisley, Chanel Skincare). Argument olfactif : 'Les parfums durent mieux sur peau hydratée'. Diagnostic gratuit en boutique.",
            "kpis_cibles": "Taux extension >20% | Diversité axes +0.8",
            "budget_estime": "2 € / consultation",
            "roi_estime": "16x sur 12 mois",
            "outils": "Salesforce · Appointy · Adobe Journey",
            "tag": "EXTENSION",
            "color": GREEN,
        },
    ],

    6: [  # Cluster 6 — Skincare Addicts
        {
            "titre": "Diagnostic Peau IA + Recommandation Parcours",
            "priorite": "HAUTE",
            "canal": "App Mobile · Kiosk boutique",
            "timing": "À chaque visite / renouvellement saisonnier",
            "segment_cible": "Skincare >50% CA · recency <60j",
            "message": "Outil de diagnostic peau (teint, hydratation, rides) → parcours produits personnalisé 3 étapes. Routine évolutive avec rappels J+30 / J+60. Suivi résultats photo.",
            "kpis_cibles": "Routine compliance >45% | CA skincare +30% | Satisfaction >8.5/10",
            "budget_estime": "0.5 € / diagnostic",
            "roi_estime": "14x",
            "outils": "Revieve AI · Sephora Virtual Artist · Braze",
            "tag": "PERSONNALISATION",
            "color": GREEN,
        },
        {
            "titre": "Abonnement Routine Automatisée",
            "priorite": "HAUTE",
            "canal": "App · Email · Subscription",
            "timing": "Selon durée produit (28j / 60j / 90j)",
            "segment_cible": "Skincare réguliers (fréquence >4/an)",
            "message": "Livraison automatique à fréquence personnalisée selon produit. Prix abonné -10%, livraison offerte, swap facile. Upsell : ajouter 1 soin nouveau par cycle pour 'tester avant les autres'.",
            "kpis_cibles": "Subscription rate >20% | Churn sub <6% | LTV ×2.5",
            "budget_estime": "2 € / abonné actif / mois",
            "roi_estime": "19x",
            "outils": "Recharge · Bold Subscriptions · Klaviyo",
            "tag": "SUBSCRIPTION",
            "color": GOLD,
        },
        {
            "titre": "Content — Education Ingrédients & Formulation",
            "priorite": "MOYENNE",
            "canal": "Instagram · YouTube · Blog SEO",
            "timing": "Séries éducatives bi-hebdomadaires",
            "segment_cible": "Skincare passionnés · ICB >60",
            "message": "Contenus deep-dive : 'Tout sur le rétinol', 'Niacinamide vs Vitamine C', guides layering. Positionnement expert vs concurrents généralistes. Calls-to-action vers les produits associés.",
            "kpis_cibles": "Engagement >7% | Saves Instagram >15% | SEO rank top-3",
            "budget_estime": "300 € / contenu expert",
            "roi_estime": "13x (earned + direct)",
            "outils": "Contentsquare · SEMrush · Later",
            "tag": "ÉDUCATION",
            "color": RED,
        },
    ],

    7: [  # Cluster 7 — Omnicanaux / Multicanaux
        {
            "titre": "Programme Omnicanal Unifié — 'Seamless Beauty'",
            "priorite": "HAUTE",
            "canal": "App + Store + Web",
            "timing": "Intégration permanente — trigger comportemental",
            "segment_cible": "Clients is_omnichannel=1 · actifs 2+ canaux",
            "message": "Expérience unifiée : panier partagé online/offline, historique visible en boutique par conseillère, 'reserve online → essai en boutique → livraison domicile'. Récompense bonus omnicanal +50 points / passage canal.",
            "kpis_cibles": "Taux omnicanal +8pp | CA +45% vs mono-canal | NPS +12pts",
            "budget_estime": "1.5 € / client / mois (plateforme)",
            "roi_estime": "20x",
            "outils": "Salesforce Commerce · Adobe Experience · Stripe",
            "tag": "OMNICANAL",
            "color": GREEN,
        },
        {
            "titre": "Conseillère Beauté Hybride — Click & Consult",
            "priorite": "MOYENNE",
            "canal": "Visio · App · Store",
            "timing": "Sur réservation · créneaux 12h–14h & 19h–21h",
            "segment_cible": "Omnicanaux premium (CA >250€)",
            "message": "Consultation beauté hybride : vidéo avec conseillère, AR try-on, suivi en boutique. Personnalisation poussée basée sur l'historique complet (online + offline). Conversion visio→achat = 35%.",
            "kpis_cibles": "Conversion consultation >35% | AOV consultation +120€",
            "budget_estime": "8 € / consultation (conseillère)",
            "roi_estime": "15x",
            "outils": "Zoom SDK · Sephora Virtual Artist · Calendly",
            "tag": "HYBRIDE",
            "color": GOLD,
        },
        {
            "titre": "Gamification Cross-Canal — Points Bonus",
            "priorite": "MOYENNE",
            "canal": "App · Email · Notification push",
            "timing": "Défis mensuels cross-canal",
            "segment_cible": "Omnicanaux en risque de mono-canalisation",
            "message": "Défis mensuels qui nécessitent les deux canaux : 'Essaie en boutique + commande online = 200 points bonus'. Storyline gamifiée sur l'année. Objectif : maintenir la bivalence canal.",
            "kpis_cibles": "Bivalence canal maintenue >85% | Engagement défi >30%",
            "budget_estime": "0.6 € / défi / client",
            "roi_estime": "12x",
            "outils": "Braze · Loyaltylion · Firebase",
            "tag": "GAMIFICATION",
            "color": RED,
        },
    ],

    8: [  # Cluster 8 — Clients occasionnels / Faible fréquence
        {
            "titre": "Nurturing Progressif — Montée en Fréquence",
            "priorite": "HAUTE",
            "canal": "Email · App Push",
            "timing": "Séquence 12 semaines post-achat",
            "segment_cible": "Clients 1–2 achats/an · recency <90j",
            "message": "Séquence onboarding 12 semaines : semaine 1 guide beauté personnalisé, semaines 2–4 tips quotidiens, semaine 6 offre discovery, semaine 12 bilan et challenge. Objectif : 3e achat dans les 90j.",
            "kpis_cibles": "3e achat rate >20% | Fréquence 0.8→1.5/an",
            "budget_estime": "2.2 € / client séquencé",
            "roi_estime": "7x",
            "outils": "Klaviyo Flows · Braze Canvas · Segment CDP",
            "tag": "NURTURING",
            "color": GOLD,
        },
        {
            "titre": "Offre Bienvenue Retour — Seuil Déclencheur",
            "priorite": "HAUTE",
            "canal": "Email transactionnel",
            "timing": "Si inactivité >60j et <1 an",
            "segment_cible": "Occasionnels avec potentiel (avg_basket >50€)",
            "message": "Offre 'bon retour' -12% sans minimum + livraison offerte. Personnalisation sur l'axe du dernier achat. Limite : 1 utilisation, valide 10j. Tracking précis de la réattribution.",
            "kpis_cibles": "Réachat rate >14% | Time-to-purchase <7j",
            "budget_estime": "1.5 € + valeur remise",
            "roi_estime": "5x",
            "outils": "Mailchimp · WooCommerce · Segment",
            "tag": "RÉACTIVATION",
            "color": RED,
        },
        {
            "titre": "Référencement & Parrainage",
            "priorite": "LONG TERME",
            "canal": "Email · App · Partage social",
            "timing": "Post premier achat J+3",
            "segment_cible": "Occasionnels satisfaits (dernier achat non retourné)",
            "message": "Programme parrainage : parrain et filleul reçoivent 15€ offerts dès 50€ d'achat. Suivi des parrainages actifs, gamification du nb de filleuls actifs. LTV d'un client parrainé = 1.8× supérieure.",
            "kpis_cibles": "Parrainage rate >8% | CAC réduit -30% | LTV filleul 1.8×",
            "budget_estime": "15 € / parrainage réussi",
            "roi_estime": "9x (LTV ajustée)",
            "outils": "ReferralHero · Friendbuy · Klaviyo",
            "tag": "ACQUISITION",
            "color": GREEN,
        },
    ],
}


def marketing_recommendation_card(reco: dict) -> str:
    """Carte HTML enrichie pour une recommandation marketing."""
    priority_colors = {"HAUTE": RED, "MOYENNE": GOLD, "LONG TERME": GREEN}
    pri_color = priority_colors.get(reco["priorite"], GOLD)
    accent    = reco.get("color", GOLD)
    return f"""
<div style="
    background:{DARK_BG};border:1px solid {BORDER};
    border-left:3px solid {accent};
    padding:1.2rem 1.5rem;margin:0.8rem 0;
    animation:fadeInUp 0.5s ease forwards;
">
    <div style="display:flex;justify-content:space-between;
                align-items:flex-start;margin-bottom:0.8rem">
        <div>
            <span style="
                font-family:'DM Mono',monospace;font-size:0.55rem;
                letter-spacing:0.2em;color:{accent};
                text-transform:uppercase;
                background:{accent}18;
                padding:2px 8px;margin-right:8px;
            ">{reco["tag"]}</span>
            <span style="
                font-family:'DM Mono',monospace;font-size:0.55rem;
                letter-spacing:0.15em;color:{pri_color};
                text-transform:uppercase;
                border:1px solid {pri_color};padding:2px 8px;
            ">PRIORITÉ {reco["priorite"]}</span>
        </div>
        <span style="
            font-family:'DM Mono',monospace;font-size:0.62rem;
            color:{GOLD};letter-spacing:0.1em;white-space:nowrap;
        ">ROI {reco["roi_estime"]}</span>
    </div>

    <div style="
        font-family:'Jost',sans-serif;
        font-size:1.05rem;font-weight:400;
        color:#F5F0EB;margin-bottom:0.8rem;
    ">{reco["titre"]}</div>

    <div style="display:grid;grid-template-columns:1fr 1fr;
                gap:0.5rem;margin-bottom:0.8rem">
        <div>
            <div style="font-family:'DM Mono',monospace;font-size:0.48rem;
                        letter-spacing:0.15em;color:#555;text-transform:uppercase;
                        margin-bottom:2px">Canal</div>
            <div style="font-family:'Jost',sans-serif;font-size:0.78rem;
                        color:{GOLD}">{reco["canal"]}</div>
        </div>
        <div>
            <div style="font-family:'DM Mono',monospace;font-size:0.48rem;
                        letter-spacing:0.15em;color:#555;text-transform:uppercase;
                        margin-bottom:2px">Timing</div>
            <div style="font-family:'Jost',sans-serif;font-size:0.78rem;
                        color:#AAAAAA">{reco["timing"]}</div>
        </div>
        <div>
            <div style="font-family:'DM Mono',monospace;font-size:0.48rem;
                        letter-spacing:0.15em;color:#555;text-transform:uppercase;
                        margin-bottom:2px">Budget / client</div>
            <div style="font-family:'DM Mono',monospace;font-size:0.78rem;
                        color:#F5F0EB">{reco["budget_estime"]}</div>
        </div>
        <div>
            <div style="font-family:'DM Mono',monospace;font-size:0.48rem;
                        letter-spacing:0.15em;color:#555;text-transform:uppercase;
                        margin-bottom:2px">Segment ciblé</div>
            <div style="font-family:'Jost',sans-serif;font-size:0.78rem;
                        color:#AAAAAA">{reco["segment_cible"]}</div>
        </div>
    </div>

    <div style="
        font-family:'Jost',sans-serif;font-size:0.77rem;
        color:#999;line-height:1.65;padding:0.65rem;
        background:#050505;border-left:2px solid {accent}40;
        margin-bottom:0.8rem;
    ">{reco["message"]}</div>

    <div style="display:flex;justify-content:space-between;align-items:center;
                flex-wrap:wrap;gap:0.4rem">
        <div style="font-family:'DM Mono',monospace;font-size:0.52rem;
                    color:#444;letter-spacing:0.06em">
            KPIs : {reco["kpis_cibles"]}
        </div>
        <div style="font-family:'DM Mono',monospace;font-size:0.5rem;
                    color:#333;letter-spacing:0.06em">
            {reco["outils"]}
        </div>
    </div>
</div>"""
