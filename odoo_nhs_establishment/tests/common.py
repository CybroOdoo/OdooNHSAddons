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
"""Shared fixtures for the NHS Establishment Register test suite."""
from odoo.tests.common import TransactionCase


class NhsEstablishmentCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.OrgUnit = cls.env['nhs.org.unit']
        cls.Post = cls.env['nhs.establishment.post']
        cls.Change = cls.env['nhs.establishment.change']
        cls.CostCentre = cls.env['nhs.cost.centre']
        cls.StaffGroup = cls.env['nhs.staff.group']
        cls.Band = cls.env['nhs.afc.band']

        cls.company = cls.env.company
        # Deterministic pay maths for the assertions below.
        cls.company.write({
            'nhs_full_time_hours_basis': 37.5,
            'nhs_on_cost_factor': 1.0,
            'nhs_change_control_required': True,
            'nhs_change_control_single_stage': False,
        })

        # Seed reference data shipped by the module.
        cls.staff_group = cls.env.ref(
            'odoo_nhs_establishment.staff_group_nursing_midwifery')
        cls.band5 = cls.env.ref('odoo_nhs_establishment.afc_band_5')  # 29970
        cls.band6 = cls.env.ref('odoo_nhs_establishment.afc_band_6')  # 37338

        cls.cost_centre = cls.CostCentre.create({
            'name': 'Main Theatres', 'code': 'CC-THEATRE',
            'budget_amount': 500000.0,
        })

        # A two-level org hierarchy: Surgery > Theatres.
        cls.unit_parent = cls.OrgUnit.create({
            'name': 'Surgery', 'unit_type': 'directorate',
        })
        cls.unit_child = cls.OrgUnit.create({
            'name': 'Theatres', 'unit_type': 'team',
            'parent_id': cls.unit_parent.id,
            'cost_centre': cls.cost_centre.id,
        })

        # ── Groups & users (Odoo 19: group_ids, not groups_id) ────────────
        cls.group_user = cls.env.ref('odoo_nhs_establishment.group_nhs_workforce_user')
        cls.group_officer = cls.env.ref('odoo_nhs_establishment.group_nhs_workforce_officer')
        cls.group_manager = cls.env.ref('odoo_nhs_establishment.group_nhs_workforce_manager')

        cls.user_readonly = cls.env['res.users'].create({
            'name': 'WF User', 'login': 'wf_user', 'email': 'u@nhs.test',
            'group_ids': [(6, 0, [cls.env.ref('base.group_user').id, cls.group_user.id])],
        })
        cls.user_officer = cls.env['res.users'].create({
            'name': 'WF Officer', 'login': 'wf_officer', 'email': 'o@nhs.test',
            'group_ids': [(6, 0, [cls.env.ref('base.group_user').id, cls.group_officer.id])],
        })
        cls.user_manager = cls.env['res.users'].create({
            'name': 'WF Manager', 'login': 'wf_manager', 'email': 'm@nhs.test',
            'group_ids': [(6, 0, [cls.env.ref('base.group_user').id, cls.group_manager.id])],
        })

    @classmethod
    def _make_post(cls, **overrides):
        """Create an ACTIVE funded post (counts in roll-ups) on Band 5."""
        vals = {
            'job_title': 'Theatre Nurse',
            'org_unit_id': cls.unit_child.id,
            'staff_group_id': cls.staff_group.id,
            'band_id': cls.band5.id,
            'funded_fte': 1.0,
            'in_post_fte': 1.0,
            'status': 'active',
        }
        vals.update(overrides)
        return cls.Post.create(vals)
