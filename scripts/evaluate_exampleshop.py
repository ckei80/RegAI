import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from regai.assessment import assess_regulatory_requirement
from regai.embeddings import LocalEmbeddingProvider
from regai.evidence_models import EvidenceChunk
from regai.evidence_processing import create_evidence_chunks
from regai.evidence_retrieval import EvidenceRetriever
from regai.requirement_assessment import RequirementAssessment
from regai.regulatory_models import RegulatoryRequirement


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_DIR = (
    PROJECT_ROOT / "data" / "sample" / "exampleshop" / "evaluation"
)
CASES_FILE = EVALUATION_DIR / "cases.json"
REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_FILE = REPORT_DIR / "exampleshop-evaluation.md"


def load_cases() -> list[dict]:
    return json.loads(CASES_FILE.read_text(encoding="utf-8"))


def create_requirement() -> RegulatoryRequirement:
    return RegulatoryRequirement(
        requirement_id="ART13-B",
        source="GDPR",
        section="Article 13",
        effective_date="2018-05-25",
        original_text=(
            "The purposes of the processing for which the personal data "
            "are intended."
        ),
        analysis={
            "topic": "Purpose of processing",
            "interpretation": (
                "Explain the purposes for which personal data is processed."
            ),
        },
    )


def load_chunks(filename: str) -> list[EvidenceChunk]:
    html = (EVALUATION_DIR / filename).read_text(encoding="utf-8")

    return create_evidence_chunks(
        html=html,
        url=f"https://exampleshop.test/evaluation/{filename}",
        retrieval_date="2026-10-08",
    )


def evaluate_case(
    case: dict,
    requirement: RegulatoryRequirement,
    embedding_provider: LocalEmbeddingProvider,
) -> dict:
    chunks = load_chunks(case["filename"])

    evidence_retriever = EvidenceRetriever(
        embedding_provider=embedding_provider,
        chunks=chunks,
    )

    result = assess_regulatory_requirement(
        requirement=requirement,
        evidence_retriever=evidence_retriever,
        top_k=5,
    )

    expected = RequirementAssessment(case["expected_assessment"])
    actual = result.assessment if result is not None else None

    return {
        "filename": case["filename"],
        "expected": expected.value,
        "actual": actual.value if actual is not None else "no_result",
        "passed": actual == expected,
        "explanation": (
            result.explanation if result is not None else "No result returned."
        ),
    }


def create_report(results: list[dict]) -> str:
    total = len(results)
    passed = sum(result["passed"] for result in results)
    failed = total - passed
    accuracy = (passed / total * 100) if total else 0.0

    actual_counts = Counter(result["actual"] for result in results)

    lines = [
        "# ExampleShop Evaluation Report",
        "",
        f"- Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"- Total cases: {total}",
        f"- Passed: {passed}",
        f"- Failed: {failed}",
        f"- Classification accuracy: {accuracy:.1f}%",
        "",
        "## Results",
        "",
        "| Case | Expected | Actual | Result |",
        "|---|---|---|---|",
    ]

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        lines.append(
            f"| {result['filename']} | {result['expected']} "
            f"| {result['actual']} | {status} |"
        )

    lines.extend(
        [
            "",
            "## Actual classification counts",
            "",
            "| Classification | Count |",
            "|---|---:|",
        ]
    )

    for classification, count in sorted(actual_counts.items()):
        lines.append(f"| {classification} | {count} |")

    lines.extend(["", "## Model explanations", ""])

    for result in results:
        lines.extend(
            [
                f"### {result['filename']}",
                "",
                f"- **Expected:** `{result['expected']}`",
                f"- **Actual:** `{result['actual']}`",
                f"- **Result:** {'PASS' if result['passed'] else 'FAIL'}",
                "",
                result["explanation"],
                "",
            ]
        )

    lines.extend(
        [
            "## Interpretation",
            "",
            "This report measures agreement with the expected classifications "
            "defined in the ExampleShop evaluation dataset. It does not establish "
            "legal compliance or measure overall regulatory accuracy.",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    cases = load_cases()
    requirement = create_requirement()
    embedding_provider = LocalEmbeddingProvider()

    results = []

    for index, case in enumerate(cases, start=1):
        print(f"[{index}/{len(cases)}] Evaluating {case['filename']}...")
        results.append(
            evaluate_case(
                case=case,
                requirement=requirement,
                embedding_provider=embedding_provider,
            )
        )

    report = create_report(results)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(report, encoding="utf-8")

    print()
    print(f"Evaluation accuracy: {sum(r['passed'] for r in results)}/{len(results)}")
    print(f"Report saved to: {REPORT_FILE}")

    return 0 if all(result["passed"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())