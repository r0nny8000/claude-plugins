# One-time install script

Offered after the install or update steps: some users would rather run one
reviewed file than copy commands. There's no template here on purpose; build
the script from the upstream steps you fetched in this session, so it's as
current as they are (ADR 0005).

## Write it

Write `/tmp/sc-install.sh` (ask before overwriting an existing one). It must:

- Start with `#!/usr/bin/env bash` and `set -euo pipefail`.
- Begin with a comment naming the sources you fetched, the `sc` version and
  today's date, and saying that it deletes itself after a successful install.
- Download the release asset for the check's `system` and `machine`, plus
  the `SHA256SUMS` file, into a `mktemp -d` folder, and check the asset with
  `sha256sum -c` (`shasum -a 256 -c` on macOS) before using it. If
  `minisign` is installed, also verify the signature as upstream's verify
  guide describes; otherwise print that it was skipped.
- Install without `sudo`: into `~/.local/bin`, or the method upstream names
  for the system (e.g. its Homebrew tap). Warn if that folder isn't on
  `PATH`.
- Save its own path with `self="$(realpath -- "$0")"` before any `cd`
  (`$0` can be relative), run `sc --version`, and delete itself with
  `rm -- "$self"` as the last command. `set -e` stops it earlier on any
  failure, so a failed run leaves the file to read and rerun.
- Before deleting itself, print the next steps: enable the CLI on the Scalable web
  platform, then run `sc login` yourself. Never run `sc login` in the
  script; upstream says to log in yourself.

Mark the commands that aren't upstream's (for example, where upstream
describes a step only in words) with a comment, as in the answer.

## Hand it over

- Don't run it, `chmod` it, or `bash -n` it as the user; that's their call
  (ADR 0004).
- Tell the user to read it first, then run `bash /tmp/sc-install.sh`. It
  removes itself when it succeeds; `/tmp` is cleared on reboot otherwise.
