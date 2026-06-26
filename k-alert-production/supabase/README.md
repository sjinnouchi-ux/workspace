# Supabase

This directory contains database migrations for the K Alert production Supabase project.

Target project:

```text
Project name: k-alert-production-tokyo
Project ref: ctuqydrapwfxvkdtdzna
Region: Northeast Asia (Tokyo), ap-northeast-1
```

Do not commit database passwords, API keys, service role keys, or `.env` files.

## Initial Migration

`migrations/20260625115000_initial_schema.sql` creates the initial application schema:

- LINE user identities
- cases
- webhook event deduplication
- messages
- AI extractions
- investigator sessions
- ChatWork notifications
- AI response rules
- rule reviews
- reports
- audit logs

RLS is enabled for all application tables. Policies are intentionally not opened in this migration; the FastAPI backend should use server-side credentials, and user-facing access policies should be added deliberately when a client/admin UI exists.

