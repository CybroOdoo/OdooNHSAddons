.. image:: https://img.shields.io/badge/license-LGPL--3-green.svg
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

NHS Establishment Register
==========================
The master record of an organisation's FUNDED POSTS — the budgeted shape of the
workforce, defined in positions rather than people. Tracks the funded
establishment against staff actually in post, exposing the vacancy gap that
drives recruitment, safe staffing and pay-budget planning. Foundation of the
NHS Workforce suite, for Odoo 19 Community and Enterprise.

Features
========
* **Funded-post register** — every establishment post held as funded vs in-post
  vs vacant FTE, by team, Agenda for Change band, staff group and cost centre.
* **Organisational hierarchy** — unlimited-depth directorate → division →
  department → team structure (web_hierarchy), with FTE and vacancy figures
  rolled up recursively to every level.
* **Vacancy tracking** — automatic vacancy status (fully staffed / part vacant /
  fully vacant / over-established), vacancy start date and days-vacant ageing,
  with a nightly reminder cron for long-standing vacancies.
* **Agenda for Change bands & staff groups** — customer-maintained indicative
  band salaries and the standard NHS staff-group classification, driving
  indicative pay-cost estimates (band salary × FTE × on-cost factor).
* **Cost centres & budgets** — annual pay budget per cost centre with indicative
  spend, budget variance and utilisation rolled up from the posts charged to it.
* **Establishment change control** — protected edits to funded FTE, band or team
  must be raised as an Establishment Change Request, with a two-stage
  (workforce → finance) or single-stage approval workflow and an indicative cost
  impact shown to approvers before sign-off. Change types: create / delete post,
  increase / decrease FTE, re-band, transfer between teams.
* **Medical / Non-AfC posts** — posts outside Agenda for Change priced from a
  manual indicative salary.
* **Interactive dashboard** — funded/in-post/vacant KPIs, vacancy hotspots,
  staff-group and band breakdowns, and cost-centre budget utilisation.
* **Reports** — Establishment report and Vacancy Register (QWeb PDF), plus
  guided spreadsheet import templates for org units and posts.
* **Role-based security** — Workforce User (read-only), Workforce Officer
  (maintain posts / raise changes) and Workforce Manager (approve changes and
  configure), with per-company record-rule scoping.

Configuration
=============
Settings → NHS Establishment:

* **Full-Time Hours Basis** — weekly hours counted as 1.0 FTE (NHS standard 37.5).
* **On-Cost Factor** — multiplier applied to indicative salary to approximate
  total employment cost (e.g. 1.2 adds 20%).
* **Require Establishment Change Control** — force funded-FTE / band / team edits
  through a change request rather than direct editing.
* **Single-Stage Approval** — allow workforce approval alone to apply a change
  (finance approval skipped) for smaller providers.

Company
-------
* `Cybrosys Techno Solutions <https://cybrosys.com/>`__

License
-------
General Public License, Version 3 (LGPL v3).
(http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

Credits
=======
Developer: (V19) Nubla Sherin K ,

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
