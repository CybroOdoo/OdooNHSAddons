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
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import tagged

from .common import NhsEstablishmentCommon


@tagged('post_install', '-at_install')
class TestOrgUnit(NhsEstablishmentCommon):
    """Org-unit hierarchy, roll-ups, recursion + archive/delete guards."""

    def test_complete_name_breadcrumb(self):
        """complete_name is the parent-chain breadcrumb."""
        self.assertEqual(self.unit_child.complete_name, 'Surgery / Theatres')
        self.assertEqual(self.unit_parent.complete_name, 'Surgery')

    def test_code_auto_sequenced(self):
        """A blank unit code is filled from the sequence (OU prefix)."""
        unit = self.OrgUnit.create({'name': 'Recovery', 'unit_type': 'team'})
        self.assertTrue(unit.code and unit.code.startswith('OU'))

    def test_rollup_totals_recurse(self):
        """funded/in-post/vacant FTE roll up from posts through the hierarchy."""
        self._make_post(funded_fte=3.0, in_post_fte=2.0)          # child
        self._make_post(funded_fte=1.0, in_post_fte=1.0,          # parent directly
                        org_unit_id=self.unit_parent.id)
        self.assertEqual(self.unit_child.funded_fte, 3.0)
        self.assertEqual(self.unit_child.vacant_fte, 1.0)
        # Parent = its own post (1.0) + child rollup (3.0) = 4.0 funded, 1.0 vacant.
        self.assertEqual(self.unit_parent.funded_fte, 4.0)
        self.assertEqual(self.unit_parent.vacant_fte, 1.0)

    def test_vacancy_rate(self):
        """vacancy_rate = vacant / funded."""
        self._make_post(funded_fte=4.0, in_post_fte=3.0)
        self.assertAlmostEqual(self.unit_child.vacancy_rate, 0.25)

    def test_draft_posts_excluded_from_rollup(self):
        """Only active/frozen posts count toward the establishment totals."""
        self._make_post(funded_fte=5.0, in_post_fte=0.0, status='draft')
        self.assertEqual(self.unit_child.funded_fte, 0.0)

    def test_recursion_blocked(self):
        """A unit cannot be made its own ancestor (ORM raises UserError, of which
        ValidationError is a subclass — the framework guard fires first)."""
        with self.assertRaises(UserError):
            self.unit_parent.parent_id = self.unit_child

    def test_archive_with_live_posts_blocked(self):
        """Archiving a unit with active/frozen posts is rejected with a clear error."""
        self._make_post(funded_fte=1.0)
        with self.assertRaises(ValidationError):
            self.unit_child.active = False

    def test_delete_unit_with_posts_blocked(self):
        """Deleting a unit that still has posts is rejected."""
        self._make_post(funded_fte=1.0)
        with self.assertRaises(UserError):
            self.unit_child.unlink()

    def test_delete_unit_with_children_blocked(self):
        """Deleting a unit that still has sub-units is rejected."""
        with self.assertRaises(UserError):
            self.unit_parent.unlink()

    def test_post_count(self):
        """post_count counts posts under a unit and its descendants."""
        self._make_post(funded_fte=1.0)
        self._make_post(funded_fte=1.0)
        self.assertEqual(self.unit_child.post_count, 2)
        # Parent sees both child posts via child_of.
        self.assertEqual(self.unit_parent.post_count, 2)
