#!/usr/bin/env python3
"""Build a read-only, hash-locked research Knowledge distribution.

The bundle intentionally contains compiled packages and the static GPT
projection, but none of the Builder, Compiler, source cache, or writable
feedback paths.  It is therefore a deployment snapshot, not another Knowledge
authoring checkout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import textwrap
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repository_revision() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--short=12", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc"),
    )


def package_metadata(path: Path) -> dict[str, str]:
    package = json.loads(path.read_text(encoding="utf-8"))
    return {
        "file": f"packages/{path.name}",
        "id": package.get("package_id") or path.stem,
        "version": package.get("package_version") or "unknown",
        "status": package.get("release_state") or "unknown",
        "review_status": package.get("provenance", {}).get("review_status", "unknown"),
        "semantic_digest": package.get("semantic_digest", "missing"),
        "sha256": sha256(path),
    }


def bundled_verify_script() -> str:
    return textwrap.dedent(
        '''\
        #!/usr/bin/env python3
        """Verify every hash-locked file in this frozen release."""
        from __future__ import annotations
        import hashlib
        import json
        import sys
        from pathlib import Path

        ROOT = Path(__file__).resolve().parents[1]
        MANIFEST = ROOT / "snapshot-manifest.json"

        def digest(path: Path) -> str:
            h = hashlib.sha256()
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    h.update(chunk)
            return h.hexdigest()

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        expected = manifest["files"]
        actual_files = {
            p.relative_to(ROOT).as_posix()
            for p in ROOT.rglob("*")
            if p.is_file() and p != MANIFEST
        }
        expected_files = set(expected)
        errors = []
        for relative, expected_hash in sorted(expected.items()):
            path = ROOT / relative
            if not path.is_file():
                errors.append(f"missing: {relative}")
            elif digest(path) != expected_hash:
                errors.append(f"digest mismatch: {relative}")
        for relative in sorted(actual_files - expected_files):
            errors.append(f"unexpected: {relative}")
        if errors:
            print("Frozen Knowledge verification FAILED", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            raise SystemExit(1)
        print(
            f"Frozen Knowledge verification PASSED: "
            f"{len(expected)} files, {manifest['package_count']} packages, "
            f"snapshot {manifest['snapshot_id']}"
        )
        '''
    )


def bundled_server_script() -> str:
    return textwrap.dedent(
        '''\
        #!/usr/bin/env python3
        """Serve the frozen read-only Knowledge API with Python stdlib."""
        from __future__ import annotations
        import argparse
        import os
        from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
        from pathlib import Path

        ROOT = Path(__file__).resolve().parents[1] / "knowledge-api"

        class ReadOnlyHandler(SimpleHTTPRequestHandler):
            def do_POST(self):
                self.send_error(405, "Frozen Knowledge API is read-only")
            do_PUT = do_POST
            do_PATCH = do_POST
            do_DELETE = do_POST

        parser = argparse.ArgumentParser()
        parser.add_argument("--host", default="127.0.0.1")
        parser.add_argument("--port", type=int, default=8765)
        args = parser.parse_args()
        os.chdir(ROOT)
        server = ThreadingHTTPServer((args.host, args.port), ReadOnlyHandler)
        print(f"Frozen Knowledge API: http://{args.host}:{args.port}/gpt/manifest.json")
        print("This process serves files only and accepts no patient responses.")
        server.serve_forever()
        '''
    )


def bundled_chat_script() -> str:
    return textwrap.dedent(
        r'''
        #!/usr/bin/env python3
        """In-memory research harness for an OpenAI-compatible chat endpoint."""
        from __future__ import annotations
        import argparse
        import json
        import os
        import ssl
        import sys
        import urllib.error
        import urllib.request
        from pathlib import Path

        ROOT = Path(__file__).resolve().parents[1]
        GPT = ROOT / "knowledge-api" / "gpt"

        def load_json(relative: str):
            return json.loads((GPT / relative).read_text(encoding="utf-8"))

        def slug_for_entry(entry: dict) -> str:
            return entry["id"].removeprefix("rfe.")

        def match_rfe(text: str, catalog: dict):
            normalized = text.strip().casefold()
            candidates = []
            for entry in catalog["entries"]:
                if entry.get("implementation_status") != "implemented":
                    continue
                terms = [entry.get("display", ""), entry.get("display_ko", "")]
                terms.extend(entry.get("aliases", []))
                for term in terms:
                    key = str(term).strip().casefold()
                    if key and (normalized == key or key in normalized):
                        candidates.append((len(key), entry))
            if not candidates:
                return None
            candidates.sort(key=lambda item: (-item[0], item[1]["id"]))
            best_length = candidates[0][0]
            best = {item[1]["id"]: item[1] for item in candidates if item[0] == best_length}
            return next(iter(best.values())) if len(best) == 1 else None

        def endpoint(base_url: str) -> str:
            clean = base_url.rstrip("/")
            if clean.endswith("/chat/completions"):
                return clean
            if clean.endswith("/v1"):
                return clean + "/chat/completions"
            return clean + "/v1/chat/completions"

        def request_chat(url: str, model: str, messages: list[dict], api_key: str, timeout: int):
            body = json.dumps({
                "model": model,
                "messages": messages,
                "temperature": 0.1,
                "stream": False,
            }, ensure_ascii=False).encode("utf-8")
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            request = urllib.request.Request(url, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(request, timeout=timeout, context=ssl.create_default_context()) as response:
                result = json.loads(response.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]

        def build_system_prompt(entry: dict) -> str:
            slug = slug_for_entry(entry)
            resources = {
                "frozen_snapshot": load_json("../snapshot-summary.json"),
                "common_facts": load_json("common-facts.json"),
                "reason_for_encounter": entry,
                "facts": load_json(f"rfe/{slug}/facts.json"),
                "questions": load_json(f"rfe/{slug}/questions.json"),
                "rules": load_json(f"rfe/{slug}/rules.json"),
            }
            instructions = (GPT / "GPT_INSTRUCTIONS.md").read_text(encoding="utf-8")
            local_contract = """
        LOCAL FROZEN ADAPTER CONTRACT (highest priority for this run)
        - The Knowledge Action calls described below have already been completed locally.
        - Use only the embedded frozen resources. Never call tools, browse, update Knowledge,
          reinterpret sources, or invent package Facts/Questions/Rules.
        - Do not emit analytics or feedback events. Keep answers only in this process memory.
        - This is research_only/unreviewed content, not a diagnostic or production service.
        - The selected package cannot change during this encounter.
        """.strip()
            return (
                local_contract
                + "\n\nPROJECT INTERVIEW INSTRUCTIONS\n"
                + instructions
                + "\n\nPRELOADED FROZEN RESOURCES\n"
                + json.dumps(resources, ensure_ascii=False, separators=(",", ":"))
            )

        parser = argparse.ArgumentParser()
        parser.add_argument("--base-url", default=os.getenv("LLM_BASE_URL", ""))
        parser.add_argument("--model", default=os.getenv("LLM_MODEL", ""))
        parser.add_argument("--api-key", default=os.getenv("LLM_API_KEY", ""))
        parser.add_argument("--timeout", type=int, default=180)
        parser.add_argument("--rfe", help="RFE alias or initial patient statement")
        parser.add_argument("--message", help="Run one initial message and exit")
        args = parser.parse_args()
        if not args.base_url or not args.model:
            parser.error("set --base-url/LLM_BASE_URL and --model/LLM_MODEL")

        catalog = load_json("reason-for-encounters.json")
        initial = args.message or args.rfe or input("오늘 어떤 이유로 오셨나요? ").strip()
        entry = match_rfe(initial, catalog)
        if entry is None:
            print("동결 catalog에서 하나의 구현 RFE로 확정하지 못했습니다.", file=sys.stderr)
            print("정확한 증상명 또는 RFE 별칭을 --rfe로 지정해 주세요.", file=sys.stderr)
            raise SystemExit(2)

        print(f"Frozen package selected: {entry['id']} ({entry.get('display_ko')})")
        messages = [
            {"role": "system", "content": build_system_prompt(entry)},
            {"role": "user", "content": initial},
        ]
        url = endpoint(args.base_url)
        try:
            answer = request_chat(url, args.model, messages, args.api_key, args.timeout)
        except (urllib.error.URLError, KeyError, ValueError) as exc:
            print(f"LLM request failed: {exc}", file=sys.stderr)
            raise SystemExit(1)
        print(f"\nASSISTANT\n{answer}")
        if args.message:
            raise SystemExit(0)
        messages.append({"role": "assistant", "content": answer})
        while True:
            user = input("\nUSER (종료: /quit)\n").strip()
            if user == "/quit":
                break
            messages.append({"role": "user", "content": user})
            answer = request_chat(url, args.model, messages, args.api_key, args.timeout)
            print(f"\nASSISTANT\n{answer}")
            messages.append({"role": "assistant", "content": answer})
        '''
    ).lstrip()


def readme(snapshot_id: str, revision: str, package_count: int) -> str:
    return textwrap.dedent(
        f'''\
        # Clinical Interview Frozen Knowledge — Research Release

        Snapshot: `{snapshot_id}`

        Repository revision: `{revision}`
        Compiled RFE packages: `{package_count}`

        이 배포본은 현재까지 축적·컴파일된 Knowledge를 **갱신 없이 그대로
        실행·검토하기 위한 동결 연구용 스냅샷**입니다. Builder, Compiler, 외부
        source 수집기, STOM 쓰기 기능과 feedback 수집 경로를 포함하지 않습니다.

        ## 가장 먼저 할 일

        ```bash
        python3 app/verify.py
        ```

        검증에 실패한 스냅샷은 사용하지 마십시오. `snapshot-manifest.json`에
        기록되지 않은 파일이 추가되거나 기존 파일이 바뀌어도 실패합니다.

        ## 사용 방식 1: 읽기 전용 Knowledge API

        ```bash
        python3 app/serve.py
        # http://127.0.0.1:8765/gpt/manifest.json
        ```

        이 서버는 정적 GET만 제공하며 환자 답변을 받거나 저장하지 않습니다.

        ## 사용 방식 2: OpenAI 호환 LLM 연구 테스트

        ```bash
        export LLM_BASE_URL=https://your-host.example/v1
        export LLM_MODEL=your-model
        export LLM_API_KEY=optional-secret
        python3 app/chat.py --rfe "머리가 아파요"
        ```

        `chat.py`는 현재 프로세스 메모리에만 대화를 유지합니다. 하나의 RFE를
        catalog alias로 선택하고 그 RFE의 동결 Facts, Questions, Rules와 공통
        Facts만 모델에 제공합니다. LLM은 표현 이해와 문장화를 담당하며 Knowledge를
        갱신할 수 없습니다.

        ## 포함 범위

        - `packages/`: hash-locked immutable compiled packages
        - `knowledge-api/gpt/`: 답변이 없는 정적 Knowledge/Fact API projection
        - `app/verify.py`: 전체 파일 SHA-256 검증
        - `app/serve.py`: 읽기 전용 정적 API
        - `app/chat.py`: OpenAI 호환 endpoint용 비영속 연구 harness

        ## 중요한 한계

        - 모든 임상 내용은 `research_only/unreviewed`이며 production 승인본이 아닙니다.
        - 진단·치료·의료인 대체 용도가 아닙니다.
        - 이 harness는 현재 Custom GPT 연구 흐름을 외부 OpenAI 호환 모델에서
          비교하기 위한 것이며, 완전한 production Clinical Memory/FHIR 저장소가
          아닙니다.
        - 패키지가 낡거나 결함이 발견되어도 이 스냅샷은 자동으로 고쳐지지 않습니다.
          새 지식은 반드시 별도 버전의 새 스냅샷으로만 배포해야 합니다.
        - 실제 환자정보와 직접 식별자를 입력하지 마십시오. endpoint 운영자의
          개인정보 및 보안 정책이 별도로 적용됩니다.
        '''
    )


def build(output_dir: Path, zip_path: Path | None, created_at: str) -> dict:
    revision = repository_revision()
    snapshot_id = f"clinical-interview-frozen-{revision}-{created_at[:10].replace('-', '')}"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    copy_tree(ROOT / "docs" / "gpt", output_dir / "knowledge-api" / "gpt")
    (output_dir / "packages").mkdir()
    package_paths = sorted((ROOT / "packages" / "generated").glob("*.json"))
    packages = []
    for source in package_paths:
        shutil.copy2(source, output_dir / "packages" / source.name)
        packages.append(package_metadata(source))

    write_text(output_dir / "app" / "verify.py", bundled_verify_script())
    write_text(output_dir / "app" / "serve.py", bundled_server_script())
    write_text(output_dir / "app" / "chat.py", bundled_chat_script())
    write_text(output_dir / "README.md", readme(snapshot_id, revision, len(packages)))

    summary = {
        "snapshot_id": snapshot_id,
        "repository_revision": revision,
        "created_at": created_at,
        "knowledge_update_mode": "disabled",
        "runtime_usage": ["research_test", "simulation"],
        "review_status": "unreviewed",
        "package_count": len(packages),
        "contains_patient_responses": False,
        "external_medical_source_access": False,
        "terminology_server_required_at_runtime": False,
    }
    write_text(
        output_dir / "knowledge-api" / "snapshot-summary.json",
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
    )

    files = {
        path.relative_to(output_dir).as_posix(): sha256(path)
        for path in sorted(output_dir.rglob("*"))
        if path.is_file()
    }
    manifest = {
        **summary,
        "immutability": {
            "policy": "files_are_read_only_by_contract_and_verified_by_sha256",
            "manifest_self_digest": "excluded",
            "silent_upgrade_allowed": False,
        },
        "packages": packages,
        "files": files,
    }
    write_text(
        output_dir / "snapshot-manifest.json",
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )

    if zip_path:
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(output_dir.rglob("*")):
                if not path.is_file():
                    continue
                relative = Path(snapshot_id) / path.relative_to(output_dir)
                info = zipfile.ZipInfo(relative.as_posix(), date_time=(2026, 7, 31, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100444 << 16
                archive.writestr(info, path.read_bytes())
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--zip", dest="zip_path", type=Path)
    parser.add_argument(
        "--created-at",
        default=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    )
    args = parser.parse_args()
    manifest = build(args.output_dir.resolve(), args.zip_path.resolve() if args.zip_path else None, args.created_at)
    print(
        f"Built {manifest['snapshot_id']}: {manifest['package_count']} packages, "
        f"{len(manifest['files'])} verified files"
    )


if __name__ == "__main__":
    main()
