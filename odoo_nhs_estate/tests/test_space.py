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
from odoo.tests.common import Form, tagged

from .common import NhsEstateCommon


@tagged('post_install', '-at_install')
class TestSpace(NhsEstateCommon):
    """Space clinical-flag derivation and occupancy computation."""

    def test_is_clinical_from_function(self):
        """is_clinical is derived from the assigned function's clinical flag."""
        self.assertTrue(self.space_clin.is_clinical)
        self.assertFalse(self.space_admin.is_clinical)

    def test_occupancy_from_utilisation(self):
        """Occupancy status/flag derive from the utilisation level."""
        self.assertEqual(self.space_clin.occupancy_status, 'occupied')
        self.assertTrue(self.space_clin.is_occupied)
        self.assertEqual(self.space_admin.occupancy_status, 'vacant')
        self.assertFalse(self.space_admin.is_occupied)

    def test_under_utilised_is_vacant(self):
        """Under-utilised counts as vacant; over-utilised counts as occupied."""
        under = self.Space.create({
            'name': 'Under', 'floor_id': self.floor.id, 'utilisation': 'under'})
        over = self.Space.create({
            'name': 'Over', 'floor_id': self.floor.id, 'utilisation': 'over'})
        self.assertFalse(under.is_occupied)
        self.assertTrue(over.is_occupied)

    def test_is_clinical_overridable(self):
        """is_clinical is stored & editable — a manual override sticks."""
        self.space_admin.is_clinical = True
        self.assertTrue(self.space_admin.is_clinical)

    def test_is_clinical_recomputes_on_function_change(self):
        """Changing the function on the Form recomputes is_clinical."""
        form = Form(self.Space)
        form.name = 'New Space'
        form.floor_id = self.floor
        form.function_id = self.func_clinical
        self.assertTrue(form.is_clinical)
        form.function_id = self.func_admin
        self.assertFalse(form.is_clinical)
