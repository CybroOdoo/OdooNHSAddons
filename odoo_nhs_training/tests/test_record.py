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

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import tagged

from .common import NhsTrainingCommon


@tagged('post_install', '-at_install')
class TestTrainingRecord(NhsTrainingCommon):
    """Training-record expiry, status, latest-flag and deletion guard."""

    def test_expiry_from_frequency(self):
        """expiry_date = completion_date + effective refresh interval."""
        today = fields.Date.context_today(self.Record)
        rec = self._record(completion_date=today)
        self.assertEqual(rec.expiry_date, today + relativedelta(months=12))
        self.assertEqual(rec.status, 'compliant')

    def test_one_off_never_expires(self):
        """A one-off subject has no expiry and is always compliant once done."""
        rec = self._record(subject=self.subj_oneoff)
        self.assertFalse(rec.expiry_date)
        self.assertEqual(rec.status, 'compliant')

    def test_expired_status(self):
        """A completion past its refresh interval is expired."""
        old = fields.Date.context_today(self.Record) - timedelta(days=400)
        rec = self._record(completion_date=old)
        self.assertEqual(rec.status, 'expired')

    def test_due_soon_status(self):
        """A completion whose expiry falls within the lead window is due_soon."""
        # expiry ≈ today + 30 days (< 60-day lead) → due_soon.
        completion = fields.Date.context_today(self.Record) - relativedelta(months=12) + timedelta(days=30)
        rec = self._record(completion_date=completion)
        self.assertEqual(rec.status, 'due_soon')

    def test_fail_forces_failed(self):
        """A Fail result forces status to failed regardless of dates."""
        rec = self._record(result='fail')
        self.assertEqual(rec.status, 'failed')

    def test_manual_expiry_override(self):
        """A manual expiry date overrides the computed one."""
        override = fields.Date.context_today(self.Record) + timedelta(days=5)
        rec = self._record(expiry_override=override)
        self.assertEqual(rec.expiry_date, override)

    def test_frequency_override_on_record(self):
        """A per-record frequency override changes the computed expiry."""
        today = fields.Date.context_today(self.Record)
        rec = self._record(completion_date=today, frequency_months=6)
        self.assertEqual(rec.expiry_date, today + relativedelta(months=6))

    def test_is_latest(self):
        """Only the most recent completion of a subject is flagged latest."""
        today = fields.Date.context_today(self.Record)
        old = self._record(completion_date=today - timedelta(days=200))
        new = self._record(completion_date=today)
        self.assertFalse(old.is_latest)
        self.assertTrue(new.is_latest)

    def test_completion_not_future(self):
        """A completion date cannot be in the future."""
        future = fields.Date.context_today(self.Record) + timedelta(days=1)
        with self.assertRaises(ValidationError):
            self._record(completion_date=future)

    def test_record_cannot_be_deleted(self):
        """Training records are archived, never deleted."""
        rec = self._record()
        with self.assertRaises(UserError):
            rec.unlink()
