"""Check generated runner/platform contracts without builds or publication."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class WorkflowGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory(prefix="friday-workflows-")
        cls.addClassCleanup(cls.fixture.cleanup)
        cls.workflows = Path(cls.fixture.name) / ".github/workflows"
        cls.workflows.mkdir(parents=True)
        (cls.workflows / "unrelated.yml").write_text("sentinel")
        subprocess.run([sys.executable, str(ROOT / "ci/generate-workflows.py")],
                       cwd=cls.fixture.name, check=True, stdout=subprocess.DEVNULL)
        cls.generated = {path.name: path.read_text() for path in cls.workflows.glob("gen_*.yml")}

    def test_generator_reproduces_checked_in_outputs(self):
        expected = {path.name: path.read_text() for path in (ROOT / ".github/workflows").glob("gen_*.yml")}
        self.assertEqual(set(self.generated), set(expected))
        for name, text in self.generated.items():
            self.assertEqual(text, expected[name], name)
        self.assertEqual((self.workflows / "unrelated.yml").read_text(), "sentinel")

    def test_native_build_runners_and_linux_uploaders(self):
        for name, text in self.generated.items():
            with self.subTest(workflow=name):
                build = re.search(r'  build:\n    runs-on: "([^"]+)"', text).group(1)
                expected = "macos-latest" if name.startswith("gen_macos") else "windows-2022" if name.startswith("gen_windows") else "boat"
                self.assertEqual(build, expected)
                if "  upload:\n" in text:
                    self.assertIn('  upload:\n    runs-on: "boat"\n    needs: build', text)
                    self.assertIn("    if: github.repository == 'wezterm/wezterm'", text)
                    self.assertIn("      contents: write", text)

    def test_distro_and_privileged_container_contracts(self):
        images = {"ubuntu20.04": "ubuntu:20.04", "ubuntu22.04": "ubuntu:22.04",
                  "ubuntu24.04": "ubuntu:24.04", "debian11": "debian:11", "debian12": "debian:12",
                  "centos9": "quay.io/centos/centos:stream9", "fedora39": "fedora:39",
                  "fedora40": "fedora:40", "fedora41": "fedora:41"}
        for target, image in images.items():
            for suffix in ("", "_continuous", "_tag"):
                name = f"gen_{target}{suffix}.yml"
                text = self.generated[name]
                if target == "ubuntu20.04":
                    self.assertIn(f'container:\n      image: "{image}"\n      options: --privileged', text, name)
                else:
                    self.assertIn(f'container: "{image}"', text, name)


if __name__ == "__main__":
    unittest.main()
