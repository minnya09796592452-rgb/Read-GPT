#!/usr/bin/env python3
"""Static APK-first compatibility inventory. Never rewrites APK or shader inputs."""
from __future__ import annotations
import argparse, hashlib, json, re, struct, zipfile
from pathlib import Path

APK_NAMES = ["CastawayDepths_3D.apk", "CastawayDepths_Real3D.apk", "CastawayDepths_UI.apk"]
VULKAN_MARKERS = [b"vkCreateInstance", b"vkCreateDevice", b"vkCreateShaderModule", b"vkCreateGraphicsPipelines", b"vkQueueSubmit", b"vkQueuePresentKHR"]
JNI_MARKERS = [b"JNI_OnLoad", b"nativeOnSurfaceCreated", b"nativeOnSurfaceChanged", b"nativeOnSurfaceDestroyed", b"nativeBootstrapReport"]

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def elf_info(data: bytes) -> dict:
    if len(data) < 20 or data[:4] != b"\x7fELF":
        return {"is_elf": False}
    cls, endian = data[4], data[5]
    order = "<" if endian == 1 else ">" if endian == 2 else None
    machine = struct.unpack(order + "H", data[18:20])[0] if order else None
    machines = {3:"x86", 40:"ARM", 62:"x86_64", 183:"AArch64", 243:"RISC-V"}
    return {"is_elf": True, "elf_class": {1:32,2:64}.get(cls), "machine_id": machine,
            "abi_hint": machines.get(machine, "unknown"),
            "vulkan_string_markers": [m.decode() for m in VULKAN_MARKERS if m in data],
            "jni_string_markers": [m.decode() for m in JNI_MARKERS if m in data]}

def spirv_interface(data: bytes) -> dict:
    if len(data) < 20 or len(data) % 4:
        raise ValueError("invalid SPIR-V byte length")
    words = struct.unpack("<" + "I" * (len(data)//4), data)
    if words[0] != 0x07230203:
        raise ValueError("invalid SPIR-V magic")
    bindings, sets, locations, entries = {}, {}, {}, []
    i = 5
    while i < len(words):
        word = words[i]; count, opcode = word >> 16, word & 0xffff
        if count < 1 or i + count > len(words):
            raise ValueError("malformed SPIR-V instruction stream")
        ins = words[i+1:i+count]
        if opcode == 15 and len(ins) >= 2:
            entries.append({"execution_model": ins[0], "function_id": ins[1]})
        elif opcode == 71 and len(ins) >= 3:
            target, decoration, value = ins[0], ins[1], ins[2]
            if decoration == 33: bindings[str(target)] = value
            elif decoration == 34: sets[str(target)] = value
            elif decoration == 30: locations[str(target)] = value
        i += count
    return {"sha256": sha256(data), "bytes": len(data), "entry_points": entries,
            "binding_decorations": bindings, "descriptor_set_decorations": sets,
            "location_decorations": locations}

def inspect_apk(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        bad = z.testzip()
        if bad: raise ValueError(f"{path.name}: CRC failure at {bad}")
        names = z.namelist()
        libs = []
        for n in names:
            if n.startswith("lib/") and n.endswith(".so"):
                raw = z.read(n)
                libs.append({"path": n, "size": len(raw), "sha256": sha256(raw), **elf_info(raw)})
        return {"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path.read_bytes()),
                "zip_entries": len(names), "crc": "PASS", "android_manifest_present": "AndroidManifest.xml" in names,
                "native_libraries": libs, "native_abis": sorted({x["path"].split("/")[1] for x in libs}),
                "assets_shader_like": [n for n in names if re.search(r"\.(spv|glsl|shader|metallib)$", n, re.I)][:250]}

def inspect_shader_archive(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        bad = z.testzip()
        if bad: raise ValueError(f"{path.name}: CRC failure at {bad}")
        shaders = {}
        for n in z.namelist():
            if n.lower().endswith(".spv"):
                shaders[n] = spirv_interface(z.read(n))
        glsl = [n for n in z.namelist() if n.lower().endswith(".glsl")]
        return {"archive": path.name, "crc": "PASS", "shader_modules": shaders,
                "glsl_sources": glsl, "policy": "Original shader bytes/interfaces are inventoried only; no rewrite or rebinding."}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--output", type=Path, default=Path("reports/apk_first_pipeline_alignment.json"))
    args = ap.parse_args(); root = args.repo_root
    result = {"scope": "APK-first static compatibility inventory", "runtime_validation": False,
              "shader_mutation": False, "apk_results": [], "shader_source": None, "limitations": [
                "Static APK/ELF/string inspection does not prove runtime Vulkan pipeline creation or rendering.",
                "No shader inputs, descriptor bindings, vertex locations, varyings, or outputs are modified.",
                "A true integration PASS requires a device run and explicit engine-side descriptor/render-pass compatibility checks."]}
    errors=[]
    for name in APK_NAMES:
        p=root/name
        if not p.is_file(): errors.append(f"missing required APK: {name}"); continue
        try: result["apk_results"].append(inspect_apk(p))
        except Exception as e: errors.append(f"{name}: {e}")
    read_zip=root/"Read.zip"
    if read_zip.is_file():
        try: result["shader_source"]=inspect_shader_archive(read_zip)
        except Exception as e: errors.append(f"Read.zip: {e}")
    else: errors.append("missing required shader/source archive: Read.zip")
    result["errors"]=errors
    result["status"]="BLOCKED" if errors else "STATIC_INVENTORY_COMPLETE_RUNTIME_UNVERIFIED"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps({"status":result["status"],"apk_count":len(result["apk_results"]),
                      "native_lib_counts":{x["file"]:len(x["native_libraries"]) for x in result["apk_results"]},
                      "shader_module_count":len((result.get("shader_source") or {}).get("shader_modules",{})),
                      "errors":errors}, indent=2))
    return 1 if errors else 0
if __name__ == "__main__": raise SystemExit(main())
