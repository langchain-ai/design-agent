# Open fonts

Every font in this folder is licensed under the SIL Open Font License 1.1. The license texts are in
[`licenses/`](licenses/). The same files, by sha256, are baked into the sandbox by
`sandbox/setup.sh` from `google/fonts` at commit `47d54ca1ebb14fd864695f1d39dc734f39017c33`.

| File | Family | Copyright | License |
| --- | --- | --- | --- |
| `Inter-Variable.ttf`, `Inter-Italic-Variable.ttf` | Inter | The Inter Project Authors | [OFL-1.1](licenses/Inter-OFL.txt) |
| `IBMPlexMono-Regular.ttf`, `IBMPlexMono-Medium.ttf`, `IBMPlexMono-SemiBold.ttf`, `IBMPlexMono-Bold.ttf` | IBM Plex Mono | IBM Corp., Reserved Font Name "Plex" | [OFL-1.1](licenses/IBMPlexMono-OFL.txt) |
| `FiraCode-Variable.ttf` | Fira Code | The Fira Code Project Authors | [OFL-1.1](licenses/FiraCode-OFL.txt) |
| `Fraunces-Variable.ttf`, `Fraunces-Italic-Variable.ttf` | Fraunces | The Fraunces Project Authors | [OFL-1.1](licenses/Fraunces-OFL.txt) |

Licensed fonts are never committed. Put them in the Git-ignored `private-fonts/` folder and declare
them in your brand pack's `fonts.toml`; see [docs/customization.md](../docs/customization.md#brand).
