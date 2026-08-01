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
from odoo.tests.common import tagged

from .common import NhsEstablishmentCommon


@tagged('post_install', '-at_install')
class TestChangeWizard(NhsEstablishmentCommon):
    """The 'Raise Change Request' wizard."""

    def test_wizard_creates_and_submits_change(self):
        """The wizard creates a change request and submits it by default."""
        post = self._make_post(funded_fte=1.0)
        wizard = self.env['nhs.establishment.change.wizard'].create({
            'change_type': 'increase_fte',
            'post_id': post.id,
            'proposed_fte': 2.0,
            'proposed_headcount': 2,
            'reason': 'Demand',
            'submit_immediately': True,
        })
        action = wizard.action_create_request()
        change = self.env['nhs.establishment.change'].browse(action['res_id'])
        self.assertEqual(change.post_id, post)
        self.assertEqual(change.proposed_fte, 2.0)
        self.assertEqual(change.state, 'submitted',
                         'submit_immediately should move it to submitted.')

    def test_wizard_leaves_draft_when_not_submitting(self):
        """Unticking submit leaves the change in draft."""
        post = self._make_post(funded_fte=1.0)
        wizard = self.env['nhs.establishment.change.wizard'].create({
            'change_type': 'increase_fte', 'post_id': post.id,
            'proposed_fte': 2.0, 'reason': 'Demand',
            'submit_immediately': False,
        })
        action = wizard.action_create_request()
        change = self.env['nhs.establishment.change'].browse(action['res_id'])
        self.assertEqual(change.state, 'draft')
