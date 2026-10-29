# Install and set up sc

Show these steps to the user; they run them. Don't run any of them yourself
unless the user explicitly asks you to run a specific command after seeing
it (ADR 0004). Written for release v1.2.0 (2026-10-22); check
https://github.com/ScalableCapital/scalable-cli#install if the steps look stale.

Replace `vX.Y.Z` with the `latest_version` from `check_install.py`, prefixed
with `v` (for example `v1.2.0`).

## Contents

- Linux (x86_64 or aarch64)
- macOS
- Verify the download (optional)
- Update
- Enable and log in

## Linux (x86_64 or aarch64)

Official binaries need glibc 2.38 or newer (the check script reports `libc`).
Debian 12 (glibc 2.36) and musl distributions such as Alpine can't run them;
building from source is the upstream workaround.

1. Download `sc-vX.Y.Z-linux-<arch>-gnu.tar.gz` for your architecture from
   https://github.com/ScalableCapital/scalable-cli/releases/latest, where
   `<arch>` is `x86_64` or `aarch64` (the `machine` field of the check).
2. Optional: verify it (see below).
3. Extract it and put `sc` on your `PATH`:

   ```bash
   tar -xzf sc-vX.Y.Z-linux-aarch64-gnu.tar.gz
   mkdir -p ~/.local/bin
   mv sc ~/.local/bin/
   sc --version
   ```

   `~/.local/bin` is one choice; any directory on `PATH` works. If the archive
   unpacks into a folder, move `sc` from there.

On a server or container without a Secret Service keyring, add this to
`~/.config/scalable-cli/config.toml` (or `$XDG_CONFIG_HOME/scalable-cli/`)
before logging in. Session secrets are then stored in local files:

```toml
[auth]
session_backend = "file"
```

## macOS

Homebrew:

```bash
brew tap ScalableCapital/tap
brew trust --formula ScalableCapital/tap/scalable-cli
brew install scalable-cli
```

Or download the PKG installer `sc-vX.Y.Z-macos-universal2.pkg` from the
latest release and run it.

## Verify the download (optional)

Needs `gh` and `minisign`. Run in the download folder; set `arch` for Linux.

```bash
tag="vX.Y.Z"
arch="aarch64" # or x86_64
repo="ScalableCapital/scalable-cli"
minisign_public_key="RWRKuuSASIzbSYpuU5gdXeTkXirJBl5+XVXLP6E60hBUUKZ5HPIGjV8b"

asset="sc-${tag}-linux-${arch}-gnu.tar.gz"
checksums="sc-${tag}-SHA256SUMS"

gh release download "${tag}" \
  --repo "${repo}" \
  --pattern "${asset}" \
  --pattern "${checksums}" \
  --pattern "${checksums}.minisig" \
  --clobber

minisign -V \
  -P "${minisign_public_key}" \
  -m "${checksums}" \
  -x "${checksums}.minisig"

set -o pipefail
grep -F "  ${asset}" "${checksums}" | sha256sum -c -
```

For the macOS PKG and the Homebrew ZIP, see
https://github.com/ScalableCapital/scalable-cli/blob/main/public-docs/verify-releases.md.

## Update

- Homebrew: `brew upgrade scalable-cli`.
- Linux and PKG: repeat the install with the new release; it replaces `sc`.

JSON output isn't guaranteed stable across releases; read the release notes
before updating a script that parses it.

## Enable and log in

1. On the Scalable web platform, enable Scalable CLI under
   Profile > Security > Agentic Investing.
2. In your own terminal, not through Claude, run `sc login` and complete the
   device-code login in the browser. `sc login --local-read-only` blocks
   write commands locally (it doesn't restrict the backend token).
3. Check it with `sc whoami`.

A session ends after 24 hours without a request and at most seven days after
login; then run `sc login` again.
