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

import psycopg2

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import tagged
from odoo.tools import mute_logger

from .common import NhsTrainingCommon


@tagged('post_install', '-at_install')
class TestRegistration(NhsTrainingCommon):
    """Professional registration status, deletion guard and regulator uniqueness."""

    def _reg(self, expiry):
        return self.Registration.create({
            'member_id': self.member.id, 'regulator_id': self.nmc.id,
            'expiry_date': expiry,
        })

    def test_status_current(self):
        """A registration well before expiry is current."""
        reg = self._reg(fields.Date.context_today(self.Registration) + timedelta(days=365))
        self.assertEqual(reg.status, 'current')

    def test_status_expiring_soon(self):
        """A registration within the due-soon window is expiring_soon."""
        reg = self._reg(fields.Date.context_today(self.Registration) + timedelta(days=15))
        self.assertEqual(reg.status, 'expiring_soon')

    def test_status_lapsed(self):
        """A registration past expiry is lapsed."""
        reg = self._reg(fields.Date.context_today(self.Registration) - timedelta(days=1))
        self.assertEqual(reg.status, 'lapsed')

    def test_lapsed_registration_blocks_compliance_api(self):
        """A lapsed registration makes is_training_compliant() return False."""
        self._record()  # training itself in date
        self.assertTrue(self.member.is_training_compliant())
        self._reg(fields.Date.context_today(self.Registration) - timedelta(days=1))
        self.assertFalse(self.member.is_training_compliant())

    def test_registration_cannot_be_deleted(self):
        """Registrations are archived, never deleted."""
        reg = self._reg(fields.Date.context_today(self.Registration) + timedelta(days=30))
        with self.assertRaises(UserError):
            reg.unlink()

    @mute_logger('odoo.sql_db')
    def test_regulator_unique_name(self):
        """UNIQUE(name) blocks a duplicate regulator name (DB constraint)."""
        with self.assertRaises(psycopg2.IntegrityError):
            with self.cr.savepoint():
                self.Regulator.create({'name': self.nmc.name})
                self.env.flush_all()
