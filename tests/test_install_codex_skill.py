"""Exercise installation without touching the user's personal skills directory."""

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("installer", ROOT / "tools/install_codex_skill.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallationTests(unittest.TestCase):
    def test_link_is_readable_and_repeatable(self):
        with tempfile.TemporaryDirectory() as directory:
            target = installer.install(Path(directory) / "skills with spaces")
            self.assertTrue(target.is_symlink())
            self.assertEqual((target / "SKILL.md").read_bytes(),
                             (installer.SOURCE / "SKILL.md").read_bytes())
            self.assertEqual(installer.install(target.parent), target)

    def test_existing_content_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / installer.SOURCE.name
            target.mkdir()
            marker = target / "user-file"
            marker.write_text("keep me")
            with self.assertRaises(ValueError):
                installer.install(directory)
            self.assertEqual(marker.read_text(), "keep me")

    def test_dangling_link_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / installer.SOURCE.name
            target.symlink_to("missing-source")
            with self.assertRaises(ValueError):
                installer.install(directory)
            self.assertEqual(os.readlink(target), "missing-source")

    def test_source_cannot_contain_installation(self):
        with self.assertRaises(ValueError):
            installer.install(installer.SOURCE / "nested-skills")
