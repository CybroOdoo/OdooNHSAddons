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
"""Shared fixtures for the NHS Estate Register test suite."""
from odoo.tests.common import TransactionCase


class NhsEstateCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Site = cls.env['nhs.estate.site']
        cls.Building = cls.env['nhs.estate.building']
        cls.Floor = cls.env['nhs.estate.floor']
        cls.Space = cls.env['nhs.estate.space']
        cls.Condition = cls.env['nhs.estate.condition']
        cls.Tenure = cls.env['nhs.estate.tenure']
        cls.Backlog = cls.env['nhs.estate.backlog']
        cls.Function = cls.env['nhs.estate.function']

        cls.company = cls.env.company

        # Two functions: a clinical and a non-clinical use.
        cls.func_clinical = cls.Function.create({'name': 'ZZ Ward', 'is_clinical': True})
        cls.func_admin = cls.Function.create({'name': 'ZZ Admin', 'is_clinical': False})

        # A site with an explicit code.
        cls.site = cls.Site.create({'name': 'St Test Hospital', 'code': 'sth'})
        cls.building = cls.Building.create({
            'name': 'Main Block', 'code': 'MB1', 'site_id': cls.site.id})
        cls.floor = cls.Floor.create({
            'name': 'Ground Floor', 'building_id': cls.building.id, 'sequence': 0})

        # Two spaces: clinical/occupied (60 m²) and admin/vacant (40 m²).
        cls.space_clin = cls.Space.create({
            'name': 'Ward 1', 'floor_id': cls.floor.id, 'area': 60.0,
            'function_id': cls.func_clinical.id, 'utilisation': 'full',
        })
        cls.space_admin = cls.Space.create({
            'name': 'Office 1', 'floor_id': cls.floor.id, 'area': 40.0,
            'function_id': cls.func_admin.id, 'utilisation': 'empty',
        })

        # ── Groups & users (Odoo 19: group_ids, not groups_id) ────────────
        cls.group_user = cls.env.ref('odoo_nhs_estate.group_nhs_estate_user')
        cls.group_officer = cls.env.ref('odoo_nhs_estate.group_nhs_estate_officer')
        cls.group_manager = cls.env.ref('odoo_nhs_estate.group_nhs_estate_manager')

        cls.user_viewer = cls.env['res.users'].create({
            'name': 'Estate Viewer', 'login': 'estate_viewer', 'email': 'v@estate.test',
            'group_ids': [(6, 0, [cls.group_user.id])],
        })
        cls.user_officer = cls.env['res.users'].create({
            'name': 'Estate Officer', 'login': 'estate_officer', 'email': 'o@estate.test',
            'group_ids': [(6, 0, [cls.group_officer.id])],
        })
        cls.user_manager = cls.env['res.users'].create({
            'name': 'Estate Manager', 'login': 'estate_manager', 'email': 'm@estate.test',
            'group_ids': [(6, 0, [cls.group_manager.id])],
        })
