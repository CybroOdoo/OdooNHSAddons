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
class TestWorkflow(NhsDsptCommon):
    """Assessment state machine, uniqueness and deletion guards."""

    def test_unique_assessment(self):
        """Only one assessment per edition + org profile + company + ODS code."""
        with self.assertRaises(ValidationError):
            self.Assessment.create({
                'edition_id': self.edition.id,
                'org_profile_id': self.profile_trust.id,
            })

    def test_mark_ready(self):
        """An assessment can be marked Ready."""
        self.assessment.action_mark_ready()
        self.assertEqual(self.assessment.state, 'ready')

    def test_publish_blocked_by_open_actions(self):
        """Publishing is blocked while any improvement action is still open."""
        ev = self._ev('4.1.1')
        ev.action_set_not_met()
        self.Action.create({
            'assessment_id': self.assessment.id, 'evidence_id': ev.id,
            'name': 'Open action', 'owner_id': self.env.user.id,
            'target_date': fields.Date.today(),
        })
        with self.assertRaises(UserError):
            self.assessment.action_publish()

    def test_publish_and_submit(self):
        """A clean assessment publishes, then submits once a reference is entered."""
        self._meet_all_mandatory()
        self.assessment.action_publish()
        self.assertEqual(self.assessment.state, 'published')
        self.assertTrue(self.assessment.published_by_id)
        # Submit requires a portal reference.
        with self.assertRaises(UserError):
            self.assessment.action_submit()
        self.assessment.submission_reference = 'DSPT-REF-123'
        self.assessment.action_submit()
        self.assertEqual(self.assessment.state, 'submitted')
        self.assertTrue(self.assessment.submission_date)

    def test_reopen_manager_only(self):
        """Only a DSPT manager can re-open a published assessment."""
        self._meet_all_mandatory()
        self.assessment.action_publish()
        with self.assertRaises(UserError):
            self.assessment.with_user(self.user_officer).action_reopen()
        self.assessment.with_user(self.user_manager).action_reopen()
        self.assertEqual(self.assessment.state, 'in_progress')

    def test_unlink_only_draft(self):
        """Only draft assessments can be deleted; in-progress must be archived."""
        # self.assessment is in_progress (generated) -> cannot delete.
        with self.assertRaises(UserError):
            self.assessment.unlink()
        draft = self.Assessment.create({
            'edition_id': self.edition.id,
            'org_profile_id': self.profile_supplier.id,
            'ods_code': 'DRAFT-DEL-1',
        })
        self.assertEqual(draft.state, 'draft')
        draft.unlink()  # allowed
        self.assertFalse(draft.exists())
