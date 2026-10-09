## Module <odoo_nhs_complaints>

#### 09.10.2026
#### Version 19.0.1.0.0
#### UPDATE

- Fixed the Duty of Candour warning on complaints: its compute depended on a
  non-existent nhs.incident.doc_state field, which blocked module install. It
  now reads the linked incident's doc_id.state.

#### 12.06.2026
#### Version 19.0.1.0.0
#### ADD

- Initial commit for NHS Complaints & PALS Management
