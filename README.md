<div align="center">

# OdooNHSAddons

### NHS-Aligned Solutions Built on Odoo — Manage NHS Back-Office Operations in Odoo

Purpose-built **Odoo 19** modules for NHS trusts and the wider UK health & care sector.
Governance, quality & safety, workforce, procurement, estates and trust management — affordable, open and built around how the NHS actually works.

[![Odoo](https://img.shields.io/badge/Odoo-19.0-714B67)](https://www.odoo.com)
[![Platform](https://img.shields.io/badge/Platform-Community%20%7C%20Enterprise-005EB8)]()
[![Region](https://img.shields.io/badge/Coverage-England%20%7C%20Scotland%20%7C%20Wales%20%7C%20NI-005EB8)]()
[![Maintainer](https://img.shields.io/badge/Maintained%20by-Cybrosys%20Technologies-00843D)](https://www.cybrosys.com)

</div>

---

## Overview

**OdooNHSAddons** is a suite of Odoo modules that bring NHS back-office and governance operations onto a single open-source platform. It is designed for **NHS trusts** and is equally usable across the wider **CQC-registered sector** — GP practices, care homes, hospices and independent providers — wherever the same statutory duties apply.

Each module is self-contained where it can be, and integrates cleanly where it should. No six-figure licences, no vendor lock-in — just NHS-specific tools built natively on Odoo.

---

## Why this suite?

Most NHS back-office functions still run on a mix of expensive single-purpose systems (Datix, CAFM platforms, ESR add-ons) and ad-hoc spreadsheets. OdooNHSAddons offers an alternative:

- **Built for the NHS** — encodes the frameworks that matter: CQC, PSIRF, LFPSE, Duty of Candour, RIDDOR, KO41a, ERIC, Agenda for Change, the NHS 5×5 risk matrix and the Six Facet Survey.
- **Full UK coverage** — England, Scotland, Wales (Local Health Boards) and HSC Northern Ireland.
- **Open and affordable** — built on Odoo Community; no per-seat lock-in.
- **Connected** — an incident can link to a complaint, a risk and a corrective action, all in one system — something standalone tools can't do.
- **No PHI by design** — the suite manages organisational, operational and governance data, not clinical patient records.

---

<div align="center">

## 💬 Let's Talk

**Want a demo, cusomisation, or help choosing the right modules for your trust?**
We'd love to hear from you — get in touch and a member of our NHS team will respond.

<br>

<table>
<tr>
<td align="center" width="50%">

### 📧 Email

**[odoo@cybrosys.com](mailto:odoo@cybrosys.com)**

Send us your requirements and<br>we'll get back to you within 1 Hour.

</td>
<td align="center" width="50%">

### 💚 WhatsApp

**[Chat on WhatsApp](https://wa.me/919074270811)**

Quick questions? Message us directly<br>for a fast, friendly reply.

</td>
</tr>
</table>

<br>

[![Email](https://img.shields.io/badge/Email-odoo@cybrosys.com-005EB8?style=for-the-badge&logo=gmail&logoColor=white)](mailto:odoo@cybrosys.com)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-Chat%20Now-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/919074270811)
[![Website](https://img.shields.io/badge/Website-cybrosys.com-00843D?style=for-the-badge&logo=google-chrome&logoColor=white)](https://www.cybrosys.com)

</div>

---

## Modules

### Trust & Governance

| Module | Technical name | Description |
|---|---|---|
| **NHS Trust Management — Core** | `odoo_nhs_trust_management` | The trust register: structure, sites, departments, governance, board members, workflow, audit and security. The foundation of the suite. |
| **NHS Trust Management — Operations & Compliance** | `odoo_nhs_trust_operations` | Sites, departments, CQC inspection tracking, workforce and financial structure. |
| **NHS Trust Management — Reports & Documents** | `odoo_nhs_trust_reports` | Board-ready Trust Profile PDFs, directory Excel exports and document attachments. |
| **NHS Trust Management — UK Regions Extension** | `odoo_nhs_uk_regions` | Adds NHS Wales (7 Local Health Boards + 3 national trusts) and HSC Northern Ireland (5 HSC Trusts + NIAS) for full UK coverage. |
| **NHS Trust Management — ODS Sync** | `odoo_nhs_ods_sync` | Live synchronisation of the trust register from the NHS Digital Organisation Data Service (ODS) — bulk load, daily delta and conflict resolution. |
| **NHS Incident & Risk Management** | `odoo_nhs_incident_risk` | A Datix-class system: unlimited-reporter incident capture, PSIRF investigations, Duty of Candour, RIDDOR, CQC notifications, LFPSE-ready reporting and a 5×5 risk register with CAPA actions. |
| **NHS Complaints & PALS Management** | `odoo_nhs_complaints` | Statutory complaints handling, PALS concern resolution, KO41a returns and PHSO escalation. Integrates with Incident & Risk. |

### Workforce

| Module | Technical name | Description |
|---|---|---|
| **NHS Workforce Management** | `odoo_nhs_workforce` | Establishment-level workforce management: funded establishment vs in-post FTE, vacancy register, Agenda for Change (AfC) pay-band structure, professional registration tracking (NMC/GMC/HCPC), mandatory & statutory training matrix and safer-staffing levels. Organisational and post-level data only — no personal HR records. |

### Procurement & Supplier

| Module | Technical name | Description |
|---|---|---|
| **NHS Supplier Pack** | `odoo_nhs_supplier_pack` | Supplier and contract management for the NHS: supplier register with compliance tracking (DSPT status, modern slavery statements, Carbon Reduction Plans, Cyber Essentials), framework call-offs, contract register with renewal alerts, and NHS procurement-threshold awareness. |

### Estates & Facilities

| Module | Technical name | Description |
|---|---|---|
| **NHS Estate Register** | `odoo_nhs_estate` | Master register of the physical estate — sites, buildings, floors and spaces, with tenure, Six Facet condition surveys and backlog maintenance. Foundation of the estates track. |
| **NHS Estates Compliance** | `odoo_nhs_estate_compliance` | Statutory compliance scheduling (water/Legionella, fire, electrical, ventilation, asbestos, LOLER, medical gas) on the Odoo maintenance engine. |
| **NHS ERIC Returns** | `odoo_nhs_eric` | Generates the mandatory annual Estates Returns Information Collection from the register and compliance data. |
| **NHS Estate Asset & Equipment** | `odoo_nhs_estate_assets` | Medical-device and equipment register, maintenance/calibration schedules and lifecycle planning. |
| **NHS Energy & Net Zero** | `odoo_nhs_estate_energy` | Energy and utilities tracking, carbon footprint and Green Plan reporting. |

> Each module carries its own `README` with detailed features, dependencies and setup steps.

---

## Architecture at a glance

```
Trust & Governance                        Estates & Facilities
─────────────────────────                 ──────────────────────────
odoo_nhs_trust_management  (core)         odoo_nhs_estate            (foundation)
   ├── odoo_nhs_trust_operations             ├── odoo_nhs_estate_compliance
   ├── odoo_nhs_trust_reports                │      └── odoo_nhs_eric
   ├── odoo_nhs_uk_regions                   ├── odoo_nhs_estate_assets
   └── odoo_nhs_ods_sync                     └── odoo_nhs_estate_energy

odoo_nhs_incident_risk     (standalone)   Workforce / Procurement
   └── odoo_nhs_complaints                   odoo_nhs_workforce
                                             odoo_nhs_supplier_pack
```

The tracks are deliberately modular — different buyers, different Odoo foundations — so they can be adopted, and developed, independently.

---

## Requirements

- **Odoo 19.0** (Community or Enterprise)
- A working Odoo server with access to install custom addons
- Internet access for the ODS Sync module (public NHS Digital directory; no API key required)

Module-level dependencies are declared in each module's `__manifest__.py`. As a rule:

- The Trust Management track builds on **NHS Trust Management — Core**.
- The Estates track builds on **NHS Estate Register**.
- **Incident & Risk** is standalone; **Complaints** depends on it.

---

## Installation

1. Clone this repository into your Odoo addons path:
   ```bash
   git clone https://github.com/<your-org>/OdooNHSAddons.git
   ```
2. Add the path to your Odoo configuration (`addons_path`).
3. Restart the Odoo server and **Update the Apps list** (developer mode enabled).
4. Install the modules you need from **Apps**, starting with the relevant track foundation
   (`odoo_nhs_trust_management` for governance, `odoo_nhs_estate` for estates).

Each module carries its own `README` with detailed setup and first-run steps.

---

## Compliance & frameworks covered

| Area | Frameworks / returns supported |
|---|---|
| Quality & safety | PSIRF, LFPSE, Duty of Candour (CQC Reg 20), NPSA harm grading, Never Events |
| Health & safety | RIDDOR 2013 |
| Regulatory notifications | CQC statutory notifications (Regs 16–18) |
| Complaints | NHS Complaints Regulations 2009, KO41a return, PHSO escalation |
| Risk | NHS 5×5 risk matrix, Board Assurance Framework, three lines of defence |
| Workforce | Agenda for Change pay bands, professional registration (NMC/GMC/HCPC), mandatory training |
| Procurement | Supplier compliance (DSPT, modern slavery, Carbon Reduction Plans), framework call-offs |
| Estates | ERIC return, Six Facet Survey, Premises Assurance Model (PAM), HTM compliance |
| Organisation data | NHS Digital ODS, full UK (England, Scotland, Wales LHBs, HSC NI) |

---

## A note on data & scope

This suite is a **back-office, governance and operational** toolset. It deliberately holds **no Patient Identifiable / clinical record data (PHI)** — incident and complaint records use minimal, data-minimised person information by design, and workforce modules track posts and establishment data, not individual HR records. It is not, and does not replace, an Electronic Patient Record (EPR) or clinical system.

The suite is **NHS-branded** but built to serve the wider CQC-registered sector wherever the same statutory duties apply (care homes, GP practices, hospices, independent providers).

---

## Maintainer

Built and maintained by **[Cybrosys Technologies](https://www.cybrosys.com)**.

For commercial enquiries, support, demos or feature requests - Mail: odoo@cybrosys.com, Whatsapp: +91 9074270811

---

## Licence

Modules in this repository are released under their individual licences (see each module's `__manifest__.py`):

- All modules and its extensions — **LGPL-3**

---

<div align="center">

**Odoo for NHS Back-Office Operations** — by Cybrosys Technologies

*Manage NHS trust structure, operations, governance, incidents, risk, complaints, workforce, procurement and estates — all on Odoo.*

</div>
