# Workflow generation and runners

`generate-workflows.py` owns all `.github/workflows/gen_*.yml` files. Change the generator, then regenerate from the repository root:

```sh
python3 ci/generate-workflows.py
python3 ci/test-generate-workflows.py
```

The generator's `LINUX_RUNNER` selects Boat for generic Linux build hosts and upload jobs. Distro identity comes from the existing container image and target name, not the host label. Ubuntu 20.04/22.04/24.04, Debian, CentOS and Fedora container versions remain unchanged. The AppImage Ubuntu 20.04 container retains `--privileged` for its FUSE contract. Do not reinterpret those containers as a generic host build.

macOS builds remain on `macos-latest`. Windows builds remain on `windows-2022`. Upload jobs still depend on their native/distro build and run outside its container. The uploader job object owns its runner; the renderer must not hardcode a second runner choice. Existing artifact names, features, paths, triggers, caches, permissions and upstream-only publishing guards remain authoritative.

Handwritten Linux workflows, including format, docs, Nix and small maintenance jobs, also use Boat. Changing a runner label does not enable upstream publishing, deployment, fork CI or external contributor access. Owner-only public execution policy is configured separately. No workflow dispatch, provider/account billing repair or credentials change is part of this source migration.

Generator tests use disposable directories and do not compile, package, publish or call providers. They verify checked-in regeneration, native runner retention, distro/privilege contracts and upstream upload guards. Real distro, FUSE, Nix, native build and publishing qualification remain separate acceptance gates. Do not infer runtime success or a speedup from generation tests.
