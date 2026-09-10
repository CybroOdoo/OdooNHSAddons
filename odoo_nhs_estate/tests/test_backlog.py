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
class TestBacklog(NhsEstateCommon):
    """Backlog maintenance items: naming, status flow and cost roll-up."""

    def _backlog(self, **kw):
        vals = {
            'name': 'Boiler replacement', 'building_id': self.building.id,
            'risk_category': 'significant', 'cost_estimate': 12000.0,
        }
        vals.update(kw)
        return self.Backlog.create(vals)

    def test_complete_name(self):
        """complete_name combines building (and space) with the description."""
        bl = self._backlog(space_id=self.space_clin.id)
        self.assertEqual(bl.complete_name, 'Main Block / Ward 1 / Boiler replacement')

    def test_status_transitions(self):
        """The status quick actions move the item through its lifecycle."""
        bl = self._backlog()
        self.assertEqual(bl.status, 'identified')
        bl.action_mark_planned()
        self.assertEqual(bl.status, 'planned')
        bl.action_mark_start()
        self.assertEqual(bl.status, 'in_progress')
        bl.action_mark_resolved()
        self.assertEqual(bl.status, 'resolved')

    def test_cost_rolls_up_to_building(self):
        """Multiple backlog items sum onto the building total."""
        self._backlog(cost_estimate=1000.0)
        self._backlog(cost_estimate=2500.0)
        self.assertEqual(self.building.backlog_total, 3500.0)
        self.assertEqual(self.building.backlog_count, 2)
