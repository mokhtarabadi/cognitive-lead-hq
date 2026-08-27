<immutable_financial_ledger_mandate>
To prevent silent data corruption and financial drift, you MUST enforce the Universal Financial Ledger Standard across all financial, transactional, and countable data operations.

### Core Mandates

1. **Snapshot-on-Write for Mutable Totals:** Whenever a financial amount, inventory count, or balance is mutated, you MUST persist a read-only snapshot of the state immediately preceding the mutation. This snapshot must be stored in a sidecar table, an immutable audit log, or a write-ahead log. Banned: allowing mutations on a mutable column without preserving the prior value in the same transaction.
2. **Mandatory `$ifNull` Precedence:** All aggregation queries (SUM, AVG, COUNT on monetary fields) MUST use explicit null-handling functions (`$ifNull`, `COALESCE`, `ISNULL`). Banned: passing nullable columns directly into mathematical operators — unhandled nulls silently return null, causing silent data loss.
3. **Observability Alerting on Ledger Discrepancies:** If a computed total diverges from the sum of its constituent line items by more than 0.01 (or the currency's smallest indivisible unit), the system MUST emit a high-severity alert and prevent the transaction from finalizing. Banned: allowing writes to complete when reconciliation fails.
4. **Deep Config Merging for Financial Settings:** Financial configuration (tax rates, currency codes, rounding rules) MUST be deeply merged, not shallowly overwritten. A partial update to a financial config object MUST preserve all sibling properties. Banned: using shallow object spread or simple assignment when updating nested financial configuration.
</immutable_financial_ledger_mandate>