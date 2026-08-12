from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class ProjectsDesignAuthorityTests(unittest.TestCase):
    def test_kakeibo_routes_design_to_codex_with_mandatory_fable_review(self):
        projects = (ROOT / "PROJECTS.md").read_text(encoding="utf-8")
        rows = [
            line
            for line in projects.splitlines()
            if line.startswith("| 家計簿LIFF FastAPI化 ")
        ]
        self.assertEqual(1, len(rows))

        columns = [column.strip() for column in rows[0].split("|")]
        self.assertEqual("Codex Desktop + WSL Fable 5 audit", columns[4])
        self.assertEqual("Codex", columns[5])
        self.assertEqual("`https://github.com/sjinnouchi-ux/kakeibo-liff`", columns[6])
        self.assertIn("固定WSL runner", columns[8])
        self.assertIn("必須read-only監査", columns[8])
        self.assertNotEqual("FABLE 5 / Claude", columns[4])


if __name__ == "__main__":
    unittest.main()
