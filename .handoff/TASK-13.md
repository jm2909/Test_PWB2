# TASK-13 handoff

- `POST /api/v1/support-requests` (Bearer) -> 201 `{id, reference, status: "submitted", submitted_at}`.
- Reference `SUP-<16 hex>`. Context: `device` -> own connection, `alert` -> own alert, `account` -> no `context_id` (422 if given); unknown or foreign id -> 404.
- Audit event `support.submitted` stores category, context_type and reference only.
- Seed: one asha request `SUP-SEED-0001` (idempotent).
- Frontend `/support?context=alert&id=...` links (TASK-12) still need a support page.
