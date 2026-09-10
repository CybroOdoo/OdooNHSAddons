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

from .common import NhsEstateCommon


@tagged('post_install', '-at_install')
class TestHierarchyRollups(NhsEstateCommon):
    """GIA / area / count roll-ups across site → building → floor → space."""

    def test_floor_gia_sums_spaces(self):
        """A floor's GIA is the sum of its spaces' areas."""
        self.assertEqual(self.floor.gia, 100.0)  # 60 + 40
        self.assertEqual(self.floor.space_count, 2)

    def test_building_gia_sums_floors(self):
        """A building's GIA sums its floors' GIA (no NIA set)."""
        self.assertEqual(self.building.gia, 100.0)
        self.assertEqual(self.building.floor_count, 1)
        self.assertEqual(self.building.space_count, 2)

    def test_building_gia_adds_nia(self):
        """When NIA is set, building GIA = sum(floor GIA) + NIA."""
        self.building.nia = 50.0
        self.assertEqual(self.building.gia, 150.0)

    def test_site_rollups(self):
        """Site totals aggregate GIA, building and space counts from buildings."""
        self.assertEqual(self.site.total_gia, 100.0)
        self.assertEqual(self.site.building_count, 1)
        self.assertEqual(self.site.space_count, 2)

    def test_building_area_analysis(self):
        """Clinical/non-clinical and occupied/vacant areas split by space."""
        self.assertEqual(self.building.clinical_area, 60.0)
        self.assertEqual(self.building.non_clinical_area, 40.0)
        self.assertEqual(self.building.occupied_area, 60.0)   # full utilisation
        self.assertEqual(self.building.vacant_area, 40.0)     # empty utilisation

    def test_site_area_analysis(self):
        """Site area analysis mirrors the sum of its buildings'."""
        self.assertEqual(self.site.site_clinical_area, 60.0)
        self.assertEqual(self.site.site_non_clinical_area, 40.0)
        self.assertEqual(self.site.site_occupied_area, 60.0)
        self.assertEqual(self.site.site_vacant_area, 40.0)

    def test_site_backlog_rollup(self):
        """Backlog cost rolls up building → site."""
        self.Backlog.create({
            'name': 'Roof repair', 'building_id': self.building.id,
            'risk_category': 'high', 'cost_estimate': 5000.0,
        })
        self.assertEqual(self.building.backlog_total, 5000.0)
        self.assertEqual(self.building.backlog_count, 1)
        self.assertEqual(self.site.total_backlog, 5000.0)

    def test_site_top_parent(self):
        """site_id resolves to the top-level parent of a nested site."""
        child = self.Site.create({
            'name': 'Annexe', 'code': 'anx', 'parent_id': self.site.id})
        self.assertEqual(child.site_id, self.site)
        self.assertEqual(self.site.child_count, 1)

    def test_gia_recomputes_on_space_change(self):
        """Changing a space area re-rolls GIA up the whole chain."""
        self.space_admin.area = 140.0  # was 40 → floor 200, building 200, site 200
        self.assertEqual(self.floor.gia, 200.0)
        self.assertEqual(self.building.gia, 200.0)
        self.assertEqual(self.site.total_gia, 200.0)
