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
"""Shared fixtures for the NHS DSPT Compliance test suite."""
import base64

from odoo.tests.common import TransactionCase


class NhsDsptCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Assessment = cls.env['nhs.dspt.assessment']
        cls.Assertion = cls.env['nhs.dspt.assertion']
        cls.Evidence = cls.env['nhs.dspt.evidence']
        cls.Action = cls.env['nhs.dspt.action']
        cls.Edition = cls.env['nhs.dspt.edition']

        cls.company = cls.env.company

        # Seed framework shipped by the module.
        cls.edition = cls.env.ref('odoo_nhs_dspt.edition_2025_26')
        cls.profile_trust = cls.env.ref('odoo_nhs_dspt.org_profile_trust')
        cls.profile_supplier = cls.env.ref('odoo_nhs_dspt.org_profile_supplier')

        # A generated Trust assessment: 10 assertion lines, 20 evidence lines
        # (all defs except the supplier-only 10.1.3), 18 mandatory-applicable.
        cls.assessment = cls.Assessment.create({
            'edition_id': cls.edition.id,
            'org_profile_id': cls.profile_trust.id,
        })
        cls.assessment.action_generate()

        # ── Groups & users (Odoo 19: group_ids, not groups_id) ────────────
        cls.group_user = cls.env.ref('odoo_nhs_dspt.group_nhs_dspt_user')
        cls.group_officer = cls.env.ref('odoo_nhs_dspt.group_nhs_dspt_officer')
        cls.group_manager = cls.env.ref('odoo_nhs_dspt.group_nhs_dspt_manager')

        cls.user_plain = cls.env['res.users'].create({
            'name': 'DSPT User', 'login': 'dspt_user', 'email': 'u@dspt.test',
            'group_ids': [(6, 0, [cls.env.ref('base.group_user').id, cls.group_user.id])],
        })
        cls.user_officer = cls.env['res.users'].create({
            'name': 'DSPT Officer', 'login': 'dspt_officer', 'email': 'o@dspt.test',
            'group_ids': [(6, 0, [cls.env.ref('base.group_user').id, cls.group_officer.id])],
        })
        cls.user_manager = cls.env['res.users'].create({
            'name': 'DSPT Manager', 'login': 'dspt_manager', 'email': 'm@dspt.test',
            'group_ids': [(6, 0, [cls.env.ref('base.group_user').id, cls.group_manager.id])],
        })

    # ── helpers ───────────────────────────────────────────────────────────
    def _ev(self, reference, assessment=None):
        """Return the evidence line on an assessment by its reference (e.g. '1.1.1')."""
        assessment = assessment or self.assessment
        return assessment.evidence_ids.filtered(lambda e: e.reference == reference)

    def _mandatory(self, assessment=None):
        assessment = assessment or self.assessment
        return assessment.evidence_ids.filtered(
            lambda e: e.is_mandatory and e.status != 'not_applicable')

    def _meet_all_mandatory(self, assessment=None):
        """Mark every mandatory-applicable evidence line 'met'."""
        assessment = assessment or self.assessment
        for ev in self._mandatory(assessment):
            ev.action_set_met()

    @staticmethod
    def _attachment(env, name='evidence.pdf'):
        return env['ir.attachment'].create({
            'name': name,
            'datas': base64.b64encode(b'proof'),
        })
