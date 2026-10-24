"""Run isolated offline eval cases; write a compact JSON scorecard, never prompts/secrets."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from xml.etree import ElementTree


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="storage/evals/offline_results.json")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as temp:
        xml = Path(temp) / "results.xml"
        run = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_copilot.py", "-m", "ai_eval", "-q", "--junitxml=" + str(xml)],
            cwd=root, capture_output=True, text=True,
        )
        cases = []
        if xml.exists():
            for case in ElementTree.parse(xml).iter("testcase"):
                outcome = "failed" if case.find("failure") is not None or case.find("error") is not None else "skipped" if case.find("skipped") is not None else "passed"
                cases.append({"case": case.attrib["name"], "outcome": outcome})
        report = {
            "mode": "offline_tfidf_and_templates", "live_provider_evaluated": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "total": len(cases), "passed": sum(c["outcome"] == "passed" for c in cases),
            "cases": cases,
            "limitation": "Behavioral assertions, not a semantic accuracy, factuality or prompt-injection robustness benchmark.",
        }
        output = Path(args.output)
        if not output.is_absolute():
            output = root / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Offline evaluation: {report['passed']}/{report['total']} passed. Report: {output}")
        if run.returncode:
            print("Evaluation failed. Run pytest -m ai_eval from backend for diagnostic details.")
        return run.returncode or (0 if cases else 1)


if __name__ == "__main__":
    raise SystemExit(main())
