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
"""Smoke tests for the NHS Backoffice Core bundle."""
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

NHS_MODULES = [
    'odoo_nhs_trust_management',
    'odoo_nhs_trust_operations',
    'odoo_nhs_trust_reports',
    'odoo_nhs_ods_sync',
    'odoo_nhs_uk_regions',
    'odoo_nhs_governance',
    'odoo_nhs_incident_risk',
    'odoo_nhs_complaints',
    'odoo_nhs_dspt',
    'odoo_nhs_establishment',
    'odoo_nhs_recruitment',
    'odoo_nhs_training',
    'odoo_nhs_estate',
]

TOP_GROUPS = [
    'odoo_nhs_trust_management.group_nhs_trust_admin',
    'odoo_nhs_ods_sync.group_nhs_ods_sync_operator',
    'odoo_nhs_governance.group_nhs_gov_manager',
    'odoo_nhs_incident_risk.group_hc_quality_lead',
    'odoo_nhs_incident_risk.group_hc_safeguarding',
    'odoo_nhs_complaints.group_nhs_complaint_quality_lead',
    'odoo_nhs_dspt.group_nhs_dspt_manager',
    'odoo_nhs_establishment.group_nhs_workforce_manager',
    'odoo_nhs_recruitment.group_nhs_recruit_manager',
    'odoo_nhs_training.group_nhs_training_manager',
    'odoo_nhs_estate.group_nhs_estate_manager',
]


@tagged('post_install', '-at_install')
class TestNhsCoreBundle(TransactionCase):

    def test_all_suite_modules_installed(self):
        """Installing the core bundle installs every NHS module."""
        modules = self.env['ir.module.module'].search([('name', 'in', NHS_MODULES)])
        self.assertEqual(set(modules.mapped('name')), set(NHS_MODULES))
        not_installed = modules.filtered(lambda m: m.state != 'installed')
        self.assertFalse(not_installed, 'Not installed: %s' % not_installed.mapped('name'))

    def test_admin_group_implies_every_top_group(self):
        """The umbrella group transitively grants each module's top group."""
        admin_group = self.env.ref('odoo_nhs_core.group_nhs_backoffice_admin')
        granted = admin_group.all_implied_ids
        for xmlid in TOP_GROUPS:
            self.assertIn(self.env.ref(xmlid), granted, '%s not implied' % xmlid)

    def test_new_admin_user_gets_full_access(self):
        """A user given only the umbrella group gets manager rights everywhere."""
        user = self.env['res.users'].create({
            'name': 'NHS Suite Admin',
            'login': 'nhs_suite_admin',
            'group_ids': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('odoo_nhs_core.group_nhs_backoffice_admin').id,
            ])],
        })
        for xmlid in TOP_GROUPS:
            self.assertTrue(user.has_group(xmlid), '%s missing on user' % xmlid)
        # Lower tiers come through each module's own implied chain.
        self.assertTrue(user.has_group('odoo_nhs_recruitment.group_nhs_recruit_viewer'))
        self.assertTrue(user.has_group('odoo_nhs_incident_risk.group_hc_reporter'))
