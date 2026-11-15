#!/usr/bin/env python3
"""Read-GPT archive audit. Read-only: never extracts or modifies source archives."""
import csv, hashlib, json, zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path.cwd()
ARCHIVES = ["Read.zip", "Read_Original_Logic.zip", "NYAMIST_ONEHIT_REPORTS.zip"]
OUT = ROOT / "reports"
OUT.mkdir(exist_ok=True)

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def inspect_zip(path):
    result = {"name": path.name, "present": path.is_file(),
              "size_bytes": path.stat().st_size if path.is_file() else None,
              "sha256": sha256_file(path) if path.is_file() else None,
              "entries": 0, "files": 0, "directories": 0, "uncompressed_bytes": 0,
              "extensions": {}, "crc_errors": [], "unsafe_paths": [],
              "sample_paths": [], "special_checks": {}}
    if not path.is_file():
        return result
    ext = Counter()
    with zipfile.ZipFile(path) as zf:
        infos = zf.infolist()
        result["entries"] = len(infos)
        result["files"] = sum(not i.is_dir() for i in infos)
        result["directories"] = sum(i.is_dir() for i in infos)
        result["uncompressed_bytes"] = sum(i.file_size for i in infos)
        result["sample_paths"] = [i.filename for i in infos[:30]]
        for info in infos:
            p = PurePosixPath(info.filename)
            if p.is_absolute() or ".." in p.parts:
                result["unsafe_paths"].append(info.filename)
            if not info.is_dir():
                ext[p.suffix.lower() or "[no extension]"] += 1
        result["extensions"] = dict(sorted(ext.items()))
        bad = zf.testzip()
        if bad:
            result["crc_errors"].append(bad)
        names = [i.filename for i in infos if not i.is_dir()]
        if path.name == "Read.zip":
            bins = [n for n in names if n.lower().endswith(".spv")]
            srcs = [n for n in names if n.lower().endswith(".glsl")]
            checks = []
            for name in bins:
                data = zf.read(name)
                checks.append({"path": name, "bytes": len(data),
                               "magic_ok": len(data) >= 20 and len(data) % 4 == 0
                               and data[:4] == b"\x03\x02\x23\x07"})
            result["special_checks"] = {
                "glsl_files": len(srcs), "spv_files": len(bins),
                "spv_magic_valid": sum(x["magic_ok"] for x in checks),
                "spv_details": checks,
                "python_files": sum(n.lower().endswith(".py") for n in names)}
        elif path.name == "Read_Original_Logic.zip":
            result["special_checks"] = {
                "apk_payload_files": [n for n in names if n.lower().endswith((".apk", ".apks", ".xapk", ".aab"))],
                "sha256_manifest_files": [n for n in names if "SHA256_MANIFEST" in n.upper()],
                "python_files": sum(n.lower().endswith(".py") for n in names),
                "video_files": sum(n.lower().endswith((".mp4", ".mkv", ".webm")) for n in names)}
        elif path.name == "NYAMIST_ONEHIT_REPORTS.zip":
            csv_results = {}
            for name in names:
                if name.lower().endswith(".csv"):
                    with zf.open(name) as raw:
                        rows = list(csv.reader(line.decode("utf-8-sig") for line in raw))
                    csv_results[name] = {"rows_excluding_header": max(0, len(rows)-1),
                                         "header": rows[0] if rows else []}
            result["special_checks"] = {"csv_files": csv_results}
    return result

archives = [inspect_zip(ROOT / name) for name in ARCHIVES]
checks = {
    "all_expected_archives_present": all(a["present"] for a in archives),
    "all_zip_crc_checks_clean": all(not a["crc_errors"] for a in archives if a["present"]),
    "no_unsafe_archive_paths": all(not a["unsafe_paths"] for a in archives if a["present"]),
}
read_zip = next(a for a in archives if a["name"] == "Read.zip")
checks["all_spirv_headers_valid"] = (
    read_zip["present"] and
    read_zip["special_checks"].get("spv_magic_valid", 0) ==
    read_zip["special_checks"].get("spv_files", -1))
summary = {
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "repository": "minnya09796592452-rgb/Read-GPT", "branch_scope": "main",
    "read_only": True, "archives": archives, "checks": checks,
    "overall": "PASS" if all(checks.values()) else "FAIL"}
(OUT / "read_gpt_archive_audit.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
lines = ["# Read-GPT Archive Audit", "",
         f"- Generated UTC: {summary['generated_utc']}",
         "- Scope: latest checked-out main commit",
         "- Source archives: read-only; no extraction or modification",
         f"- Overall: **{summary['overall']}**", "", "## Checks"]
for key, value in checks.items():
    lines.append(f"- {'PASS' if value else 'FAIL'} — {key}")
for a in archives:
    lines += ["", f"## {a['name']}", f"- Present: {a['present']}",
              f"- Size: {a['size_bytes']} bytes", f"- SHA-256: {a['sha256']}",
              f"- ZIP entries: {a['entries']} ({a['files']} files, {a['directories']} directories)",
              f"- Uncompressed bytes: {a['uncompressed_bytes']}",
              f"- CRC errors: {len(a['crc_errors'])}", f"- Unsafe paths: {len(a['unsafe_paths'])}",
              "- Extensions: " + ", ".join(f"{k}={v}" for k,v in a["extensions"].items())]
    if a["special_checks"]:
        lines += ["", "### Specialized checks", "~~~json",
                  json.dumps(a["special_checks"], indent=2, ensure_ascii=False), "~~~"]
lines += ["", "## Interpretation",
          "- ZIP CRC and path checks validate archive integrity/safety only.",
          "- SPIR-V header checks do not prove shader validation, pipeline compatibility, or rendering correctness.",
          "- Static archive contents do not prove runtime EOS, Vulkan, or gameplay behavior.",
          "- APK inventory findings are based on archive payloads, not transcript references.", ""]
(OUT / "read_gpt_archive_audit.md").write_text("\n".join(lines), encoding="utf-8")
print("Audit result:", summary["overall"])
if summary["overall"] != "PASS":
    raise SystemExit(1)
