#!/usr/bin/env python3
"""Build a source and rights inventory for questionnaire/interview assets.

The report is intentionally conservative. It records repository claims and official
rights-review leads; it is not legal advice and never upgrades a source permission.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "coverage/questionnaire-source-rights-inventory-latest.json"
DEFAULT_MARKDOWN = ROOT / "docs/QUESTIONNAIRE_INTERVIEW_SOURCE_RIGHTS_INVENTORY.md"

OPEN_OR_DOCUMENTED = {
    "allowed",
    "CC0-1.0",
    "FHIR_specification_license",
}
LIMITED = {
    "restricted",
    "metadata_and_summary_only",
    "metadata_and_summary_only_CC_BY_NC_SA_3_IGO",
    "metadata_only",
    "official_link_only",
    "licensed_lookup_metadata_only",
    "local_research_environment",
    "metadata_only_review_required",
    "CC_BY_NC_ND_metadata_and_summary_only",
    "KOGL_type_4_metadata_and_summary_only_no_redistribution",
    "source_provided_for_research",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def walk(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def source_index() -> tuple[dict[str, dict[str, Any]], list[str], int]:
    index: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    artifact_entry_count = 0
    for path in sorted((ROOT / "sources/manifests").glob("*.json")):
        data = load_json(path)
        for artifact in data.get("artifacts", []):
            artifact_entry_count += 1
            source_id = artifact.get("id")
            if not source_id:
                continue
            if source_id in index:
                duplicates.append(source_id)
            index[source_id] = {**artifact, "manifest_path": relative(path)}
    return index, sorted(set(duplicates)), artifact_entry_count


def rights_bucket(status: str) -> str:
    if status in OPEN_OR_DOCUMENTED:
        return "documented_open_or_allowed"
    if status in LIMITED:
        return "restricted_or_limited"
    if status == "prohibited":
        return "prohibited"
    return "unknown_or_unclassified"


def rights_summary(statuses: Iterable[str]) -> dict[str, Any]:
    counts = Counter(statuses)
    buckets = Counter()
    for status, count in counts.items():
        buckets[rights_bucket(status)] += count
    if buckets["prohibited"]:
        gate = "blocked"
    elif buckets["unknown_or_unclassified"] or buckets["restricted_or_limited"]:
        gate = "rights_review_required"
    else:
        gate = "documented_sources_only"
    return {
        "source_license_status_counts": dict(sorted(counts.items())),
        "normalized_rights_counts": dict(sorted(buckets.items())),
        "external_use_gate": gate,
    }


def package_assets() -> list[dict[str, Any]]:
    catalog = load_json(ROOT / "knowledge/catalog/primary-care-rfe.json")
    package_by_id: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in sorted((ROOT / "packages/generated").glob("*.json")):
        package = load_json(path)
        package_by_id[package["package_id"]] = (path, package)

    assets: list[dict[str, Any]] = []
    for entry in catalog["entries"]:
        package_id = entry.get("package_id")
        if not package_id or not package_id.startswith("package.primary-care-"):
            continue
        path, package = package_by_id[package_id]
        nodes = package["knowledge_graph"]["nodes"]
        source_artifacts = [
            obj for obj in walk(package)
            if "license_status" in obj and ("id" in obj or "canonical_url" in obj)
        ]
        statuses = [obj.get("license_status", "unknown") for obj in source_artifacts]
        assets.append({
            "id": entry["id"],
            "title": entry.get("display_ko") or entry.get("display"),
            "asset_class": "dynamic_clinical_interview",
            "implementation_status": entry.get("implementation_status"),
            "repository_paths": [
                "knowledge/catalog/primary-care-rfe.json",
                relative(path),
            ],
            "package_id": package_id,
            "package_version": package.get("package_version"),
            "question_count": sum(node.get("type") == "QuestionTemplate" for node in nodes),
            "source_defined_fixed_items": False,
            "content_origin": "project_authored_dynamic_interview_knowledge",
            "source_artifact_count": len(source_artifacts),
            "rights": {
                **rights_summary(statuses),
                "internal_test": "allowed_under_draft_limited_use_policy",
                "external_distribution": "source_and_derivation_rights_review_required",
                "commercial_use": "source_and_derivation_rights_review_required",
            },
            "fidelity": "not_a_source_defined_fixed_questionnaire",
            "clinical_use": "unreviewed_draft_limited_use",
        })
    return assets


def source_refs(value: Any) -> list[str]:
    refs: set[str] = set()
    for obj in walk(value):
        candidate = obj.get("source_refs")
        if isinstance(candidate, list):
            refs.update(ref for ref in candidate if isinstance(ref, str) and ref.startswith("source."))
    return sorted(refs)


def resolve_sources(refs: list[str], index: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    resolved = []
    missing = []
    for ref in refs:
        if ref in index:
            artifact = index[ref]
            resolved.append({
                "id": ref,
                "title": artifact.get("title"),
                "publisher": artifact.get("publisher"),
                "version": artifact.get("version"),
                "license_status": artifact.get("license_status", "unknown"),
                "complete": artifact.get("complete", False),
                "manifest_path": artifact["manifest_path"],
            })
        else:
            missing.append(ref)
    return resolved, missing


def count_question_like(value: Any) -> int:
    return sum(
        1 for obj in walk(value)
        if isinstance(obj.get("id"), str)
        and (
            isinstance(obj.get("text_ko"), str)
            or isinstance(obj.get("text"), dict)
        )
    )


def referenced_external_instruments(value: Any) -> list[dict[str, Any]]:
    """Return named instruments that are referenced but not administered here."""
    instruments: dict[str, dict[str, Any]] = {}
    for obj in walk(value):
        recognized = obj.get("recognized_instruments")
        if not isinstance(recognized, list):
            continue
        for item in recognized:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                continue
            instrument_id = item["id"]
            instruments[instrument_id] = {
                "id": instrument_id,
                "recognition_level": item.get("level"),
                "items_embedded": False,
                "runtime_role": "name_version_score_and_safety_result_capture_only",
                "rights_status": "instrument_specific_review_required",
            }
    return [instruments[key] for key in sorted(instruments)]


def hira_assets(index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    path = ROOT / "knowledge/assessments/hira-adequacy-assessment-interviews-2026.json"
    data = load_json(path)
    catalog = {entry["program_id"]: entry for entry in data["entry_catalog"]}
    assets = []
    for program in data["programs"]:
        entry = catalog[program["id"]]
        refs = source_refs(program)
        resolved, missing = resolve_sources(refs, index)
        statuses = [item["license_status"] for item in resolved]
        fixed = entry["entry_type"] in {"fixed_questionnaire", "fixed_standardized_instrument"}
        exact = entry["source_fidelity"] == "official_source_questionnaire_verified"
        internal_gate = (
            "repository_research_source_only_rights_confirmation_pending"
            if exact else "allowed_for_project_authored_research_test_or_result_capture"
        )
        assets.append({
            "id": program["id"],
            "title": entry["display_ko"],
            "asset_class": entry["entry_type"],
            "implementation_status": entry["runtime_readiness"],
            "repository_paths": [relative(path)],
            "question_count": count_question_like(program),
            "source_defined_fixed_items": exact,
            "content_origin": (
                "official_source_questionnaire_transcribed"
                if exact else "project_authored_from_assessment_metadata_or_result_capture"
            ),
            "source_fidelity": entry["source_fidelity"],
            "source_notice_ko": entry["source_notice_ko"],
            "related_asset_id": (
                "kr-patient-experience-evaluation-5th-2025"
                if program["id"] == "hira.inpatient_patient_experience.5th-2025"
                else None
            ),
            "source_refs": refs,
            "resolved_sources": resolved,
            "missing_source_refs": missing,
            "referenced_external_instruments": referenced_external_instruments(program),
            "rights": {
                **rights_summary(statuses),
                "internal_test": internal_gate,
                "external_distribution": "blocked_pending_explicit_rights_review",
                "commercial_use": "blocked_pending_explicit_rights_review",
            },
            "clinical_use": "unreviewed_draft_limited_use",
        })
    return assets


def screening_assets(index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    path = ROOT / "knowledge/preventive/kr-national-health-screening-2026.json"
    data = load_json(path)
    assets = []
    for group in data["question_groups"]:
        refs = source_refs(group) or data.get("source_refs", [])
        resolved, missing = resolve_sources(refs, index)
        statuses = [item["license_status"] for item in resolved]
        assets.append({
            "id": group["id"],
            "title": group["title"]["ko"],
            "asset_class": "adaptive_preventive_question_group",
            "implementation_status": "research_test_ready",
            "repository_paths": [relative(path)],
            "question_count": len(group.get("questions", [])),
            "source_defined_fixed_items": False,
            "content_origin": "project_authored_questions_informed_by_official_program_metadata",
            "source_fidelity": "not_the_official_NHIS_questionnaire",
            "source_refs": refs,
            "resolved_sources": resolved,
            "missing_source_refs": missing,
            "rights": {
                **rights_summary(statuses),
                "internal_test": "allowed_under_draft_limited_use_policy",
                "official_form_submission": "blocked_pending_official_form_fidelity_verification",
                "external_distribution": "rights_and_attribution_review_required",
                "commercial_use": "rights_and_attribution_review_required",
            },
            "clinical_use": "unreviewed_draft_limited_use",
        })
    return assets


def fhir_questionnaire_assets(index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    assets = []
    for path in sorted((ROOT / "fhir/r4/questionnaires").glob("*.json")):
        data = load_json(path)
        refs = [identifier["value"] for identifier in data.get("identifier", [])
                if identifier.get("system") == "urn:clinical-interview:source-ref"]
        if not refs:
            refs = ["source.hira.patient-experience-5th.2025"] if "patient-experience" in path.name else []
        resolved, missing = resolve_sources(refs, index)
        statuses = [item["license_status"] for item in resolved]
        item_count = sum(
            1 for obj in walk(data.get("item", []))
            if obj.get("type") not in {"group", "display", None}
        )
        assets.append({
            "id": data["id"],
            "canonical": data.get("url"),
            "version": data.get("version"),
            "title": data.get("title"),
            "asset_class": "fhir_fixed_questionnaire",
            "implementation_status": "research_test_ready",
            "repository_paths": [relative(path)],
            "question_count": item_count,
            "source_defined_fixed_items": True,
            "content_origin": "official_source_questionnaire_transcribed",
            "source_fidelity": "official_source_questionnaire_verified_by_repository",
            "source_refs": refs,
            "resolved_sources": resolved,
            "missing_source_refs": missing,
            "rights": {
                **rights_summary(statuses),
                "internal_test": "repository_research_source_only_rights_confirmation_pending",
                "external_distribution": "blocked_pending_explicit_rights_review",
                "commercial_use": "blocked_pending_explicit_rights_review",
            },
            "clinical_use": "unreviewed_draft_limited_use",
        })
    return assets


def shared_assessment_assets(index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    path = ROOT / "knowledge/shared/hira-pain-assessment.json"
    data = load_json(path)
    refs = source_refs(data)
    resolved, missing = resolve_sources(refs, index)
    statuses = [item["license_status"] for item in resolved]
    return [{
        "id": data["id"],
        "title": "재사용 가능한 통증 NRS 문진",
        "asset_class": "shared_assessment_component",
        "implementation_status": "research_test_ready",
        "repository_paths": [relative(path)],
        "question_count": len(data.get("questions", [])),
        "source_defined_fixed_items": False,
        "content_origin": "project_authored_shared_assessment_component",
        "source_refs": refs,
        "resolved_sources": resolved,
        "missing_source_refs": missing,
        "rights": {
            **rights_summary(statuses),
            "internal_test": "allowed_under_draft_limited_use_policy",
            "external_distribution": "source_and_derivation_rights_review_required",
            "commercial_use": "source_and_derivation_rights_review_required",
        },
        "clinical_use": "unreviewed_draft_limited_use",
    }]


def validate_inventory(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ids = [asset["id"] for asset in report["assets"]]
    if len(ids) != len(set(ids)):
        duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
        errors.append(f"duplicate asset ids: {duplicates}")
    for asset in report["assets"]:
        for path in asset["repository_paths"]:
            if not (ROOT / path).exists():
                errors.append(f"{asset['id']}: missing repository path {path}")
        if asset.get("missing_source_refs"):
            errors.append(f"{asset['id']}: unresolved source refs {asset['missing_source_refs']}")
        if asset["source_defined_fixed_items"]:
            if asset["rights"].get("external_distribution") != "blocked_pending_explicit_rights_review":
                errors.append(f"{asset['id']}: fixed source items must fail closed for external distribution")
    for candidate in report["acquisition_candidates"]:
        if candidate.get("content_in_repository"):
            errors.append(f"{candidate['id']}: candidate content must not be embedded before rights review")
        if candidate.get("implementation_status") == "metadata_only_not_implemented" and candidate.get("runtime_use"):
            errors.append(f"{candidate['id']}: metadata-only candidate cannot be runtime-enabled")
        if candidate.get("acquisition_priority"):
            if not candidate.get("official_sources"):
                errors.append(f"{candidate['id']}: prioritized domestic candidate requires official sources")
            for source in candidate.get("official_sources", []):
                if not source.get("url", "").startswith("https://"):
                    errors.append(f"{candidate['id']}: official source must use HTTPS")
            boundary = candidate.get("runtime_adoption_boundary", {})
            if not boundary.get("allowed_now") or not boundary.get("blocked_now"):
                errors.append(f"{candidate['id']}: prioritized domestic candidate requires an adoption boundary")

    domestic = report.get("domestic_acquisition_order", [])
    priorities = [candidate.get("acquisition_priority") for candidate in domestic]
    if priorities != list(range(1, len(priorities) + 1)):
        errors.append(f"domestic acquisition priorities must be contiguous from 1: {priorities}")
    return errors


def build_report(as_of: str) -> dict[str, Any]:
    index, duplicate_source_ids, source_artifact_entry_count = source_index()
    candidates = load_json(ROOT / "sources/inventory/questionnaire-instrument-candidates.json")
    domestic_candidates = sorted(
        (candidate for candidate in candidates["candidates"] if candidate.get("acquisition_priority")),
        key=lambda candidate: candidate["acquisition_priority"],
    )
    assets = (
        package_assets()
        + hira_assets(index)
        + screening_assets(index)
        + fhir_questionnaire_assets(index)
        + shared_assessment_assets(index)
    )
    class_counts = Counter(asset["asset_class"] for asset in assets)
    gate_counts = Counter(asset["rights"]["external_use_gate"] for asset in assets)
    report = {
        "id": "coverage.questionnaire-source-rights-inventory",
        "version": "0.2.0",
        "as_of": as_of,
        "status": "draft",
        "review_status": "unreviewed",
        "scope": {
            "included": [
                "compiled dynamic clinical interview packages",
                "HIRA assessment interview programs",
                "Korean national health-screening adaptive question groups",
                "FHIR fixed Questionnaires",
                "shared reusable assessment components",
                "external acquisition candidates"
            ],
            "excluded": [
                "patient responses",
                "conversation transcripts",
                "untracked local source files",
                "generated GPT export duplicates",
                "health-screening package recommendation catalog products"
            ]
        },
        "interpretation": {
            "not_legal_advice": True,
            "metadata_access_is_not_item_use_permission": True,
            "internal_test_does_not_waive_instrument_rights": True,
            "external_or_commercial_use_requires_explicit_review": True,
            "fixed_questionnaires_are_not_auto_mapped_or_rewritten": True
        },
        "summary": {
            "asset_count": len(assets),
            "asset_class_counts": dict(sorted(class_counts.items())),
            "external_use_gate_counts": dict(sorted(gate_counts.items())),
            "source_manifest_artifact_entry_count": source_artifact_entry_count,
            "unique_source_id_count": len(index),
            "duplicate_source_ids": duplicate_source_ids,
            "candidate_family_count": len(candidates["candidates"]),
        },
        "assets": assets,
        "acquisition_candidates": candidates["candidates"],
        "domestic_acquisition_order": domestic_candidates,
        "next_actions": [
            "Perform explicit rights review for the HIRA fixed patient-experience questionnaire before external distribution.",
            "Obtain and verify the official NHIS questionnaire before claiming official-form fidelity or prepopulation compatibility.",
            "Ask HealthMeasures whether the intended company-internal digital PROMIS sandbox requires HEAP and translation permission.",
            "In order, compare CHS concepts, then KHP concepts, then KLoSA concepts against existing Facts without copying source-defined items.",
            "For every domestic source, verify artifact-level rights and any embedded third-party scale rights before electronic administration.",
            "Resolve unknown and restricted source statuses package-by-package before commercial deployment.",
            "Add instrument owner, version, scoring, translation and electronic-administration rights to every future fixed questionnaire."
        ],
        "provenance": {
            "generated_by": "tools/inventory/build_questionnaire_source_rights_inventory.py",
            "contains_patient_responses": False,
            "contains_source_defined_candidate_item_text": False,
        }
    }
    report["validation_errors"] = validate_inventory(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# 설문·문진 자원 출처 및 권리 Inventory",
        "",
        f"기준일: {report['as_of']}",
        "상태: `draft / unreviewed`",
        "",
        "> 이 문서는 저장소의 권리·출처 상태를 보수적으로 점검한 결과이며 법률 의견이 아니다. 내부 테스트는 저작권·전자 시행·번역 허가를 자동으로 면제하지 않는다.",
        "",
        "## 요약",
        "",
        f"- 현재 자원: **{summary['asset_count']}개**",
        f"- 외부 획득 후보군: **{summary['candidate_family_count']}개**",
        f"- source manifest artifact entry: **{summary['source_manifest_artifact_entry_count']}개**",
        f"- 고유 source ID: **{summary['unique_source_id_count']}개**",
        f"- 검증 오류: **{len(report['validation_errors'])}개**",
        "",
        "### 자원 유형별 수",
        "",
        "| 자원 유형 | 수 |",
        "|---|---:|",
    ]
    for kind, count in summary["asset_class_counts"].items():
        lines.append(f"| `{kind}` | {count} |")
    lines += [
        "",
        "## 해석 원칙",
        "",
        "- 동적 문진은 프로젝트가 작성한 draft 질문이며 source-defined fixed questionnaire가 아니다.",
        "- HIRA 평가 프로그램 중 공식 원문이 확인되지 않은 항목은 공식 평가도구가 아니라 연구용 문진 또는 기존 결과 입력 구조다.",
        "- 국가건강검진 질문군은 공식 NHIS 설문 원본이 아니라 공식 제도 자료를 참고한 adaptive draft다.",
        "- 공식 원문 기반 환자경험 Questionnaire는 내부 연구 source 상태만 기록되어 있어 외부 배포를 차단한다.",
        "- PROMIS 문항은 현재 저장소에 탑재하지 않았다. 회사 내부 디지털 테스트도 HEAP 또는 별도 허가 필요 여부를 먼저 확인한다.",
        "",
        "## 문항을 탑재하지 않은 외부 도구 참조",
        "",
        "HIRA 프로그램에 이름이 등장하더라도 해당 척도의 문항을 시행한다는 뜻은 아니다. 현재는 도구명·버전·총점과 안전 관련 결과를 입력받는 구조이며, 실제 문항 탑재에는 도구별 권리 검토가 필요하다.",
        "",
        "| 프로그램 | 참조 도구 | 현재 역할 | 권리 상태 |",
        "|---|---|---|---|",
    ]
    for asset in report["assets"]:
        for instrument in asset.get("referenced_external_instruments", []):
            lines.append(
                f"| `{asset['id']}` | `{instrument['id']}` | "
                f"`{instrument['runtime_role']}` | `{instrument['rights_status']}` |"
            )
    lines += [
        "",
        "## 현재 자원",
        "",
        "| ID | 유형 | 문항 | 원문 고정 | 내부 시험 | 외부 사용 gate |",
        "|---|---|---:|:---:|---|---|",
    ]
    for asset in report["assets"]:
        lines.append(
            f"| `{asset['id']}` | `{asset['asset_class']}` | {asset['question_count']} | "
            f"{'예' if asset['source_defined_fixed_items'] else '아니오'} | "
            f"`{asset['rights'].get('internal_test', 'not_recorded')}` | "
            f"`{asset['rights']['external_use_gate']}` |"
        )
    lines += [
        "",
        "## 외부 획득 후보",
        "",
        "| 후보 | 현재 상태 | 저장소 문항 | 다음 단계 |",
        "|---|---|:---:|---|",
    ]
    for candidate in report["acquisition_candidates"]:
        lines.append(
            f"| `{candidate['family']}` | `{candidate['implementation_status']}` | "
            f"{'예' if candidate['content_in_repository'] else '아니오'} | {candidate['next_action']} |"
        )
    lines += [
        "",
        "## 국내 자원 도입 순서",
        "",
        "공개 페이지 접근은 문항 재사용 허가가 아니다. 아래 순서는 concept-level gap 분석 순서이며, 원문 문항·보기·채점 규칙은 권리 확인 전 Runtime에 넣지 않는다.",
        "",
        "| 순서 | 자원 | 최신 확인본 | 현재 허용 | 현재 차단 |",
        "|---:|---|---|---|---|",
    ]
    for candidate in report["domestic_acquisition_order"]:
        release = candidate.get("latest_verified_release", {})
        release_text = release.get("survey_year") or release.get("questionnaire_appendix") or "metadata"
        allowed = ", ".join(candidate["runtime_adoption_boundary"]["allowed_now"])
        blocked = ", ".join(candidate["runtime_adoption_boundary"]["blocked_now"])
        lines.append(
            f"| {candidate['acquisition_priority']} | `{candidate['family']}` | `{release_text}` | "
            f"{allowed} | {blocked} |"
        )
    lines += [
        "",
        "## 우선 조치",
        "",
    ]
    for index, action in enumerate(report["next_actions"], 1):
        lines.append(f"{index}. {action}")
    lines += [
        "",
        "## 재생성 및 검증",
        "",
        "```bash",
        "python3 tools/inventory/build_questionnaire_source_rights_inventory.py",
        "python3 tools/inventory/build_questionnaire_source_rights_inventory.py --check",
        "python3 -m unittest tests.test_questionnaire_source_rights_inventory",
        "```",
        "",
        "기계 판독 원본: `coverage/questionnaire-source-rights-inventory-latest.json`",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--as-of")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.as_of:
        as_of = args.as_of
    elif args.check and args.output.exists():
        as_of = load_json(args.output).get("as_of", date.today().isoformat())
    else:
        as_of = date.today().isoformat()
    report = build_report(as_of)
    rendered_json = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    rendered_markdown = markdown(report)

    if args.check:
        stale = []
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered_json:
            stale.append(str(args.output.relative_to(ROOT)))
        if not args.markdown.exists() or args.markdown.read_text(encoding="utf-8") != rendered_markdown:
            stale.append(str(args.markdown.relative_to(ROOT)))
        if report["validation_errors"]:
            print("Inventory validation failed:")
            for error in report["validation_errors"]:
                print(f"- {error}")
            return 1
        if stale:
            print("Inventory outputs are stale:")
            for path in stale:
                print(f"- {path}")
            return 1
        print(f"Inventory check passed: assets={report['summary']['asset_count']}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered_json, encoding="utf-8")
    args.markdown.write_text(rendered_markdown, encoding="utf-8")
    if report["validation_errors"]:
        print("Inventory generated with validation errors:")
        for error in report["validation_errors"]:
            print(f"- {error}")
        return 1
    print(
        f"Inventory generated: assets={report['summary']['asset_count']} "
        f"candidates={report['summary']['candidate_family_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
