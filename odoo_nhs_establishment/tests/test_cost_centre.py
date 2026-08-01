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

from .common import NhsEstablishmentCommon


@tagged('post_install', '-at_install')
class TestCostCentre(NhsEstablishmentCommon):
    """Cost-centre roll-ups, budget variance/utilisation and unique code."""

    def test_rollups_and_variance(self):
        """Spend rolls up from posts; variance = budget - spend."""
        # Two Band 5 posts (29970 each) charged to the cost centre.
        self._make_post(funded_fte=1.0, cost_centre=self.cost_centre.id)
        self._make_post(funded_fte=1.0, cost_centre=self.cost_centre.id)
        self.assertEqual(self.cost_centre.post_count, 2)
        self.assertAlmostEqual(self.cost_centre.funded_fte, 2.0)
        self.assertAlmostEqual(self.cost_centre.indicative_pay_total, 29970.0 * 2)
        self.assertAlmostEqual(self.cost_centre.budget_variance,
                               500000.0 - 29970.0 * 2)

    def test_budget_utilisation(self):
        """utilisation = spend / budget."""
        self._make_post(funded_fte=1.0, cost_centre=self.cost_centre.id)
        # budget_utilization is stored at 3-dp precision -> 0.060.
        self.assertAlmostEqual(self.cost_centre.budget_utilization, 0.06, places=3)

    @mute_logger('odoo.sql_db')
    def test_unique_code_per_company(self):
        """A UNIQUE(code, company_id) DB constraint blocks duplicate codes."""
        with self.assertRaises(psycopg2.IntegrityError):
            with self.cr.savepoint():
                self.CostCentre.create({'name': 'Dup', 'code': 'CC-THEATRE'})
                self.env.flush_all()
