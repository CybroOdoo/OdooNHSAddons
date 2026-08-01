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
from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import NhsEstablishmentCommon


@tagged('post_install', '-at_install')
class TestChangeControl(NhsEstablishmentCommon):
    """Establishment change-control guard and the approval workflow."""

    def test_direct_edit_of_controlled_field_blocked(self):
        """With change control on, editing funded_fte directly is refused."""
        post = self._make_post(funded_fte=1.0)
        with self.assertRaises(UserError):
            post.funded_fte = 2.0

    def test_direct_edit_allowed_when_control_disabled(self):
        """With change control off, controlled fields can be edited directly."""
        self.company.nhs_change_control_required = False
        post = self._make_post(funded_fte=1.0)
        post.funded_fte = 2.0
        self.assertEqual(post.funded_fte, 2.0)

    def _new_increase(self, post, proposed_fte=3.0):
        return self.Change.create({
            'change_type': 'increase_fte',
            'post_id': post.id,
            'proposed_fte': proposed_fte,
            'proposed_headcount': int(proposed_fte),
            'reason': 'Winter pressures',
        })

    def test_two_stage_approval_and_apply(self):
        """draft → submit → workforce → finance → apply updates the post FTE."""
        post = self._make_post(funded_fte=1.0)
        change = self._new_increase(post, 3.0).with_user(self.user_manager)
        change.action_submit()
        self.assertEqual(change.state, 'submitted')
        change.action_workforce_approve()
        self.assertEqual(change.state, 'workforce_approved')
        change.action_finance_approve()
        self.assertEqual(change.state, 'finance_approved')
        change.action_apply()
        self.assertEqual(change.state, 'applied')
        self.assertEqual(post.funded_fte, 3.0,
                         'Applying the change should update the post funded FTE.')

    def test_single_stage_skips_finance(self):
        """Single-stage companies jump to finance_approved on workforce approval."""
        self.company.nhs_change_control_single_stage = True
        post = self._make_post(funded_fte=1.0)
        change = self._new_increase(post, 2.0).with_user(self.user_manager)
        change.action_submit()
        change.action_workforce_approve()
        self.assertEqual(change.state, 'finance_approved')

    def test_cost_impact_increase(self):
        """Cost impact of an FTE increase = salary x delta x on-cost."""
        post = self._make_post(funded_fte=1.0)  # Band 5 = 29970
        change = self._new_increase(post, 3.0)
        self.assertAlmostEqual(change.cost_impact, 29970.0 * 2.0)

    def test_apply_reband(self):
        """A reband change moves the post to the proposed band."""
        post = self._make_post(funded_fte=1.0)
        change = self.Change.create({
            'change_type': 'reband', 'post_id': post.id,
            'proposed_fte': post.funded_fte, 'proposed_band_id': self.band6.id,
            'reason': 'Job evaluation',
        }).with_user(self.user_manager)
        change.action_submit()
        change.action_workforce_approve()
        change.action_finance_approve()
        change.action_apply()
        self.assertEqual(post.band_id, self.band6)

    def test_apply_transfer(self):
        """A transfer change moves the post to the target unit."""
        post = self._make_post(funded_fte=1.0)
        change = self.Change.create({
            'change_type': 'transfer', 'post_id': post.id,
            'org_unit_id': self.unit_parent.id,
            'reason': 'Service reconfiguration',
        }).with_user(self.user_manager)
        change.action_submit()
        change.action_workforce_approve()
        change.action_finance_approve()
        change.action_apply()
        self.assertEqual(post.org_unit_id, self.unit_parent)

    def test_apply_create_post(self):
        """A create_post change spawns a new active post in the target unit."""
        change = self.Change.create({
            'change_type': 'create_post', 'org_unit_id': self.unit_child.id,
            'proposed_job_title': 'New HCA',
            'proposed_staff_group_id': self.staff_group.id,
            'proposed_band_id': self.band5.id,
            'proposed_fte': 2.0, 'proposed_headcount': 2,
            'reason': 'Expansion',
        }).with_user(self.user_manager)
        change.action_submit()
        change.action_workforce_approve()
        change.action_finance_approve()
        change.action_apply()
        self.assertTrue(change.post_id, 'create_post should link the new post.')
        self.assertEqual(change.post_id.funded_fte, 2.0)
        self.assertEqual(change.post_id.status, 'active')

    def test_reject_requires_reason(self):
        """Rejecting a change needs a rejection reason."""
        post = self._make_post(funded_fte=1.0)
        change = self._new_increase(post)
        change.action_submit()
        with self.assertRaises(UserError):
            change.action_reject()
        change.rejection_reason = 'Not funded'
        change.action_reject()
        self.assertEqual(change.state, 'rejected')

    def test_only_manager_can_approve(self):
        """A workforce officer cannot approve; a manager can."""
        post = self._make_post(funded_fte=1.0)
        change = self._new_increase(post)
        change.action_submit()
        with self.assertRaises(UserError):
            change.with_user(self.user_officer).action_workforce_approve()
        change.with_user(self.user_manager).action_workforce_approve()
        self.assertEqual(change.state, 'workforce_approved')

    def test_wrong_state_transitions_rejected(self):
        """Approvals are only valid from the correct prior state."""
        post = self._make_post(funded_fte=1.0)
        change = self._new_increase(post).with_user(self.user_manager)
        # Cannot finance-approve a draft.
        with self.assertRaises(UserError):
            change.action_finance_approve()
        # Cannot apply before finance approval.
        change.action_submit()
        change.action_workforce_approve()
        with self.assertRaises(UserError):
            change.action_apply()
