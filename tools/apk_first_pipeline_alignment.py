#!/usr/bin/env python3
"""Fail-closed APK-first evidence inventory; never rewrites APK or shader inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import zipfile
from pathlib import Path

APK_NAMES = ("CastawayDepths_3D.apk", "CastawayDepths_Real3D.apk", "CastawayDepths_UI.apk")
VIDEO_ARCHIVE = "Read_Original_Logic.zip"
VIDEO_NAME = "Screenrecorder-2026-11-15-11-21-48-658.mp4"
VULKAN_MARKERS = (
    b"vkCreateInstance", b"vkCreateDevice", b"vkCreateShaderModule",
    b"vkCreateGraphicsPipelines", b"vkCreateRenderPass", b"vkCmdBeginRenderPass",
    b"vkCmdBindPipeline", b"vkCmdDraw", b"vkQueueSubmit", b"vkQueuePresentKHR",
)
JNI_MARKERS = (
    b"JNI_OnLoad", b"nativeOnSurfaceCreated", b"nativeOnSurfaceChanged",
    b"nativeOnSurfaceDestroyed", b"nativeBootstrapReport",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def elf_info(data: bytes) -> dict:
    if len(data) < 20 or data[:4] != b"\x7fELF":
        return {"is_elf": False}
    elf_class, endian = data[4], data[5]
    order = "<" if endian == 1 else ">" if endian == 2 else None
    if order is None:
        return {"is_elf": True, "malformed_header": True}
    machine = struct.unpack(order + "H", data[18:20])[0]
    machines = {3: "x86", 40: "ARM", 62: "x86_64", 183: "AArch64", 243: "RISC-V"}
    return {
        "is_elf": True,
        "elf_class": {1: 32, 2: 64}.get(elf_class, "unknown"),
        "machine_id": machine,
        "abi_hint": machines.get(machine, "unknown"),
        "vulkan_string_markers": [m.decode() for m in VULKAN_MARKERS if m in data],
        "jni_string_markers": [m.decode() for m in JNI_MARKERS if m in data],
    }


def _spirv_string(words: tuple[int, ...]) -> str:
    raw = struct.pack("<" + "I" * len(words), *words)
    return raw.split(b"\0", 1)[0].decode("utf-8", errors="replace")


def spirv_interface(data: bytes) -> dict:
    if len(data) < 20 or len(data) % 4:
        raise ValueError("invalid SPIR-V byte length")
    words = struct.unpack("<" + "I" * (len(data) // 4), data)
    if words[0] != 0x07230203:
        raise ValueError("invalid SPIR-V magic")
    if words[4] == 0:
        raise ValueError("invalid SPIR-V id bound")
    decorations: dict[str, dict] = {}
    names: dict[str, str] = {}
    entries = []
    variables = []
    i = 5
    while i < len(words):
        first = words[i]
        count, opcode = first >> 16, first & 0xFFFF
        if count < 1 or i + count > len(words):
            raise ValueError(f"malformed SPIR-V instruction at word {i}")
        ins = words[i + 1:i + count]
        if opcode == 5 and len(ins) >= 2:  # OpName
            names[str(ins[0])] = _spirv_string(ins[1:])
        elif opcode == 15 and len(ins) >= 3:  # OpEntryPoint
            entries.append({
                "execution_model": ins[0],
                "function_id": ins[1],
                "name": _spirv_string(ins[2:]),
                "interface_ids": [str(x) for x in ins[2 + (len(_spirv_string(ins[2:]).encode()) + 1 + 3) // 4:]],
            })
        elif opcode == 71 and len(ins) >= 2:  # OpDecorate
            target, decoration = str(ins[0]), ins[1]
            if decoration in (30, 33, 34) and len(ins) >= 3:
                key = {30: "location", 33: "binding", 34: "descriptor_set"}[decoration]
                decorations.setdefault(target, {})[key] = ins[2]
        elif opcode == 59 and len(ins) >= 3:  # OpVariable
            variables.append({"result_type": ins[0], "id": str(ins[1]), "storage_class": ins[2]})
        i += count
    interface = []
    for var in variables:
        item = dict(var)
        item["name"] = names.get(item["id"])
        item.update(decorations.get(item["id"], {}))
        interface.append(item)
    return {
        "sha256": sha256(data),
        "bytes": len(data),
        "version_word": f"0x{words[1]:08x}",
        "generator": words[2],
        "id_bound": words[3],
        "entry_points": entries,
        "interface_variables": interface,
        "decorations_by_id": decorations,
    }


def inspect_apk(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"{path.name}: CRC failure at {bad}")
        names = archive.namelist()
        libs = []
        for name in names:
            if name.startswith("lib/") and name.endswith(".so"):
                raw = archive.read(name)
                libs.append({
                    "path": name, "size": len(raw), "sha256": sha256(raw),
                    **elf_info(raw),
                })
        return {
            "file": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256(path.read_bytes()),
            "zip_entries": len(names),
            "crc": "PASS",
            "android_manifest_present": "AndroidManifest.xml" in names,
            "native_libraries": libs,
            "native_abis": sorted({item["path"].split("/")[1] for item in libs}),
            "assets_shader_like": [
                name for name in names
                if re.search(r"\.(spv|glsl|shader|metallib)$", name, re.I)
            ],
        }


def inspect_shader_archive(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"{path.name}: CRC failure at {bad}")
        shaders = {
            name: spirv_interface(archive.read(name))
            for name in archive.namelist() if name.lower().endswith(".spv")
        }
        glsl = [name for name in archive.namelist() if name.lower().endswith(".glsl")]
        return {
            "archive": path.name,
            "crc": "PASS",
            "shader_modules": shaders,
            "glsl_sources": glsl,
            "policy": "Original shader bytes/interfaces are inventoried only; no rewrite or rebinding.",
        }


def inspect_video_evidence(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"{path.name}: CRC failure at {bad}")
        try:
            info = archive.getinfo(VIDEO_NAME)
        except KeyError as exc:
            raise ValueError(f"runtime evidence video missing: {VIDEO_NAME}") from exc
        digest = hashlib.sha256()
        with archive.open(info) as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
        return {
            "archive": path.name,
            "path": VIDEO_NAME,
            "bytes": info.file_size,
            "sha256": digest.hexdigest(),
            "evidence_type": "user-supplied visual runtime recording",
            "observed_limit": "Visual evidence of an APK session; not proof of Vulkan validation-layer cleanliness or every pipeline/descriptor contract.",
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("reports/apk_first_pipeline_alignment.json"))
    args = parser.parse_args()
    root = args.repo_root
    result = {
        "scope": "APK-first static compatibility and evidence inventory",
        "runtime_validation": False,
        "integration_gate": "BLOCKED",
        "shader_mutation": False,
        "apk_results": [],
        "shader_source": None,
        "video_evidence": None,
        "limitations": [
            "Static APK/ELF/SPIR-V inspection cannot prove runtime graphics-pipeline creation or rendering correctness.",
            "The recording is retained as visual runtime evidence, but cannot prove descriptor/render-pass compatibility or absence of GPU validation errors.",
            "No candidate pipeline artifact or machine-generated device-runtime attestation is currently part of this gate.",
            "No shader inputs, descriptor bindings, vertex locations, varyings, or outputs are modified.",
            "A PASS requires an instrumented target-device run of both the golden APK and candidate, with pipeline creation, draw submission, frame capture, and validation-error checks.",
        ],
    }
    errors = []
    for name in APK_NAMES:
        path = root / name
        if not path.is_file():
            errors.append(f"missing required APK: {name}")
            continue
        try:
            result["apk_results"].append(inspect_apk(path))
        except Exception as exc:
            errors.append(f"{name}: {exc}")
    read_zip = root / "Read.zip"
    if read_zip.is_file():
        try:
            result["shader_source"] = inspect_shader_archive(read_zip)
        except Exception as exc:
            errors.append(f"Read.zip: {exc}")
    else:
        errors.append("missing required shader/source archive: Read.zip")
    video_zip = root / VIDEO_ARCHIVE
    if video_zip.is_file():
        try:
            result["video_evidence"] = inspect_video_evidence(video_zip)
        except Exception as exc:
            errors.append(f"{VIDEO_ARCHIVE}: {exc}")
    else:
        errors.append(f"missing runtime evidence archive: {VIDEO_ARCHIVE}")
    result["errors"] = errors
    result["static_inventory_status"] = "BLOCKED" if errors else "COMPLETE"
    result["status"] = "BLOCKED_RUNTIME_GATE"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {
        "status": result["status"],
        "static_inventory_status": result["static_inventory_status"],
        "apk_count": len(result["apk_results"]),
        "native_library_counts": {
            item["file"]: len(item["native_libraries"]) for item in result["apk_results"]
        },
        "shader_module_count": len((result.get("shader_source") or {}).get("shader_modules", {})),
        "video_evidence_present": result["video_evidence"] is not None,
        "errors": errors,
    }
    print(json.dumps(summary, indent=2))
    # Deliberately fail closed: static inventory or a video cannot satisfy runtime integration.
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
