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
from datetime import date, timedelta

from freezegun import freeze_time

from odoo import fields
from odoo.tests.common import tagged

from .common import NhsDsptCommon


@tagged('post_install', '-at_install')
class TestReadiness(NhsDsptCommon):
    """Readiness %, achieved_status, gaps, assertion status, staleness."""

    def test_initial_not_met(self):
        """A freshly generated assessment reads 0% and 'Standards Not Met'."""
        self.assertEqual(self.assessment.readiness_pct, 0.0)
        self.assertEqual(self.assessment.achieved_status, 'not_met')

    def test_all_met_gives_standards_met(self):
        """Meeting every mandatory item gives 100% and 'Standards Met'."""
        self._meet_all_mandatory()
        self.assertEqual(self.assessment.readiness_pct, 100.0)
        self.assertEqual(self.assessment.achieved_status, 'standards_met')
        self.assertEqual(self.assessment.gap_count, 0)

    def test_partial_readiness_percentage(self):
        """readiness_pct = mandatory met / mandatory total."""
        mandatory = self._mandatory()          # 18 items
        for ev in mandatory[:9]:
            ev.action_set_met()
        self.assertAlmostEqual(self.assessment.readiness_pct, 50.0, places=1)

    def test_gap_and_plan_in_place(self):
        """A not-met mandatory item is a gap; covering it with an action → plan_in_place."""
        mandatory = self._mandatory()
        for ev in mandatory[1:]:
            ev.action_set_met()
        gap = mandatory[0]
        gap.action_set_not_met()
        self.assertEqual(self.assessment.gap_count, 1)
        self.assertIn(gap, self.assessment.gap_evidence_ids)
        # Raise an action covering the gap -> achieved_status becomes plan_in_place.
        self.Action.create({
            'assessment_id': self.assessment.id,
            'evidence_id': gap.id,
            'name': 'Close the gap',
            'owner_id': self.env.user.id,
            'target_date': fields.Date.today(),
        })
        self.assertEqual(self.assessment.achieved_status, 'plan_in_place')

    def test_approaching_status(self):
        """Above the approaching threshold (default 80%) but not complete → approaching."""
        mandatory = self._mandatory()          # 18
        for ev in mandatory[:16]:              # ~88.9%
            ev.action_set_met()
        self.assertGreaterEqual(self.assessment.readiness_pct, 80.0)
        self.assertEqual(self.assessment.achieved_status, 'approaching')

    def test_not_applicable_excluded_from_readiness(self):
        """Not-applicable mandatory items drop out of the readiness denominator."""
        total_before = len(self._mandatory())
        ev = self._mandatory()[0]
        ev.na_reason = 'Not relevant to this org'
        ev.action_set_not_applicable()
        self.assertEqual(len(self._mandatory()), total_before - 1)

    def test_assertion_status_rollup(self):
        """An assertion is 'met' once all its mandatory evidence is met, 'not_met'
        if any mandatory evidence is not met."""
        assertion = self._ev('2.1.1').assertion_id
        self._ev('2.1.1').action_set_met()
        self._ev('2.1.2').action_set_met()
        self.assertEqual(assertion.status, 'met')
        self._ev('2.1.2').action_set_not_met()
        self.assertEqual(assertion.status, 'not_met')

    def test_stale_evidence(self):
        """A met item whose review date is older than the stale window is flagged stale."""
        ev = self._ev('1.1.1')
        with freeze_time('2026-01-15'):
            ev.action_set_met()
            ev.evidence_review_date = date(2024, 1, 1)  # >12 months before
            ev._compute_is_stale()
            self.assertTrue(ev.is_stale)
            self.assertEqual(self.assessment.stale_evidence_count, 1)
