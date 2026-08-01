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

from odoo.tests import Form
from odoo.tests.common import tagged

from .common import NhsEstablishmentCommon


@tagged('post_install', '-at_install')
class TestPostFte(NhsEstablishmentCommon):
    """FTE maths, vacancy status, indicative pay and status/flag syncing."""

    def test_vacant_and_status_fully_staffed(self):
        """funded == in_post -> 0 vacant, fully_staffed."""
        post = self._make_post(funded_fte=2.0, in_post_fte=2.0)
        self.assertEqual(post.vacant_fte, 0.0)
        self.assertEqual(post.vacancy_status, 'fully_staffed')

    def test_vacant_and_status_part_and_full(self):
        """Partly and fully vacant statuses are derived from the FTE gap."""
        part = self._make_post(funded_fte=2.0, in_post_fte=1.0)
        self.assertEqual(part.vacant_fte, 1.0)
        self.assertEqual(part.vacancy_status, 'part_vacant')
        full = self._make_post(funded_fte=2.0, in_post_fte=0.0)
        self.assertEqual(full.vacancy_status, 'fully_vacant')

    def test_over_established(self):
        """in_post > funded -> over_established (negative vacant)."""
        post = self._make_post(funded_fte=1.0, in_post_fte=2.0)
        self.assertEqual(post.vacancy_status, 'over_established')
        self.assertEqual(post.vacant_fte, -1.0)

    def test_indicative_pay(self):
        """indicative_pay = band salary x funded FTE x on-cost factor."""
        post = self._make_post(funded_fte=2.0)  # Band 5 = 29970, on-cost 1.0
        self.assertAlmostEqual(post.indicative_pay, 29970.0 * 2.0)

    def test_indicative_pay_on_cost_factor(self):
        """The company on-cost factor scales the indicative pay."""
        self.company.nhs_on_cost_factor = 1.2
        post = self._make_post(funded_fte=1.0)
        self.assertAlmostEqual(post.indicative_pay, 29970.0 * 1.2)

    def test_medical_uses_manual_salary(self):
        """Medical / Non-AfC posts price off the manual salary, not a band."""
        post = self._make_post(
            band_id=False, is_medical=True, manual_indicative_salary=90000.0,
            funded_fte=1.0)
        self.assertAlmostEqual(post.indicative_pay, 90000.0)

    def test_fte_value_helper(self):
        """The pure FTE helper: hours / basis * headcount, rounded to 2 dp."""
        self.assertEqual(self.Post._compute_fte_value(37.5, 1, 37.5), 1.0)
        self.assertEqual(self.Post._compute_fte_value(37.5, 2, 37.5), 2.0)
        self.assertEqual(self.Post._compute_fte_value(18.75, 1, 37.5), 0.5)
        self.assertEqual(self.Post._compute_fte_value(37.5, 0, 37.5), 0.0)

    def test_onchange_fte_basis(self):
        """Editing hours/headcount on the form recomputes funded & in-post FTE."""
        form = Form(self.Post)
        form.job_title = 'Nurse'
        form.org_unit_id = self.unit_child
        form.staff_group_id = self.staff_group
        form.band_id = self.band5
        form.contracted_hours = 37.5
        form.funded_headcount = 3
        form.in_post_headcount = 2
        self.assertEqual(form.funded_fte, 3.0)
        self.assertEqual(form.in_post_fte, 2.0)

    def test_onchange_is_medical_clears_band(self):
        """Ticking Medical / Non-AfC clears the AfC band on the form."""
        form = Form(self.Post)
        form.job_title = 'Consultant'
        form.org_unit_id = self.unit_child
        form.staff_group_id = self.staff_group
        form.band_id = self.band5
        form.is_medical = True
        self.assertFalse(form.band_id)

    def test_status_flags_synced_on_create(self):
        """status drives active/is_frozen at create time."""
        frozen = self._make_post(status='frozen')
        self.assertTrue(frozen.active)
        self.assertTrue(frozen.is_frozen)
        deleted = self._make_post(status='deleted')
        self.assertFalse(deleted.active)
        self.assertFalse(deleted.is_frozen)

    def test_status_flags_synced_on_write(self):
        """Writing status keeps active/is_frozen consistent (change-control off)."""
        self.company.nhs_change_control_required = False
        post = self._make_post()
        post.action_freeze_post()
        self.assertEqual(post.status, 'frozen')
        self.assertTrue(post.is_frozen)
        post.action_delete_post()
        self.assertEqual(post.status, 'deleted')
        self.assertFalse(post.active)

    def test_vacancy_start_date_set_and_cleared(self):
        """vacancy_start_date is stamped when vacant and cleared when filled."""
        self.company.nhs_change_control_required = False
        post = self._make_post(funded_fte=2.0, in_post_fte=1.0)
        self.assertTrue(post.vacancy_start_date, 'A vacancy should stamp a start date.')
        post.write({'in_post_fte': 2.0})
        self.assertFalse(post.vacancy_start_date, 'Filling the post clears the date.')

    def test_days_vacant(self):
        """days_vacant is the age in days of the current vacancy."""
        self.company.nhs_change_control_required = False
        with freeze_time('2026-06-01'):
            post = self._make_post(funded_fte=1.0, in_post_fte=0.0)
            self.assertEqual(post.vacancy_start_date, date(2026, 6, 1))
        with freeze_time('2026-06-11'):
            post.invalidate_recordset(['days_vacant'])
            self.assertEqual(post.days_vacant, 10)

    def test_cron_long_vacancy_posts_note(self):
        """The nightly cron posts a chatter note on a long-standing vacancy."""
        self.company.nhs_change_control_required = False
        post = self._make_post(funded_fte=1.0, in_post_fte=0.0)
        post.vacancy_start_date = date.today() - timedelta(days=90)
        before = len(post.message_ids)
        self.Post._cron_check_long_vacancies(threshold_days=90)
        self.assertGreater(len(post.message_ids), before,
                           'A note should be posted for a 90-day vacancy.')
