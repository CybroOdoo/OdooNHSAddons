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
from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import NhsDsptCommon


@tagged('post_install', '-at_install')
class TestWizards(NhsDsptCommon):
    """The generate / new-edition / bulk-owner / carry-forward wizards."""

    def test_generate_wizard(self):
        """The generate wizard populates a fresh assessment's lines."""
        assessment = self.Assessment.create({
            'edition_id': self.edition.id,
            'org_profile_id': self.profile_supplier.id,
            'ods_code': 'WIZ-GEN-1',
        })
        wizard = self.env['nhs.dspt.generate.wizard'].create(
            {'assessment_id': assessment.id})
        wizard.action_confirm()
        self.assertTrue(assessment.evidence_ids)
        self.assertEqual(assessment.state, 'in_progress')

    def test_new_edition_wizard(self):
        """The new-edition wizard clones the source edition to a new year."""
        wizard = self.env['nhs.dspt.new.edition.wizard'].create({
            'source_edition_id': self.edition.id,
            'new_year': '2101/02',
            'new_name': 'DSPT 2101/02',
        })
        action = wizard.action_confirm()
        new_edition = self.Edition.browse(action['res_id'])
        self.assertEqual(new_edition.year, '2101/02')
        self.assertEqual(new_edition.state, 'draft')
        self.assertTrue(new_edition.standard_ids)

    def test_bulk_owner_wizard(self):
        """The bulk-owner wizard reassigns several evidence items at once."""
        evidence = self.assessment.evidence_ids[:5]
        wizard = self.env['nhs.dspt.bulk.owner.wizard'].with_context(
            active_model='nhs.dspt.evidence',
            active_ids=evidence.ids,
        ).create({'owner_id': self.user_officer.id})
        wizard.action_confirm()
        self.assertTrue(all(e.owner_id == self.user_officer for e in evidence))

    def test_bulk_owner_wizard_rejects_bad_model(self):
        """The bulk-owner wizard only works from evidence/assertion lists."""
        with self.assertRaises(UserError):
            self.env['nhs.dspt.bulk.owner.wizard'].with_context(
                active_model='res.partner', active_ids=[1],
            ).create({'owner_id': self.user_officer.id})

    def test_carry_forward_wizard(self):
        """The carry-forward wizard copies prior answers into a new assessment."""
        self._ev('2.1.1').write({'status': 'met', 'answer': 'Contracts updated.'})
        new_edition = self.edition.copy_edition(new_year='2102/03')
        new_edition.action_activate()
        new_assessment = self.Assessment.create({
            'edition_id': new_edition.id,
            'org_profile_id': self.profile_trust.id,
        })
        new_assessment.action_generate()
        wizard = self.env['nhs.dspt.carry.forward.wizard'].create({
            'assessment_id': new_assessment.id,
            'prior_assessment_id': self.assessment.id,
        })
        wizard.action_confirm()
        self.assertEqual(self._ev('2.1.1', assessment=new_assessment).answer,
                         'Contracts updated.')
