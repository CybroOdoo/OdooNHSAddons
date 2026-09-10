.. image:: https://img.shields.io/badge/license-LGPL--3-green.svg
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

NHS Estate Register
===================
The master inventory of the NHS physical estate — sites, buildings, floors and
functional spaces — with tenure, Six Facet condition surveying and backlog
maintenance tracking. Provides hierarchical roll-ups of GIA and clinical /
non-clinical area splits and an ERIC-aligned function taxonomy. The foundation
of the NHS Estates & Facilities suite, for Odoo 19 Community and Enterprise.

Features
========
* **Estate hierarchy** — Site → Building → Floor → Space, browsable in one
  unified hierarchy view, with GIA and space counts rolled up at every level.
* **Sites** — campuses with type, operational status, address/geolocation, land
  area, parking and a self-referencing parent structure.
* **Buildings** — code, build year/age, storeys, GIA (rolled up from floors,
  plus NIA), predominant function, listed status, tenure and operational status.
* **Floors & spaces** — floors ordered by level (basements negative), spaces
  with function, area, capacity, department, clinical flag and utilisation
  (driving occupied/vacant area analysis).
* **Six Facet condition surveys** — physical, statutory, functional,
  utilisation, quality and energy grades, with a configurable overall roll-up
  (worst grade or weighted average) and the building's latest grade surfaced.
* **Tenure & leases** — freehold / leasehold / PFI / LIFT / NHSPS / CHP /
  licence, with lease term, rent, break clauses, rent-review and expiry flags,
  plus reminder activities.
* **Backlog maintenance** — cost-estimated items by element and risk category,
  with status flow and roll-up to building and site.
* **ERIC-aligned function taxonomy** — hierarchical use classifications with a
  clinical flag and ERIC category codes.
* **Dashboard & reports** — an estate dashboard (GIA, condition, backlog, lease
  expiries, tenure/function breakdowns), an estate register PDF and per-building
  passports.
* **Role-based security** — Viewer (read-only), Officer (maintain the register)
  and Manager (configure reference data and manage everything), with per-company
  record-rule scoping.

Configuration
=============
Settings → NHS Estate:

* **Condition Roll-up Rule** — how the overall Six Facet grade is derived from
  the facet ratings: *Worst Grade* (conservative, default) or *Weighted Average*.

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
