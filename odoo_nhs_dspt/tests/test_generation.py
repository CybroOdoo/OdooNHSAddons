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
class TestGeneration(NhsDsptCommon):
    """action_generate: line creation, profile filtering, idempotency, state."""

    def test_generation_creates_lines(self):
        """Generating a Trust assessment creates 10 assertions and 20 evidence lines."""
        self.assertEqual(len(self.assessment.assertion_ids), 10)
        self.assertEqual(len(self.assessment.evidence_ids), 20)

    def test_generation_sets_in_progress(self):
        """Generating moves a draft assessment to in_progress."""
        self.assertEqual(self.assessment.state, 'in_progress')

    def test_profile_filtering_excludes_supplier_only(self):
        """The supplier-only evidence 10.1.3 is excluded from a Trust assessment,
        but its trust/gp/care siblings 10.1.1 / 10.1.2 are present."""
        self.assertFalse(self._ev('10.1.3'),
                         'Supplier-only evidence must not appear on a Trust assessment.')
        self.assertTrue(self._ev('10.1.1'))
        self.assertTrue(self._ev('10.1.2'))

    def test_supplier_profile_gets_supplier_evidence(self):
        """A Supplier assessment includes 10.1.3 and excludes trust/gp/care-only 10.1.1."""
        supplier_assessment = self.Assessment.create({
            'edition_id': self.edition.id,
            'org_profile_id': self.profile_supplier.id,
            'ods_code': 'SUP-TEST-1',  # avoid clash with the demo supplier assessment
        })
        supplier_assessment.action_generate()
        refs = supplier_assessment.evidence_ids.mapped('reference')
        self.assertIn('10.1.3', refs)
        self.assertNotIn('10.1.1', refs)

    def test_generation_idempotent(self):
        """Re-running generation does not duplicate existing lines."""
        before = len(self.assessment.evidence_ids)
        self.assessment.action_generate()
        self.assertEqual(len(self.assessment.evidence_ids), before)

    def test_mandatory_applicable_count(self):
        """18 mandatory-applicable evidence items for a Trust assessment."""
        self.assertEqual(len(self._mandatory()), 18)
