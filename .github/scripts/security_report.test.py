import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "security_report", Path(__file__).with_name("security_report.py"))
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


class SecurityReportTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name, "report.json")

    def save(self, data):
        self.path.write_text(json.dumps(data))

    def test_clean_and_vulnerable_bun(self):
        self.save({})
        self.assertEqual(report.bun_findings(self.path, 0), [])
        advisory = {"severity": "high", "url": "https://github.com/advisories/GHSA-test"}
        self.save({"example": [advisory, advisory]})
        findings = report.bun_findings(self.path, 1)
        text = report.write_report(findings, self.directory.name)
        self.assertIn("**1 package/advisory matches**", text)
        self.assertIn("not that the application is vulnerability-free", text)

    def test_scanner_errors_never_become_clean_results(self):
        for data, status in (({}, 1), ({"error": "rate limited"}, 1), ([], 0), ({}, 2)):
            with self.subTest(data=data, status=status):
                self.save(data)
                with self.assertRaises(ValueError):
                    report.bun_findings(self.path, status)
        self.path.write_text("<html>unavailable</html>")
        with self.assertRaises(ValueError):
            report.bun_findings(self.path, 1)

if __name__ == "__main__":
    unittest.main()
