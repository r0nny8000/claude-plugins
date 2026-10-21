# scalable-cli

A skill for the Scalable CLI `sc`, the official command line for the Scalable
Broker by Scalable Capital. This skill is unofficial and not affiliated with
Scalable Capital.

## Requirements

The skill doesn't install anything. It checks for `sc` and shows the install
steps for your system; you run them.

| Requirement          | Needed   | Notes                                                                                   |
|----------------------|----------|-----------------------------------------------------------------------------------------|
| `sc`, latest release | required | macOS: Homebrew or PKG. Linux: tarball for `x86_64` or `aarch64`, binary on your `PATH` |
| Scalable CLI enabled | required | On the Scalable web platform under Profile > Security > Agentic Investing               |
| `sc login`           | required | Run it yourself, not through Claude; `sc login --local-read-only` blocks write commands |
| `gh`, `minisign`     | optional | Download a release and verify its signed checksums                                      |

## Scalable CLI documentation

All the official documentation is in the repo README, on GitHub under the
ScalableCapital organization.

| Topic                       | Link                                                                        |
|-----------------------------|-----------------------------------------------------------------------------|
| Repository                  | https://github.com/ScalableCapital/scalable-cli                             |
| Releases and downloads      | https://github.com/ScalableCapital/scalable-cli/releases                    |
| Install                     | https://github.com/ScalableCapital/scalable-cli#install                     |
| Quick start and login       | https://github.com/ScalableCapital/scalable-cli#quick-start                 |
| Release artifact provenance | https://github.com/ScalableCapital/scalable-cli#release-artifact-provenance |
| Common commands             | https://github.com/ScalableCapital/scalable-cli#common-commands             |
| Trading                     | https://github.com/ScalableCapital/scalable-cli#trading                     |
| Automation                  | https://github.com/ScalableCapital/scalable-cli#automation                  |
| Help                        | https://github.com/ScalableCapital/scalable-cli#help                        |
| Configuration               | https://github.com/ScalableCapital/scalable-cli#configuration               |
| Security policy             | https://github.com/ScalableCapital/scalable-cli/blob/main/SECURITY.md       |

Before `sc` can be used, Scalable CLI has to be enabled on the Scalable web
platform under Profile > Security > Agentic Investing. Run `sc login` yourself
rather than through an AI agent, as the upstream README advises.
