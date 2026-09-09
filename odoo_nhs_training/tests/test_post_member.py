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
class TestPostAndTeam(NhsTrainingCommon):
    """Post → member cascade and org-unit team-compliance roll-ups."""

    def _make_post(self):
        return self.Post.create({
            'job_title': 'Staff Nurse', 'org_unit_id': self.ward.id,
            'staff_group_id': self.staff_group.id, 'band_id': self.band5.id,
            'funded_fte': 1.0, 'status': 'active',
            'training_requirement_profile_id': self.profile.id,
        })

    def test_member_inherits_from_post_on_create(self):
        """Creating a member with only a post cascades team/staff-group/profile."""
        post = self._make_post()
        member = self.Member.create({'name': 'New Starter', 'post_id': post.id})
        self.assertEqual(member.org_unit_id, self.ward)
        self.assertEqual(member.staff_group_id, self.staff_group)
        self.assertEqual(member.requirement_profile_id, self.profile)

    def test_member_reference_sequenced(self):
        """A new workforce member gets a sequenced reference."""
        self.assertTrue(self.member.reference and self.member.reference != 'New')

    def test_team_rollup(self):
        """Required/compliant subject counts roll up to the unit and its parent."""
        # member (on ward) requires 1 subject, none done yet.
        self.assertGreaterEqual(self.ward.team_required_count, 1)
        self.assertEqual(self.ward.team_compliant_count, 0)
        # Division rolls up the ward.
        self.assertGreaterEqual(self.division.team_required_count, 1)
        # Complete the subject → compliant count rises.
        self._record()
        self.assertEqual(self.ward.team_compliant_count, 1)
        self.assertEqual(self.ward.team_compliance_pct, 100.0)
        self.assertEqual(self.division.team_compliant_count, 1)

    def test_post_member_count(self):
        """A post reports how many workforce members hold it."""
        post = self._make_post()
        self.Member.create({'name': 'Holder', 'post_id': post.id})
        self.assertEqual(post.member_count, 1)
