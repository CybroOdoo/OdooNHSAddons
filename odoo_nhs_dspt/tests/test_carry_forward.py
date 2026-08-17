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

from .common import NhsDsptCommon


@tagged('post_install', '-at_install')
class TestCarryForward(NhsDsptCommon):
    """Carrying answers/owners forward from a prior assessment by reference."""

    def test_carry_forward_answers_and_owner(self):
        """Answers, status and owner are copied to matching references in a new
        edition's assessment (matched by evidence reference, not record id)."""
        # Complete the prior (current) assessment's 1.1.1 item.
        prior_ev = self._ev('1.1.1')
        prior_ev.write({
            'status': 'met',
            'answer': 'We have a DPO in place.',
            'owner_id': self.user_officer.id,
            'evidence_review_date': '2026-02-01',
        })

        # A new edition cloned from the current one, activated.
        new_edition = self.edition.copy_edition(new_year='2100/01')
        new_edition.action_activate()
        new_assessment = self.Assessment.create({
            'edition_id': new_edition.id,
            'org_profile_id': self.profile_trust.id,
            'prior_assessment_id': self.assessment.id,
        })
        new_assessment.action_generate()

        updated = new_assessment.action_carry_forward()
        self.assertGreater(updated, 0)
        new_ev = self._ev('1.1.1', assessment=new_assessment)
        self.assertEqual(new_ev.status, 'met')
        self.assertEqual(new_ev.answer, 'We have a DPO in place.')
        self.assertEqual(new_ev.owner_id, self.user_officer)

    def test_carry_forward_no_prior_returns_zero(self):
        """Carrying forward with no prior assessment updates nothing."""
        lonely = self.Assessment.create({
            'edition_id': self.edition.id,
            'org_profile_id': self.profile_supplier.id,
            'ods_code': 'CF-NONE-1',
        })
        lonely.action_generate()
        self.assertEqual(lonely.action_carry_forward(), 0)
