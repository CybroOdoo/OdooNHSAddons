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
from datetime import date, timedelta

from freezegun import freeze_time

from odoo.tests.common import tagged

from .common import NhsEstateCommon


@tagged('post_install', '-at_install')
class TestCondition(NhsEstateCommon):
    """Six-facet condition surveys: overall grade and building roll-up."""

    def _survey(self, **facets):
        vals = {'building_id': self.building.id, 'survey_date': '2026-01-15'}
        vals.update(facets)
        return self.Condition.create(vals)

    def test_overall_grade_worst(self):
        """Default 'worst' roll-up takes the poorest facet grade."""
        self.env['ir.config_parameter'].sudo().set_param(
            'odoo_nhs_estate.condition_rollup', 'worst')
        survey = self._survey(facet_physical='A', facet_statutory='B', facet_energy='D')
        survey._compute_overall_grade()
        self.assertEqual(survey.overall_grade, 'D')

    def test_overall_grade_weighted(self):
        """'weighted' roll-up averages the facet grades to a band."""
        self.env['ir.config_parameter'].sudo().set_param(
            'odoo_nhs_estate.condition_rollup', 'weighted')
        # A(1) + B(2) + D(4) = 7 / 3 = 2.33 → band B.
        survey = self._survey(facet_physical='A', facet_statutory='B', facet_energy='D')
        survey._compute_overall_grade()
        self.assertEqual(survey.overall_grade, 'B')

    def test_no_facets_no_grade(self):
        """A survey with no facet ratings has no overall grade."""
        survey = self._survey()
        self.assertFalse(survey.overall_grade)

    def test_name_autosequenced(self):
        """A survey name is auto-sequenced from 'New Survey'."""
        survey = self._survey(facet_physical='A')
        self.assertTrue(survey.name and survey.name != 'New Survey')

    def test_building_latest_grade(self):
        """The building shows the grade of its most recent survey."""
        self._survey(survey_date='2025-01-01', facet_physical='D')
        self._survey(survey_date='2026-06-01', facet_physical='B')
        self.assertEqual(self.building.latest_condition_grade, 'B')
        self.assertEqual(self.building.condition_count, 2)

    def test_latest_grade_recomputes_on_unlink(self):
        """Deleting the latest survey reverts the building to the prior grade."""
        old = self._survey(survey_date='2025-01-01', facet_physical='D')
        new = self._survey(survey_date='2026-06-01', facet_physical='A')
        self.assertEqual(self.building.latest_condition_grade, 'A')
        new.unlink()
        self.assertEqual(self.building.latest_condition_grade, 'D')

    @freeze_time('2026-03-01')
    def test_next_survey_date_default(self):
        """next_survey_date defaults to survey_date + 30 days on the form."""
        survey = self.Condition.create({
            'building_id': self.building.id, 'survey_date': '2026-03-01'})
        self.assertEqual(survey.next_survey_date, date(2026, 3, 31))
