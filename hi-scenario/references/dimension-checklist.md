# 12-Dimension Edge Case Checklist

Per-dimension prompt questions for `hi-scenario` analysis.

## 1. User Types
- [ ] What happens when an **unauthenticated** user accesses this?
- [ ] What happens when an **admin** vs **regular user** vs **moderator** uses this?
- [ ] What happens with **banned/suspended** user sessions?
- [ ] What happens for a **brand-new user** (no data, no history)?
- [ ] What happens for a **power user** (extreme usage patterns)?
- [ ] What happens when accessed by a **bot/scraper** (non-human user agent)?

## 2. Input Extremes
- [ ] Empty string / null / undefined for every input field
- [ ] Maximum length strings (e.g., 1MB text in a name field)
- [ ] Unicode characters, emoji, RTL text, zero-width characters
- [ ] Special characters: `<script>`, `' OR 1=1 --`, `../../../etc/passwd`
- [ ] Negative numbers where only positive expected
- [ ] Extremely large numbers (overflow potential)
- [ ] Non-ASCII email addresses (international domains)
- [ ] Malformed JSON / XML in request bodies

## 3. Timing
- [ ] What if two users submit the same form at the exact same time?
- [ ] What if the database is slow (5s query time)?
- [ ] What if an external API call times out?
- [ ] What if the user double-clicks the submit button?
- [ ] What if a scheduled job overlaps with manual action?
- [ ] What if network latency causes request reordering?

## 4. Scale
- [ ] Empty list (0 items) — does the UI handle it gracefully?
- [ ] Single item — edge case for "select all" and batch operations
- [ ] 10,000+ items — pagination, memory, rendering performance
- [ ] Pagination boundary: exactly N items on the last page
- [ ] Cursor-based pagination wrap-around
- [ ] Concurrent list modification while paginating

## 5. State Transitions
- [ ] First-time use: no prior state exists
- [ ] User aborts mid-flow (closes browser, goes back)
- [ ] Resume after crash — can the flow recover?
- [ ] Partial completion — is intermediate state valid?
- [ ] Invalid state transitions (skip step, go backwards)
- [ ] State machine deadlock / unreachable states

## 6. Environment
- [ ] Mobile device with low CPU and memory
- [ ] Browser with JavaScript disabled
- [ ] Screen reader / accessibility tool
- [ ] Behind corporate proxy or VPN
- [ ] Different timezone (UTC+14 to UTC-12)
- [ ] Different locale (date formats, number formats, RTL)
- [ ] Slow 3G connection

## 7. Error Cascades
- [ ] Database connection fails — what error does user see?
- [ ] External API returns 500 — does the system degrade gracefully?
- [ ] Disk full — can writes fail without corruption?
- [ ] Out of memory — does the process crash cleanly?
- [ ] Network partition — split-brain scenario
- [ ] Partial writes — transaction rollback behavior
- [ ] Message queue full — backpressure handling

## 8. Authorization
- [ ] Expired JWT token accessing protected route
- [ ] User with wrong role accessing admin endpoint
- [ ] Shared/leaked access token — can it be revoked?
- [ ] CORS misconfiguration — cross-origin request allowed?
- [ ] CSRF token missing on state-changing request
- [ ] Horizontal privilege escalation (access other user's data)
- [ ] Vertical privilege escalation (user → admin)

## 9. Data Integrity
- [ ] Duplicate entries — does unique constraint fail cleanly?
- [ ] Orphan references — child record without parent
- [ ] Encoding mismatch (UTF-8 vs Latin-1 in database)
- [ ] Concurrent schema migration while writes occur
- [ ] Soft deletes — can related records become inconsistent?
- [ ] Circular foreign key references

## 10. Integration
- [ ] Webhook replay — idempotency handling
- [ ] API version mismatch between services
- [ ] Third-party service outage — graceful degradation
- [ ] Contract drift — field added/removed in upstream API
- [ ] Rate limiting by external API
- [ ] SSL certificate expiry on external endpoint

## 11. Compliance
- [ ] GDPR deletion request — all user data removed?
- [ ] Audit logging gap — who did what and when?
- [ ] Data retention policy — old data purged correctly?
- [ ] Accidental PII exposure in logs or error messages
- [ ] Consent tracking — user opted out but data still collected?
- [ ] Data export — can user download all their data?

## 12. Business Logic
- [ ] Edge pricing: $0.00 item, negative price, currency rounding
- [ ] Coupon stacking: multiple discounts combining unexpectedly
- [ ] Refund after partial delivery — correct amount?
- [ ] Free tier limits: exactly at limit, 1 over limit
- [ ] Subscription: trial end, payment failure, upgrade/downgrade
- [ ] Loyalty points: earned, redeemed, expired simultaneously
