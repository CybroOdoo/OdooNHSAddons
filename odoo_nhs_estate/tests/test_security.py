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

from .common import NhsEstateCommon


@tagged('post_install', '-at_install')
class TestSecurity(NhsEstateCommon):
    """Access-control model: viewer read-only, officer edit, manager config."""

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.models')
    def test_viewer_cannot_create_site(self):
        """An estate viewer is read-only on sites."""
        with self.assertRaises(AccessError):
            self.Site.with_user(self.user_viewer).create(
                {'name': 'X', 'code': 'XVIEW'})

    def test_viewer_can_read_site(self):
        """An estate viewer can read sites."""
        self.assertEqual(self.site.with_user(self.user_viewer).name, 'St Test Hospital')

    def test_officer_can_create_building(self):
        """An estate officer can create buildings."""
        building = self.Building.with_user(self.user_officer).create(
            {'name': 'Officer Block', 'site_id': self.site.id})
        self.assertTrue(building.id)

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.models')
    def test_officer_cannot_create_function(self):
        """Functions are manager-only reference config (officer read-only)."""
        with self.assertRaises(AccessError):
            self.Function.with_user(self.user_officer).create({'name': 'Officer Fn'})

    def test_manager_can_create_function(self):
        """An estate manager can maintain the function taxonomy."""
        fn = self.Function.with_user(self.user_manager).create({'name': 'Manager Fn'})
        self.assertTrue(fn.id)

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.models')
    def test_officer_cannot_delete_building(self):
        """Officers have perm_unlink=0 on buildings — deletion refused at ACL."""
        with self.assertRaises(AccessError):
            self.building.with_user(self.user_officer).unlink()
