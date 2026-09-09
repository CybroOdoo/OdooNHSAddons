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
from datetime import timedelta

from odoo import fields
from odoo.tests.common import tagged

from .common import NhsTrainingCommon


@tagged('post_install', '-at_install')
class TestCompliance(NhsTrainingCommon):
    """Member-level compliance counts, percentage, status and exemptions."""

    def test_not_done_is_non_compliant(self):
        """A member with a required subject and no record is 0% / non-compliant."""
        self.assertEqual(self.member.required_subject_count, 1)
        self.assertEqual(self.member.compliant_subject_count, 0)
        self.assertEqual(self.member.compliance_pct, 0.0)
        self.assertEqual(self.member.compliance_status, 'non_compliant')

    def test_compliant_after_completion(self):
        """Completing the required subject makes the member 100% / compliant."""
        self._record()
        self.assertEqual(self.member.compliant_subject_count, 1)
        self.assertEqual(self.member.compliance_pct, 100.0)
        self.assertEqual(self.member.compliance_status, 'compliant')

    def test_expired_counts_and_status(self):
        """An expired required subject counts as expired and non-compliant."""
        old = fields.Date.context_today(self.Record) - timedelta(days=400)
        self._record(completion_date=old)
        self.assertEqual(self.member.expired_subject_count, 1)
        self.assertEqual(self.member.compliant_subject_count, 0)
        self.assertEqual(self.member.compliance_status, 'non_compliant')

    def test_failed_counts(self):
        """A failed latest attempt counts as failed and is not compliant."""
        self._record(result='fail')
        self.assertEqual(self.member.failed_subject_count, 1)
        self.assertEqual(self.member.compliant_subject_count, 0)

    def test_exempt_excluded_from_denominator(self):
        """A waived subject is exempt and drops out of the required count."""
        self.Requirement.create({
            'member_id': self.member.id, 'subject_id': self.subj_annual.id,
            'override_type': 'waive', 'exemption_reason': 'Secondment'})
        self.assertEqual(self.member.required_subject_count, 0)
        # No required subjects → treated as 100% compliant.
        self.assertEqual(self.member.compliance_pct, 100.0)

    def test_compliance_line_sync(self):
        """compliance_line_ids mirror the resolved subjects and their statuses."""
        self._record()
        # compliance_line_ids is populated as a side effect of the stored
        # compliance compute; trigger it explicitly before reading the lines.
        self.member._compute_compliance()
        line = self.member.compliance_line_ids.filtered(
            lambda l: l.subject_id == self.subj_annual)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.status, 'compliant')

    def test_at_risk_band(self):
        """Between (target-15) and target the member is 'at_risk'."""
        # Require two subjects, meet one → 50%. Lower target so 50% lands in at-risk.
        self.Requirement.create({
            'profile_id': self.profile.id, 'subject_id': self.subj_extra.id})
        self.env['ir.config_parameter'].sudo().set_param(
            'odoo_nhs_training.compliance_target', 60)
        self._record()  # meet the annual subject only
        self.member.invalidate_recordset()
        self.member._compute_compliance()
        self.assertEqual(self.member.required_subject_count, 2)
        self.assertEqual(self.member.compliance_pct, 50.0)
        self.assertEqual(self.member.compliance_status, 'at_risk')

    def test_is_training_compliant_api(self):
        """is_training_compliant() is False with an expired subject, True when in date."""
        old = fields.Date.context_today(self.Record) - timedelta(days=400)
        rec = self._record(completion_date=old)
        self.assertFalse(self.member.is_training_compliant())
        # A fresh completion supersedes the expired one.
        self._record()
        self.assertTrue(self.member.is_training_compliant())

    def test_leaver_excluded(self):
        """A leaver is treated as compliant (excluded from live compliance)."""
        self.member.is_leaver = True
        self.member._compute_compliance()
        self.assertEqual(self.member.compliance_status, 'compliant')
