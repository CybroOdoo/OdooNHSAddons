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
import psycopg2

from odoo.tests.common import tagged
from odoo.tools import mute_logger

from .common import NhsEstateCommon


@tagged('post_install', '-at_install')
class TestCodesAndConstraints(NhsEstateCommon):
    """Code casing/sequencing, display names and UNIQUE constraints."""

    def test_site_code_uppercased(self):
        """A site code is stored upper-cased."""
        self.assertEqual(self.site.code, 'STH')  # created as 'sth'

    def test_site_code_autosequenced(self):
        """A blank site code is filled from the sequence."""
        site = self.Site.create({'name': 'No Code Site'})
        self.assertTrue(site.code)

    def test_building_code_autosequenced(self):
        """A blank building code is filled from the sequence."""
        building = self.Building.create({'name': 'Block B', 'site_id': self.site.id})
        self.assertTrue(building.code)

    def test_site_display_name(self):
        """Site display name is '[code] name'."""
        self.assertEqual(self.site.display_name, '[STH] St Test Hospital')

    def test_space_complete_name(self):
        """Space complete_name is the full site/building/floor/space path."""
        self.assertEqual(
            self.space_clin.complete_name,
            'St Test Hospital / Main Block / Ground Floor / Ward 1')

    @mute_logger('odoo.sql_db')
    def test_site_code_unique(self):
        """Duplicate site code is blocked by a UNIQUE constraint."""
        with self.assertRaises(psycopg2.IntegrityError):
            with self.cr.savepoint():
                self.Site.create({'name': 'Dup', 'code': 'STH'})
                self.env.flush_all()

    @mute_logger('odoo.sql_db')
    def test_building_code_unique(self):
        """Duplicate building code is blocked by a UNIQUE constraint."""
        with self.assertRaises(psycopg2.IntegrityError):
            with self.cr.savepoint():
                self.Building.create(
                    {'name': 'Dup', 'code': 'MB1', 'site_id': self.site.id})
                self.env.flush_all()

    @mute_logger('odoo.sql_db')
    def test_floor_unique_sequence_per_building(self):
        """Two floors cannot share the same order within one building."""
        with self.assertRaises(psycopg2.IntegrityError):
            with self.cr.savepoint():
                self.Floor.create(
                    {'name': 'Dup GF', 'building_id': self.building.id, 'sequence': 0})
                self.env.flush_all()

    @mute_logger('odoo.sql_db')
    def test_space_code_unique(self):
        """Duplicate space code is blocked by a UNIQUE constraint."""
        code = self.space_clin.code
        with self.assertRaises(psycopg2.IntegrityError):
            with self.cr.savepoint():
                self.Space.create(
                    {'name': 'Dup', 'floor_id': self.floor.id, 'code': code})
                self.env.flush_all()

    @mute_logger('odoo.sql_db')
    def test_function_unique_name_parent(self):
        """A function name must be unique within its parent.

        NB: the DB unique index treats a NULL parent as distinct, so this only
        fires for children under a real parent (top-level names can repeat).
        """
        self.Function.create({'name': 'Surgical', 'parent_id': self.func_clinical.id})
        with self.assertRaises(psycopg2.IntegrityError):
            with self.cr.savepoint():
                self.Function.create({'name': 'Surgical', 'parent_id': self.func_clinical.id})
                self.env.flush_all()

    def test_function_complete_name_recursive(self):
        """Function complete_name builds the parent path recursively."""
        child = self.Function.create({'name': 'Surgical', 'parent_id': self.func_clinical.id})
        self.assertEqual(child.complete_name, 'ZZ Ward / Surgical')
