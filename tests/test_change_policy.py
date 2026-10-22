"""اجرای واقعی قواعد منع بازنویسی با مخزن Git موقت."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from check_change_policy import policy

class ChangePolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.git("init","-q")
        self.git("config","user.name","Test Agent")
        self.git("config","user.email","agent@example.invalid")
        self.path=self.root/"analyses"/"TEST1234"
        self.path.mkdir(parents=True)
        (self.path/"case.md").write_text("شناسنامه")
        (self.path/"original.md").write_text("اصل تحلیل")
        self.git("add",".")
        self.git("commit","-qm","start")
        self.base=self.git("rev-parse","HEAD").strip()
    def tearDown(self):self.temp.cleanup()
    def git(self,*args):
        return subprocess.run(["git",*args],cwd=self.root,
            capture_output=True,text=True,check=True).stdout
    def commit(self):
        self.git("add","-A");self.git("commit","-qm","change")
    def test_original_modified_rejected(self):
        (self.path/"original.md").write_text("دست‌کاری نسخه قدیمی")
        self.commit()
        self.assertTrue(any("original.md" in s for s in policy(self.base,cwd=self.root)))
    def test_update_added_allowed(self):
        (self.path/"update-20261022T080000Z.md").write_text("آپدیت تازه")
        self.commit()
        self.assertEqual(policy(self.base,cwd=self.root),[])
    def test_update_modified_rejected(self):
        old=self.path/"update-20261022T080000Z.md"
        old.write_text("نسخه اول");self.commit()
        updated_base=self.git("rev-parse","HEAD").strip()
        old.write_text("بازنویسی ممنوع");self.commit()
        self.assertTrue(policy(updated_base,cwd=self.root))
    def test_case_deleted_rejected(self):
        (self.path/"case.md").unlink()
        self.commit()
        self.assertTrue(any("case.md" in s for s in policy(self.base,cwd=self.root)))
