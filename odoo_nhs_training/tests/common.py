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
"""Shared fixtures for the NHS Mandatory Training Register test suite."""
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class NhsTrainingCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Subject = cls.env['nhs.training.subject']
        cls.Requirement = cls.env['nhs.training.requirement']
        cls.Profile = cls.env['nhs.requirement.profile']
        cls.Member = cls.env['nhs.workforce.member']
        cls.Record = cls.env['nhs.training.record']
        cls.Registration = cls.env['nhs.registration']
        cls.Regulator = cls.env['nhs.regulator']
        cls.OrgUnit = cls.env['nhs.org.unit']
        cls.Post = cls.env['nhs.establishment.post']

        cls.company = cls.env.company

        # Reference data from the establishment dependency.
        cls.staff_group = cls.env.ref('odoo_nhs_establishment.staff_group_nursing_midwifery')
        cls.band5 = cls.env.ref('odoo_nhs_establishment.afc_band_5')
        cls.nmc = cls.env.ref('odoo_nhs_training.regulator_nmc')

        # Org hierarchy: Division > Ward.
        cls.division = cls.OrgUnit.create({'name': 'Surgery Division', 'unit_type': 'division'})
        cls.ward = cls.OrgUnit.create({
            'name': 'Ward A', 'unit_type': 'team', 'parent_id': cls.division.id})

        # Two subjects: an annual (expiring) one and a one-off induction.
        # Test-unique subject names to avoid clashing with shipped seed subjects
        # (UNIQUE(name, level)).
        cls.subj_annual = cls.Subject.create({
            'name': 'ZZ Test Annual', 'training_class': 'mandatory',
            'default_frequency_months': 12, 'default_lead_days': 60,
        })
        cls.subj_oneoff = cls.Subject.create({
            'name': 'ZZ Test Induction', 'training_class': 'statutory',
            'is_one_off': True,
        })
        cls.subj_extra = cls.Subject.create({
            'name': 'ZZ Test Levelled', 'level': 'Level 2',
            'training_class': 'statutory', 'default_frequency_months': 36,
        })

        # A requirement profile requiring the annual subject.
        cls.profile = cls.Profile.create({'name': 'Ward Nurse'})
        cls.Requirement.create({
            'profile_id': cls.profile.id, 'subject_id': cls.subj_annual.id,
            'is_mandatory': True,
        })

        # A member on that profile.
        cls.member = cls.Member.create({
            'name': 'Jo Nurse', 'org_unit_id': cls.ward.id,
            'staff_group_id': cls.staff_group.id,
            'requirement_profile_id': cls.profile.id,
            'email': 'jo@nhs.test',
        })

        # ── Groups & users (Odoo 19: group_ids, not groups_id) ────────────
        cls.group_user = cls.env.ref('odoo_nhs_training.group_nhs_training_user')
        cls.group_officer = cls.env.ref('odoo_nhs_training.group_nhs_training_officer')
        cls.group_manager = cls.env.ref('odoo_nhs_training.group_nhs_training_manager')

        cls.user_viewer = cls.env['res.users'].create({
            'name': 'Train Viewer', 'login': 'train_viewer', 'email': 'v@train.test',
            'group_ids': [(6, 0, [cls.env.ref('base.group_user').id, cls.group_user.id])],
        })
        cls.user_officer = cls.env['res.users'].create({
            'name': 'Train Officer', 'login': 'train_officer', 'email': 'o@train.test',
            'group_ids': [(6, 0, [cls.env.ref('base.group_user').id, cls.group_officer.id])],
        })
        cls.user_manager = cls.env['res.users'].create({
            'name': 'Train Manager', 'login': 'train_manager', 'email': 'm@train.test',
            'group_ids': [(6, 0, [cls.env.ref('base.group_user').id, cls.group_manager.id])],
        })

    @classmethod
    def _record(cls, member=None, subject=None, completion_date=None, **kw):
        vals = {
            'member_id': (member or cls.member).id,
            'subject_id': (subject or cls.subj_annual).id,
            'completion_date': completion_date or fields.Date.context_today(cls.env['nhs.training.record']),
        }
        vals.update(kw)
        return cls.Record.create(vals)
