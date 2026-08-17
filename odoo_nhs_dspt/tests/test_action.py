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
from odoo.exceptions import ValidationError
from odoo.tests.common import tagged

from .common import NhsDsptCommon


@tagged('post_install', '-at_install')
class TestAction(NhsDsptCommon):
    """Improvement action lifecycle: creation guard, completion, verification."""

    def _gap_action(self, ref='4.1.1'):
        """Mark an evidence item Not Met and raise an action against it."""
        ev = self._ev(ref)
        ev.action_set_not_met()
        return self.Action.create({
            'assessment_id': self.assessment.id,
            'evidence_id': ev.id,
            'name': 'Resolve %s' % ref,
            'owner_id': self.env.user.id,
            'target_date': fields.Date.today() + timedelta(days=14),
        }), ev

    def test_action_reference_sequenced(self):
        """A new action gets a sequenced reference (not left as 'New')."""
        action, _ = self._gap_action()
        self.assertTrue(action.reference and action.reference != 'New')

    def test_action_requires_not_met_evidence(self):
        """An action can only be raised against a Not-Met evidence item."""
        ev = self._ev('1.1.1')
        ev.action_set_met()
        with self.assertRaises(ValidationError):
            self.Action.create({
                'assessment_id': self.assessment.id,
                'evidence_id': ev.id,
                'name': 'Invalid',
                'owner_id': self.env.user.id,
                'target_date': fields.Date.today(),
            })

    def test_complete_requires_note_and_attachment(self):
        """Completing an action needs both a completion note and an attachment."""
        action, _ = self._gap_action()
        with self.assertRaises(ValidationError):
            action.action_mark_completed()
        action.completion_note = 'Policy published'
        with self.assertRaises(ValidationError):
            action.action_mark_completed()
        action.attachment_ids = [(6, 0, self._attachment(self.env).ids)]
        action.action_mark_completed()
        self.assertEqual(action.state, 'completed')

    def test_verify_sets_evidence_met(self):
        """Verifying an action flips its originating gap evidence to Met."""
        action, ev = self._gap_action()
        action.completion_note = 'Done'
        action.attachment_ids = [(6, 0, self._attachment(self.env).ids)]
        action.action_mark_completed()
        action.action_mark_verified()
        self.assertEqual(action.state, 'verified')
        self.assertEqual(ev.status, 'met')

    def test_is_overdue(self):
        """An open action past its target date is overdue; a completed one is not."""
        action, _ = self._gap_action()
        action.target_date = fields.Date.today() - timedelta(days=1)
        action._compute_is_overdue()
        self.assertTrue(action.is_overdue)

    def test_cron_escalate_overdue_schedules_activity(self):
        """The overdue-escalation cron schedules a to-do on the action owner."""
        action, _ = self._gap_action()
        action.target_date = fields.Date.today() - timedelta(days=5)
        self.Action._cron_escalate_overdue()
        activity = self.env['mail.activity'].search([
            ('res_model', '=', 'nhs.dspt.action'),
            ('res_id', '=', action.id),
        ])
        self.assertTrue(activity, 'An escalation activity should be scheduled.')
