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
from odoo.exceptions import AccessError
from odoo.tests.common import tagged
from odoo.tools import mute_logger

from .common import NhsTrainingCommon


@tagged('post_install', '-at_install')
class TestSecurity(NhsTrainingCommon):
    """Access-control model: viewer read-only, officer edit, manager config."""

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.models')
    def test_viewer_cannot_create_member(self):
        """A training viewer is read-only on workforce members."""
        with self.assertRaises(AccessError):
            self.Member.with_user(self.user_viewer).create(
                {'name': 'X', 'org_unit_id': self.ward.id})

    def test_officer_can_create_record(self):
        """A training officer can log training completions."""
        rec = self.Record.with_user(self.user_officer).create({
            'member_id': self.member.id, 'subject_id': self.subj_annual.id})
        self.assertTrue(rec.id)

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.models')
    def test_officer_cannot_create_subject(self):
        """Training subjects are manager-only config (officer read-only)."""
        with self.assertRaises(AccessError):
            self.Subject.with_user(self.user_officer).create({'name': 'New Subject'})

    def test_manager_can_create_subject(self):
        """A training manager can maintain the subject catalogue."""
        subject = self.Subject.with_user(self.user_manager).create(
            {'name': 'Manager Subject'})
        self.assertTrue(subject.id)

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.models')
    def test_officer_cannot_delete_member(self):
        """Officers have perm_unlink=0 on workforce members — deletion is refused
        at the ACL layer (members carry no Python unlink override)."""
        with self.assertRaises(AccessError):
            self.member.with_user(self.user_officer).unlink()
