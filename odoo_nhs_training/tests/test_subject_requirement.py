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

from .common import NhsTrainingCommon


@tagged('post_install', '-at_install')
class TestSubjectAndRequirement(NhsTrainingCommon):
    """Training subjects, requirement scoping and requirement resolution."""

    def test_subject_complete_name(self):
        """complete_name combines subject and level."""
        self.assertEqual(self.subj_extra.complete_name, 'ZZ Test Levelled (Level 2)')
        self.assertEqual(self.subj_annual.complete_name, 'ZZ Test Annual')

    @mute_logger('odoo.sql_db')
    def test_subject_unique_name_level(self):
        """UNIQUE(name, level) blocks a duplicate subject+level (DB constraint).

        NB: the DB unique index treats a NULL level as distinct, so it only
        catches duplicates when a level is set (un-levelled names can repeat).
        """
        with self.assertRaises(psycopg2.IntegrityError):
            with self.cr.savepoint():
                self.Subject.create({'name': 'ZZ Test Levelled', 'level': 'Level 2'})
                self.env.flush_all()

    def test_subject_same_name_different_level_ok(self):
        """The same subject name at a different level is allowed."""
        rec = self.Subject.create({'name': 'ZZ Test Annual', 'level': 'Level 2'})
        self.assertTrue(rec.id)

    def test_requirement_single_scope(self):
        """A requirement must attach to exactly one of profile/staff-group/member."""
        with self.assertRaises(ValidationError):
            self.Requirement.create({
                'subject_id': self.subj_annual.id,
                'profile_id': self.profile.id,
                'staff_group_id': self.staff_group.id,
            })

    def test_member_override_needs_type(self):
        """An individual-level requirement must state Add or Waive."""
        with self.assertRaises(ValidationError):
            self.Requirement.create({
                'subject_id': self.subj_annual.id,
                'member_id': self.member.id,
                'override_type': False,
            })

    def test_waive_needs_reason(self):
        """A waived requirement must record an exemption reason."""
        with self.assertRaises(ValidationError):
            self.Requirement.create({
                'subject_id': self.subj_annual.id,
                'member_id': self.member.id,
                'override_type': 'waive',
            })

    def test_resolution_from_profile_and_staff_group(self):
        """Required subjects resolve from the profile plus staff-group requirements."""
        # Add a staff-group requirement for the one-off subject.
        self.Requirement.create({
            'staff_group_id': self.staff_group.id, 'subject_id': self.subj_oneoff.id})
        subjects = self.member.required_subject_ids
        self.assertIn(self.subj_annual, subjects, 'from the profile')
        self.assertIn(self.subj_oneoff, subjects, 'from the staff group')

    def test_individual_add_and_waive(self):
        """An individual Add extends, and a Waive exempts, the resolved set."""
        # Add subj_extra individually.
        self.Requirement.create({
            'member_id': self.member.id, 'subject_id': self.subj_extra.id,
            'override_type': 'add'})
        self.assertIn(self.subj_extra, self.member.required_subject_ids)
        # Waive the profile's annual subject → it becomes exempt (still listed, but
        # excluded from the required count).
        self.Requirement.create({
            'member_id': self.member.id, 'subject_id': self.subj_annual.id,
            'override_type': 'waive', 'exemption_reason': 'On long-term secondment'})
        lines = self.member.get_requirement_lines()[self.member.id]
        annual_line = [l for l in lines if l['subject'] == self.subj_annual][0]
        self.assertTrue(annual_line['exempt'])

    def test_effective_frequency_override(self):
        """A requirement frequency override wins over the subject default."""
        self.Requirement.search([
            ('profile_id', '=', self.profile.id),
            ('subject_id', '=', self.subj_annual.id)]).frequency_months_override = 6
        self.assertEqual(
            self.member.get_effective_frequency_months(self.subj_annual), 6)
