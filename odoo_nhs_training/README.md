.. image:: https://img.shields.io/badge/license-LGPL--3-green.svg
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

NHS Mandatory Training Register
===============================
Statutory and mandatory training compliance for the NHS — turning the training-
matrix spreadsheet into a live, role-driven compliance system. Tracks whether
every member of staff holds the training their role requires and whether it is
still in date, for Odoo 19 Community and Enterprise.

Features
========
* **CSTF-aligned training subjects** — statutory / mandatory / role-specific /
  local subjects, optionally levelled (e.g. Safeguarding Level 1/2/3), each with
  a refresh interval, one-off flag and due-soon window.
* **Role-based requirements** — bundle requirements into Requirement Profiles
  assigned to establishment posts, or attach them to a whole staff group, with
  individual add/waive overrides and exemptions per member.
* **Automatic requirement resolution** — each member's required set is resolved
  from their profile, staff group and individual overrides; the record-training
  screen is restricted to that resolved set.
* **Completion & expiry tracking** — record completions with method, provider,
  certificate and evidence; expiry is derived from the completion date and the
  effective refresh interval (with manual-override and per-record frequency),
  giving a live compliant / due-soon / expired / failed status.
* **Professional registration** — track NMC/GMC/HCPC/GPhC/GDC registrations with
  expiry, revalidation and current/expiring-soon/lapsed status.
* **Compliance engine** — per-member compliance %, status (compliant / at risk /
  non-compliant) against a board-set target, with team and organisation roll-ups
  through the establishment hierarchy.
* **Training Matrix & Compliance Dashboard** — the signature members × subjects
  colour-coded matrix, plus a dashboard of weakest subjects/teams, due-soon and
  expired registers and lapsed registrations.
* **Reminders & escalation** — nightly member reminders and manager to-do
  activities for due-soon/expired training, low-compliance team escalation and a
  weekly compliance digest.
* **Reports** — training matrix, board report, individual record and completion
  certificate. Plus a stable ``is_training_compliant()`` API for rostering/bank
  modules.
* **Role-based security** — Viewer (read-only), Officer (record training, manage
  members/requirements) and Manager (configure subjects/profiles and manage
  everything), with per-company scoping and portal self-view.

Configuration
=============
Settings → NHS Training:

* **Training Due Soon Window (Days)** — default lead time before a professional
  registration is flagged expiring soon (subjects carry their own window).
* **Compliance Target (%)** — the board-set target member/team/organisation
  compliance is measured against.
* **Training Digest Recipients** — fallback email addresses for the weekly digest.

Company
-------
* `Cybrosys Techno Solutions <https://cybrosys.com/>`__

License
-------
General Public License, Version 3 (LGPL v3).
(http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

Credits
=======
Developer: (V19) Cybrosys Techno Solutions

Contact: odoo@cybrosys.com

Contacts
--------
* Mail Contact : odoo@cybrosys.com
* Website : https://cybrosys.com

Bug Tracker
-----------
Bugs are tracked on GitHub Issues. In case of trouble, please check there if your issue has already been reported.

Maintainer
==========
.. image:: https://cybrosys.com/images/logo.png
   :target: https://cybrosys.com

This module is maintained by Cybrosys Technologies.

For support and more information, please visit `Our Website <https://cybrosys.com/>`__

Further information
===================
HTML Description: `<static/description/index.html>`__
