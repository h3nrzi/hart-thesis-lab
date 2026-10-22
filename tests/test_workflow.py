"""آزمون بدون تماس شبکه و بدون ایجاد پرونده در مخزن اصلی."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class FlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel in ("README.md", "CONTRIBUTING.md", "INDEX.md", "docs/workflow.md",
                    "docs/statuses.md", "templates/case.md", "templates/original.md",
                    "templates/update.md", "templates/review.md", "templates/outcome.md",
                    "analyses/README.md"):
            dest = self.root/rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/rel, dest)
    def tearDown(self):
        self.tmp.cleanup()
    def run_script(self, name, *args):
        return subprocess.run([sys.executable, str(ROOT/"scripts"/name),
            *args, "--root", str(self.root)], text=True, capture_output=True)
    def create(self):
        return self.run_script("create_case.py", "--url",
            "https://www.tradingview.com/chart/XAUUSD/DEMO1234-Example/")
    def initial(self):
        case = self.root/"analyses"/"DEMO1234"
        text = (self.root/"templates"/"original.md").read_text(encoding="utf-8")
        (case/"original.md").write_text(text.replace("[شناسه]", "DEMO1234")
            .replace("[نشانی]", "https://www.tradingview.com/chart/XAUUSD/DEMO1234-Example/"),
            encoding="utf-8")
        return case
    def test_link_creates_only_case_and_index(self):
        self.assertEqual(self.create().returncode, 0)
        folder = self.root/"analyses"/"DEMO1234"
        self.assertEqual([x.name for x in folder.iterdir()], ["case.md"])
        self.assertIn("در انتظار متن اولیه", (folder/"case.md").read_text(encoding="utf-8"))
        self.assertIn("DEMO1234", (self.root/"INDEX.md").read_text(encoding="utf-8"))
        self.assertNotEqual(self.create().returncode, 0)
        self.assertEqual(self.run_script("validate_structure.py").returncode, 0)
    def test_outcome_requires_explicit_instructor_followup(self):
        self.assertEqual(self.create().returncode, 0)
        folder = self.initial()
        self.assertNotEqual(self.run_script("prepare_outcome.py", "--id", "DEMO1234",
                                           "--update", "update-20261103T160000Z.md").returncode, 0)
        update = folder/"update-20261103T160000Z.md"
        s = (self.root/"templates"/"update.md").read_text(encoding="utf-8")
        s = s.replace("[شناسه]", "DEMO1234").replace("[لینک مستقیم]",
            "https://www.tradingview.com/chart/XAUUSD/DEMO1234-Example/")
        update.write_text(s, encoding="utf-8")
        self.assertNotEqual(self.run_script("prepare_outcome.py", "--id", "DEMO1234",
                                           "--update", update.name).returncode, 0)
        s = s.replace("**بررسی صریح نتیجه توسط مدرس:** خیر",
                      "**بررسی صریح نتیجه توسط مدرس:** بله")
        s = s.replace("**شاهد بررسی نتیجه:** نامشخص",
                      "**شاهد بررسی نتیجه:** مدرس پایان سناریو را در آپدیت اعلام کرد.")
        update.write_text(s, encoding="utf-8")
        self.assertEqual(self.run_script("prepare_outcome.py", "--id", "DEMO1234",
                                        "--update", update.name).returncode, 0)
        self.assertTrue((folder/"outcome.md").exists())
        self.assertEqual(self.run_script("validate_structure.py").returncode, 0)
        case = folder/"case.md"
        case.write_text(case.read_text(encoding="utf-8").replace(
            "**وضعیت پرونده:** در انتظار متن اولیه", "**وضعیت پرونده:** بسته‌شده"), encoding="utf-8")
        self.assertNotEqual(self.run_script("validate_structure.py").returncode, 0)
        out = folder/"outcome.md"
        out.write_text(out.read_text(encoding="utf-8").replace(
            "**وضعیت ارزیابی:** پیش‌نویس", "**وضعیت ارزیابی:** تکمیل‌شده"), encoding="utf-8")
        self.assertEqual(self.run_script("validate_structure.py").returncode, 0)

if __name__ == "__main__":
    unittest.main()
