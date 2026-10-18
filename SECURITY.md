# Security policy

## Reporting a vulnerability

Use GitHub's private vulnerability reporting on this repository ("Report a vulnerability" under
the Security tab). Do not open a public issue for a security problem, and do not include tokens,
thread contents or files people shared in a report.

## What counts

- Any path that lets model output, a Slack message, a file someone shares, Paper canvas content,
  MCP metadata or a web page change policy, reveal a secret, reach a tool outside the assembled
  surface, or send anything outside the thread.
- Credentials reaching the sandbox, a prompt, graph state, a log, an error, a Slack block, a
  fixture or a snapshot.
- Sandbox escapes: reading or writing outside `/workspace`, reaching the Docker socket, the host,
  cloud metadata, or the network when egress is denied.
- Server-side request forgery through `fetch_asset` or any URL the agent is given.
- Paper scope bypass: writing to the protected brand file, deleting nodes or writing tokens when
  disabled, `paper-gen:`/`paper-asset:`/`file:` URLs reaching the canvas.
- Delivering a file twice, delivering a file the thread did not produce, or claiming a delivery
  that did not happen.
- Bridge or API authentication bypass, DNS rebinding against the Paper bridge, thread ownership
  bypass on the self-hosted API, or Slack signature verification bypass.

## What we commit to

- Acknowledge reports within five business days.
- Keep defaults safe: sandbox egress denied, Paper off, deletes and token writes off, nothing
  published or sent outside the thread.
- Publish fixes with a changelog entry and, where relevant, a regression test in `tests/`.

## Supported versions

Only the `main` branch is supported before the first tagged release.
