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
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import tagged

from .common import NhsDsptCommon


@tagged('post_install', '-at_install')
class TestEvidence(NhsDsptCommon):
    """Evidence line behaviour: status setters, N/A reason, locking, deletion."""

    def test_set_met_stamps_review_date(self):
        """Marking evidence Met defaults the review date to today when unset."""
        ev = self._ev('1.1.1')
        self.assertFalse(ev.evidence_review_date)
        ev.action_set_met()
        self.assertEqual(ev.status, 'met')
        self.assertEqual(ev.evidence_review_date, fields.Date.context_today(ev))

    def test_set_met_keeps_existing_review_date(self):
        """A pre-set review date is preserved when marking Met."""
        ev = self._ev('1.1.2')
        ev.evidence_review_date = '2026-01-01'
        ev.action_set_met()
        self.assertEqual(str(ev.evidence_review_date), '2026-01-01')

    def test_not_applicable_requires_reason(self):
        """Marking evidence Not Applicable without a reason is rejected."""
        ev = self._ev('1.1.1')
        with self.assertRaises(ValidationError):
            ev.action_set_not_applicable()
        ev.na_reason = 'Handled by parent org'
        ev.action_set_not_applicable()
        self.assertEqual(ev.status, 'not_applicable')

    def test_evidence_cannot_be_deleted(self):
        """Evidence lines are managed by generation and cannot be manually deleted."""
        with self.assertRaises(UserError):
            self._ev('1.1.1').unlink()

    def test_locked_when_published(self):
        """Once published, non-managers cannot edit evidence."""
        self._meet_all_mandatory()
        self.assessment.action_publish()
        self.assertEqual(self.assessment.state, 'published')
        ev = self._ev('1.1.1')
        with self.assertRaises(UserError):
            ev.with_user(self.user_officer).write({'answer': 'late edit'})
        # A manager can still edit (re-open path).
        ev.with_user(self.user_manager).write({'answer': 'manager edit'})
        self.assertEqual(ev.answer, 'manager edit')

    def test_owner_only_edit_for_plain_user(self):
        """A plain DSPT user can edit only evidence assigned to them."""
        mine = self._ev('1.1.1')
        mine.owner_id = self.user_plain
        not_mine = self._ev('1.1.2')
        not_mine.owner_id = self.user_officer
        # Own item: allowed.
        mine.with_user(self.user_plain).write({'answer': 'done by me'})
        self.assertEqual(mine.answer, 'done by me')
        # The owner record-rule hides other people's items from a plain user
        # (search applies record rules; exists() would not).
        visible = self.Evidence.with_user(self.user_plain).search(
            [('assessment_id', '=', self.assessment.id)])
        self.assertIn(mine, visible)
        self.assertNotIn(not_mine, visible)
