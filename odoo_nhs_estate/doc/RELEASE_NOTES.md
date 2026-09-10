## Module <odoo_nhs_estate>

#### 09.09.2026
#### Version 19.0.1.0.0
#### UPDATE

- Added an automated test suite (tests/): 47 tests across hierarchy roll-ups,
  codes/constraints, spaces, condition surveys, tenure, backlog and security
  (TransactionCase / Form). Green on Community and Enterprise.
- Converted the build-year and target-year checks from @api.onchange to
  @api.constrains so invalid years are also rejected on create/import, not just
  in the form; removed the now-redundant backlog write() override.
- Added titles to decorative Font Awesome icons across the estate views (view
  accessibility) and switched the estate reports from t-esc to t-out.

#### 18.08.2026
#### Version 19.0.1.0.0
#### ADD

- Initial commit for NHS Estate Register
