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
from odoo.tests.common import tagged

from .common import NhsTrainingCommon


@tagged('post_install', '-at_install')
class TestAssignPostsWizard(NhsTrainingCommon):
    """The bulk 'assign posts to a requirement profile' wizard."""

    def _make_post(self, title):
        return self.Post.create({
            'job_title': title, 'org_unit_id': self.ward.id,
            'staff_group_id': self.staff_group.id, 'band_id': self.band5.id,
            'funded_fte': 1.0, 'status': 'active',
        })

    def test_assign_and_unassign(self):
        """The wizard links selected posts to the profile and clears deselected ones."""
        post_a = self._make_post('Nurse A')
        post_b = self._make_post('Nurse B')
        # Assign both to the profile.
        wizard = self.env['nhs.profile.assign.posts.wizard'].create({
            'profile_id': self.profile.id,
            'post_ids': [(6, 0, (post_a + post_b).ids)],
        })
        wizard.action_confirm()
        self.assertEqual(post_a.training_requirement_profile_id, self.profile)
        self.assertEqual(post_b.training_requirement_profile_id, self.profile)
        # Re-run keeping only post_a → post_b is unassigned.
        wizard2 = self.env['nhs.profile.assign.posts.wizard'].create({
            'profile_id': self.profile.id,
            'post_ids': [(6, 0, post_a.ids)],
        })
        wizard2.action_confirm()
        self.assertEqual(post_a.training_requirement_profile_id, self.profile)
        self.assertFalse(post_b.training_requirement_profile_id)
