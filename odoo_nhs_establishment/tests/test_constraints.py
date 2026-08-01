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

from odoo.exceptions import ValidationError
from odoo.tests.common import tagged
from odoo.tools import mute_logger

from .common import NhsEstablishmentCommon


@tagged('post_install', '-at_install')
class TestConstraints(NhsEstablishmentCommon):
    """@api.constrains and SQL unique constraints across the module."""

    def test_negative_fte_blocked(self):
        """Funded and in-post FTE cannot be negative."""
        with self.assertRaises(ValidationError):
            self._make_post(funded_fte=-1.0)
        with self.assertRaises(ValidationError):
            self._make_post(funded_fte=1.0, in_post_fte=-0.5)

    def test_band_required_unless_medical(self):
        """A non-medical, non-deleted post must carry an AfC band."""
        with self.assertRaises(ValidationError):
            self._make_post(band_id=False, is_medical=False)
        # Medical post without a band is fine.
        post = self._make_post(band_id=False, is_medical=True,
                               manual_indicative_salary=80000.0)
        self.assertTrue(post)

    def test_change_requires_post(self):
        """A non-create change type requires an affected post."""
        with self.assertRaises(ValidationError):
            self.Change.create({
                'change_type': 'increase_fte', 'proposed_fte': 1.0,
                'reason': 'x',
            })

    def test_change_requires_target_unit(self):
        """create_post / transfer require a target unit."""
        with self.assertRaises(ValidationError):
            self.Change.create({
                'change_type': 'create_post', 'reason': 'x',
                'proposed_job_title': 'X',
            })

    @mute_logger('odoo.sql_db')
    def test_staff_group_unique_name(self):
        """A UNIQUE(name) DB constraint blocks duplicate staff-group names."""
        self.StaffGroup.create({'name': 'ZZ Unique Group'})
        with self.assertRaises(psycopg2.IntegrityError):
            with self.cr.savepoint():
                self.StaffGroup.create({'name': 'ZZ Unique Group'})
                self.env.flush_all()
