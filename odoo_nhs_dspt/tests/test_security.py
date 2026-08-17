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
from odoo.exceptions import AccessError
from odoo.tests.common import tagged
from odoo.tools import mute_logger

from .common import NhsDsptCommon


@tagged('post_install', '-at_install')
class TestSecurity(NhsDsptCommon):
    """Access-control model: user read-only, officer edit, manager config."""

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.models')
    def test_user_cannot_create_assessment(self):
        """A plain DSPT user cannot create assessments (perm_create=0)."""
        with self.assertRaises(AccessError):
            self.Assessment.with_user(self.user_plain).create({
                'edition_id': self.edition.id,
                'org_profile_id': self.profile_supplier.id,
                'ods_code': 'SEC-1',
            })

    def test_officer_can_create_assessment(self):
        """A DSPT officer can create assessments."""
        assessment = self.Assessment.with_user(self.user_officer).create({
            'edition_id': self.edition.id,
            'org_profile_id': self.profile_supplier.id,
            'ods_code': 'SEC-OFFICER-1',
        })
        self.assertTrue(assessment.id)

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.models')
    def test_officer_cannot_create_edition(self):
        """Edition definitions are manager-only config (officer has read-only)."""
        with self.assertRaises(AccessError):
            self.Edition.with_user(self.user_officer).create(
                {'name': 'X', 'year': '2097/98'})

    def test_manager_can_create_edition(self):
        """A DSPT manager can create editions."""
        edition = self.Edition.with_user(self.user_manager).create(
            {'name': 'X', 'year': '2096/97'})
        self.assertTrue(edition.id)

    def test_officer_sees_all_evidence(self):
        """An officer is unrestricted by the owner record-rule."""
        count = self.Evidence.with_user(self.user_officer).search_count(
            [('assessment_id', '=', self.assessment.id)])
        self.assertEqual(count, 20)

    def test_assessment_company_default(self):
        """A new assessment defaults to the current company."""
        self.assertEqual(self.assessment.company_id, self.company)
