# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': 'NHS Backoffice Management Core',
    'summary': 'One-click installer for the complete NHS Backoffice suite — '
               'Trust management, ODS sync, governance, incidents & risk, '
               'complaints, DSPT, workforce, recruitment, training and estate. '
               'NHS, Odoo NHS',
    'description': """
Bundle module for the NHS Backoffice suite. Installing it installs
every NHS module and adds a single "NHS Backoffice Administrator" group that
grants full management access across the whole suite.
""",
    'version': '19.0.1.0.0',
    'category': 'Services',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'license': 'LGPL-3',
    'depends': [
        # Trust & organisation
        'odoo_nhs_trust_management',
        'odoo_nhs_trust_operations',
        'odoo_nhs_trust_reports',
        'odoo_nhs_ods_sync',
        'odoo_nhs_uk_regions',
        # Governance & clinical quality
        'odoo_nhs_governance',
        'odoo_nhs_incident_risk',
        'odoo_nhs_complaints',
        'odoo_nhs_dspt',
        # Workforce
        'odoo_nhs_establishment',
        'odoo_nhs_recruitment',
        'odoo_nhs_training',
        # Estates & facilities
        'odoo_nhs_estate',
    ],
    'data': [
        'security/nhs_core_security.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'application': True,
    'installable': True,
    'auto_install': False,
}
