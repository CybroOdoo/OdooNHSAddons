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

from odoo.exceptions import UserError
from odoo.tests.common import tagged
from odoo.tools import mute_logger

from .common import NhsDsptCommon


@tagged('post_install', '-at_install')
class TestEdition(NhsDsptCommon):
    """Edition uniqueness and deep-clone to a new year."""

    @mute_logger('odoo.sql_db')
    def test_year_unique(self):
        """A UNIQUE(year) DB constraint blocks a duplicate edition year."""
        with self.assertRaises(psycopg2.IntegrityError):
            with self.cr.savepoint():
                self.Edition.create({'name': 'Dup', 'year': '2025/26'})
                self.env.flush_all()

    def test_copy_edition_deep_clone(self):
        """copy_edition clones standards/assertions/evidence into a new draft
        edition and flags the copied definitions as 'new'."""
        new_edition = self.edition.copy_edition(new_year='2099/00',
                                                new_name='DSPT 2099/00')
        self.assertEqual(new_edition.state, 'draft')
        self.assertEqual(len(new_edition.standard_ids), len(self.edition.standard_ids))
        new_assertions = new_edition.standard_ids.assertion_def_ids
        self.assertEqual(len(new_assertions), self.edition.assertion_count)
        self.assertTrue(all(a.change_flag == 'new' for a in new_assertions),
                        'Cloned assertions should be flagged new for reviewer awareness.')

    def test_copy_edition_duplicate_year_raises(self):
        """Cloning to an already-existing year is rejected."""
        with self.assertRaises(UserError):
            self.edition.copy_edition(new_year='2025/26')

    def test_activate_and_archive(self):
        """Edition activate/archive state helpers work."""
        edition = self.Edition.create({'name': 'X', 'year': '2098/99', 'state': 'draft'})
        edition.action_activate()
        self.assertEqual(edition.state, 'active')
        edition.action_archive_edition()
        self.assertEqual(edition.state, 'archived')
