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

from .common import NhsEstablishmentCommon


@tagged('post_install', '-at_install')
class TestSecurity(NhsEstablishmentCommon):
    """Access-control model: read-only user, officer create, manager-only config."""

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.models')
    def test_readonly_user_cannot_create_post(self):
        """A Workforce User is read-only on posts (perm_create=0)."""
        with self.assertRaises(AccessError):
            self.Post.with_user(self.user_readonly).create({
                'job_title': 'X', 'org_unit_id': self.unit_child.id,
                'staff_group_id': self.staff_group.id, 'band_id': self.band5.id,
                'funded_fte': 1.0,
            })

    def test_readonly_user_can_read_post(self):
        """A Workforce User can read posts."""
        post = self._make_post(funded_fte=1.0)
        self.assertEqual(
            post.with_user(self.user_readonly).job_title, 'Theatre Nurse')

    def test_officer_can_create_post(self):
        """A Workforce Officer can create posts (perm_create=1)."""
        post = self.Post.with_user(self.user_officer).create({
            'job_title': 'Officer Post', 'org_unit_id': self.unit_child.id,
            'staff_group_id': self.staff_group.id, 'band_id': self.band5.id,
            'funded_fte': 1.0, 'status': 'active',
        })
        self.assertTrue(post.reference.startswith('POST'))

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.models')
    def test_officer_cannot_edit_bands(self):
        """AfC bands are manager-only config (officer has no write)."""
        with self.assertRaises(AccessError):
            self.band5.with_user(self.user_officer).indicative_salary = 40000.0

    def test_afc_band_shared_across_companies(self):
        """A company-less band is visible under the company record rule."""
        shared = self.band5.with_user(self.user_readonly)
        self.assertTrue(shared.name)
