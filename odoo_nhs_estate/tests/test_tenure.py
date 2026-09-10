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
from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import tagged

from .common import NhsEstateCommon


@tagged('post_install', '-at_install')
class TestTenure(NhsEstateCommon):
    """Tenure naming, lease term, expiry flag and date constraints."""

    def test_name_computed(self):
        """Tenure name combines the tenure type label and the building name."""
        tenure = self.Tenure.create({
            'building_id': self.building.id, 'tenure_type': 'leasehold'})
        self.assertEqual(tenure.name, 'Leasehold — Main Block')

    def test_lease_term_years(self):
        """lease_term_years is derived from start and end dates."""
        tenure = self.Tenure.create({
            'building_id': self.building.id, 'tenure_type': 'leasehold',
            'lease_start': '2020-01-01', 'lease_end': '2030-01-01',
        })
        self.assertEqual(tenure.lease_term_years, 10)  # ~10 years, Integer

    def test_expiring_soon_true(self):
        """A lease ending within 12 months is flagged expiring soon."""
        tenure = self.Tenure.create({
            'building_id': self.building.id, 'tenure_type': 'leasehold',
            'lease_end': fields.Date.today() + timedelta(days=100),
        })
        self.assertTrue(tenure.expiring_soon)

    def test_expiring_soon_false(self):
        """A lease ending beyond 12 months is not flagged expiring soon."""
        tenure = self.Tenure.create({
            'building_id': self.building.id, 'tenure_type': 'leasehold',
            'lease_end': fields.Date.today() + timedelta(days=500),
        })
        self.assertFalse(tenure.expiring_soon)

    def test_lease_end_before_start_rejected(self):
        """Lease end cannot precede lease start."""
        with self.assertRaises(ValidationError):
            self.Tenure.create({
                'building_id': self.building.id, 'tenure_type': 'leasehold',
                'lease_start': '2030-01-01', 'lease_end': '2029-01-01',
            })

    def test_contract_end_before_start_rejected(self):
        """Contract end cannot precede contract start."""
        with self.assertRaises(ValidationError):
            self.Tenure.create({
                'building_id': self.building.id, 'tenure_type': 'pfi',
                'contract_start': '2030-01-01', 'contract_end': '2029-01-01',
            })
