# Example: Work Breakdown Document

This is an example of a work breakdown that the skill can turn into JIRA tickets.
The agent reads this document, extracts each ticket's summary, description, and
acceptance criteria, then builds the `tickets.json` input file automatically.

The format below is not strict — the agent will adapt to whatever structure the
user provides. But this layout works well because each section maps cleanly to
JIRA fields.

---

## Work Breakdown

### Ticket 1: Add OAuth2 Authentication

**Summary:** Implement OAuth2 client credentials flow for API authentication

**Description:**
Replace the current API key authentication with OAuth2 client credentials flow.
The server should request tokens from the identity provider, cache them until
expiry, and automatically refresh when needed.

**Scope:**
- Create `TokenManager` class with `getToken()` and `refreshToken()` methods
- Token caching with expiry-aware refresh (refresh 60s before expiry)
- Support configurable token endpoint URL
- Retry logic for transient auth failures (429, 503)
- Unit tests for token lifecycle (fresh, cached, expired, refresh failure)

**Acceptance Criteria:**
- [ ] `getToken()` returns a valid Bearer token
- [ ] Tokens are cached and reused until near expiry
- [ ] Expired tokens trigger automatic refresh
- [ ] Token endpoint URL is configurable via config file
- [ ] Auth failures produce clear error messages
- [ ] Unit tests cover all token states

**Dependencies:** None
**Estimate:** Medium

---

### Ticket 2: Rate Limiting and Retry Logic

**Summary:** Add configurable rate limiting with exponential backoff retry

**Description:**
API calls should respect rate limits and retry transient failures automatically.
Implement a request wrapper that handles 429 (Too Many Requests) and 5xx errors
with exponential backoff.

**Scope:**
- Request wrapper with configurable retry count and backoff multiplier
- Parse `Retry-After` header from 429 responses
- Exponential backoff: 1s, 2s, 4s, 8s (configurable base and max)
- Circuit breaker: stop retrying after N consecutive failures
- Logging for each retry attempt with reason and delay

**Acceptance Criteria:**
- [ ] 429 responses trigger retry with `Retry-After` delay
- [ ] 5xx responses trigger retry with exponential backoff
- [ ] 4xx responses (except 429) fail immediately without retry
- [ ] Maximum retry count is configurable
- [ ] Circuit breaker trips after consecutive failures
- [ ] All retries are logged with attempt number and delay

**Dependencies:** Ticket 1 (auth tokens needed for API calls)
**Estimate:** Small

---

### Ticket 3: Integration Test Suite

**Summary:** Add end-to-end integration tests against a mock API server

**Description:**
Create an integration test suite that validates the full request lifecycle:
authentication, request building, rate limiting, and response parsing.
Use a local mock server to simulate API responses without hitting production.

**Scope:**
- Mock server using `msw` (Mock Service Worker) for HTTP interception
- Test scenarios: successful auth, expired token refresh, rate limit handling
- Test both happy path and error paths
- CI-compatible: runs without external dependencies
- Test report generation

**Acceptance Criteria:**
- [ ] Mock server starts and responds to auth and API requests
- [ ] Tests cover: fresh auth, token refresh, 429 retry, 5xx retry, 4xx failure
- [ ] Tests run in CI without external service dependencies
- [ ] Test report is generated after each run
- [ ] All tests pass on Node.js 18 and 20

**Dependencies:** Tickets 1 and 2
**Estimate:** Medium
