"""تست واقعی اینکه کشِ ignored مانع نیست ولی فایل کاربر مانع است."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from check_worktree import inspect


class WorktreeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Temporary")
        self.git("config", "user.email", "temporary@example.invalid")
        shutil.copyfile(ROOT / ".gitignore", self.root / ".gitignore")
        (self.root / "README.md").write_text("متن پروژه", encoding="utf-8")
        self.git("add", ".gitignore", "README.md")
        self.git("commit", "-qm", "baseline")

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True,
                              text=True, check=True).stdout

    def test_python_cache_does_not_block(self):
        cache = self.root / "scripts" / "__pycache__"
        cache.mkdir(parents=True)
        (cache / "agent_status.cpython-312.pyc").write_bytes(b"temporary cache")
        self.assertTrue(inspect(self.root)["clean"])
        self.assertEqual(inspect(self.root)["next_action"], "proceed")
        # فایل موجود است و نباید برای تمیزی Git حذف شود.
        self.assertTrue((cache / "agent_status.cpython-312.pyc").exists())

    def test_real_untracked_file_blocks(self):
        case = self.root / "analyses" / "DEMO1234"
        case.mkdir(parents=True)
        (case / "case.md").write_text("شناسنامه واقعی", encoding="utf-8")
        result = inspect(self.root)
        self.assertFalse(result["clean"])
        self.assertIn("analyses/DEMO1234/case.md", str(result["changes"]))

    def test_tracked_changes_still_block(self):
        (self.root / "README.md").write_text("تغییر ثبت‌نشده", encoding="utf-8")
        state = inspect(self.root)
        self.assertFalse(state["clean"])
        self.assertEqual(state["next_action"], "stop_and_report")

    def test_unignored_script_does_not_get_exempted(self):
        (self.root / "scripts").mkdir()
        (self.root / "scripts" / "local_work.py").write_text("print(1)", encoding="utf-8")
        self.assertFalse(inspect(self.root)["clean"])


if __name__ == "__main__":
    unittest.main()
