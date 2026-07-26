# Security

## Credential boundary

Credentials are runtime configuration, not source. `.env`, `.private`, tokens,
cookies, authenticated URLs, and provider caches are prohibited from the handoff
release. `.env.example` contains placeholders only.

## Runtime boundary

Frozen mode is provider-free. Cloud mode does not load a local private file or
probe local IBKR. Local mode binds to loopback. The application exposes no account,
position, order, execution, or trading capability.

## Output boundary

Public API errors and release tools omit secret values, private absolute paths,
tracebacks, and personal identifiers. The release audit reports category, relative
path, line number, and counts while withholding matched content.

## Operator responsibilities

- Store credentials in the deployment platform's secret manager.
- Use a unique read-only IBKR client identifier.
- Apply provider rate limits and entitlements.
- Run the release audit and an independent secret scanner before distribution.
- Rotate any credential found in tracked content; the application does not rotate
  credentials automatically.
