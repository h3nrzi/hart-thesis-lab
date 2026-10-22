"""تست تشخیص وضعیت بدون حافظه سشن، در فضای موقت."""
import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "scripts"))
from agent_status import inspect

class AgentStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        needed=("README.md","CONTRIBUTING.md","INDEX.md","docs/workflow.md","docs/statuses.md",
                "templates/case.md","templates/original.md","templates/update.md",
                "templates/review.md","templates/outcome.md","analyses/README.md")
        for rel in needed:
            p=self.root/rel; p.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(BASE/rel,p)
        self.case=self.root/"analyses"/"TEST1234";self.case.mkdir()
    def tearDown(self): self.tmp.cleanup()
    def put(self,name,content): (self.case/name).write_text(content,encoding="utf-8")
    def create_case(self):
        self.put("case.md", "**شناسه ایده:** TEST1234\n**نشانی منبع:** https://www.tradingview.com/chart/XAUUSD/TEST1234/\n- **وضعیت پرونده:** در انتظار متن اولیه\n")
    def status(self):return inspect(self.root,"TEST1234")
    def test_no_case(self):
        self.case.rmdir()
        self.assertEqual(self.status()["stage"],"NOT_FOUND")
    def test_await_original(self):
        self.create_case()
        self.assertEqual(self.status()["stage"],"AWAITING_ORIGINAL")
        self.assertIn("متن",self.status()["next_question"])
    def test_original_tracking_and_conflict(self):
        self.create_case(); self.put("original.md","تحلیل اولیه دستی")
        self.assertEqual(self.status()["stage"],"CONFLICT")
        p=self.case/"case.md"
        p.write_text(p.read_text().replace("در انتظار متن اولیه","در حال پیگیری"))
        self.assertEqual(self.status()["stage"],"TRACKING")
    def test_outcome_sequence(self):
        self.create_case(); p=self.case/"case.md"
        p.write_text(p.read_text().replace("در انتظار متن اولیه","در حال پیگیری"))
        self.put("original.md","**شناسه ایده:** TEST1234\n")
        self.put("update-20261101T110000Z.md","**شناسه ایده:** TEST1234\n- **نشانی منبع:** https://www.tradingview.com/chart/XAUUSD/TEST1234/\n- **بررسی صریح نتیجه توسط مدرس:** خیر\n- **شاهد بررسی نتیجه:** نامشخص\n")
        self.assertEqual(self.status()["stage"],"TRACKING")
        up=self.case/"update-20261101T110000Z.md"
        up.write_text(up.read_text().replace("**بررسی صریح نتیجه توسط مدرس:** خیر","**بررسی صریح نتیجه توسط مدرس:** بله").replace("**شاهد بررسی نتیجه:** نامشخص","**شاهد بررسی نتیجه:** مدرس گفته تحلیل خاتمه یافته."))
        self.assertEqual(self.status()["stage"],"READY_FOR_OUTCOME")
        self.put("outcome.md","- **آپدیت مستند بررسی نتیجه توسط مدرس:** update-20261101T110000Z.md\n- **وضعیت ارزیابی:** پیش‌نویس\n")
        self.assertEqual(self.status()["stage"],"CONFLICT")
        p.write_text(p.read_text().replace("در حال پیگیری","در حال تدوین نتیجه"))
        self.assertEqual(self.status()["stage"],"DRAFT_OUTCOME")
        out=self.case/"outcome.md"
        out.write_text(out.read_text().replace("پیش‌نویس","تکمیل‌شده"))
        p.write_text(p.read_text().replace("در حال تدوین نتیجه","بسته‌شده"))
        self.assertEqual(self.status()["stage"],"CLOSED")
