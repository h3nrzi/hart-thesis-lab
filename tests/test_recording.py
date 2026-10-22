"""چرخه نمونه غیرواقعی و idempotency در پوشه موقت."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
from create_case import create_case
from record_original import record as record_original
from record_event import record as record_event
from agent_status import inspect

class RecordingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        files=("README.md","CONTRIBUTING.md","INDEX.md","docs/workflow.md",
               "docs/statuses.md","templates/case.md","templates/original.md",
               "templates/update.md","templates/review.md","templates/outcome.md",
               "analyses/README.md")
        for rel in files:
            p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/rel,p)
        self.url="https://www.tradingview.com/chart/XAUUSD/DEMO1234-Example/"
        create_case(self.root,self.url)
        self.source=self.root/"text.txt"
        self.source.write_text("سناریوی فرضی تست؛ متن ارسالی کاربر",encoding="utf-8")
    def tearDown(self):self.tmp.cleanup()
    def test_original_is_immutable_and_idempotent(self):
        one,created=record_original(self.root,"DEMO1234",self.source)
        self.assertTrue(created)
        self.assertEqual(self.root.joinpath("analyses/DEMO1234/original.md"),one)
        self.assertEqual(inspect(self.root,"DEMO1234")["stage"],"TRACKING")
        two,created=record_original(self.root,"DEMO1234",self.source)
        self.assertEqual(one,two);self.assertFalse(created)
        self.source.write_text("محتوای متفاوت",encoding="utf-8")
        with self.assertRaises(FileExistsError):
            record_original(self.root,"DEMO1234",self.source)
    def test_updates_require_instructor_and_no_duplicate(self):
        record_original(self.root,"DEMO1234",self.source)
        one,created=record_event(self.root,"DEMO1234","update",self.source,self.url)
        self.assertTrue(created)
        two,created=record_event(self.root,"DEMO1234","update",self.source,self.url)
        self.assertEqual(one,two);self.assertFalse(created)
        self.assertEqual(inspect(self.root,"DEMO1234")["stage"],"TRACKING")
        self.source.write_text("مدرس پایان سناریوی تست را اعلام کرد",encoding="utf-8")
        # زمان نام رویداد نباید به زمان واقعی انتشار وانمود کند.
        with self.assertRaises(ValueError):
            record_event(self.root,"DEMO1234","update",self.source,self.url,declares_outcome=True)
        # برای آزمودن حالت مجاز، رویداد قدیمی ساختگی را حذف می‌کنیم تا محدودیت نام در یک ثانیه مطرح نشود.
        one.unlink()
        record_event(self.root,"DEMO1234","update",self.source,self.url,declares_outcome=True,
                     witness="مدرس در متن ارسالی پایان را صریح اعلام کرد")
        self.assertEqual(inspect(self.root,"DEMO1234")["stage"],"READY_FOR_OUTCOME")
    def test_review_cannot_assert_instructor_outcome(self):
        record_original(self.root,"DEMO1234",self.source)
        with self.assertRaises(ValueError):
            record_event(self.root,"DEMO1234","review",self.source,declares_outcome=True,
                         witness="این متن از AI است نه مدرس")
