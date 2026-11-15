# Read-GPT Archive Audit

- Generated UTC: 2026-11-15T11:53:35.596572+00:00
- Scope: latest checked-out main commit
- Source archives: read-only; no extraction or modification
- Overall: **PASS**

## Checks
- PASS — all_expected_archives_present
- PASS — all_zip_crc_checks_clean
- PASS — no_unsafe_archive_paths
- PASS — all_spirv_headers_valid

## Read.zip
- Present: True
- Size: 2106592 bytes
- SHA-256: d5b81909be29a74fb0e2fd2ca40c21f60cfbc94fd075687a7cbf9a468faf632e
- ZIP entries: 300 (194 files, 106 directories)
- Uncompressed bytes: 2047860
- CRC errors: 0
- Unsafe paths: 0
- Extensions: .csv=2, .glsl=9, .idx=1, .md=3, .pack=1, .py=9, .rev=1, .sample=14, .spv=9, .txt=30, [no extension]=115

### Specialized checks
~~~json
{
  "glsl_files": 9,
  "spv_files": 9,
  "spv_magic_valid": 9,
  "spv_details": [
    {
      "path": "Read/ceto/shaders_2026-11-13/entry_0_fragment_vk.spv",
      "bytes": 2368,
      "magic_ok": true
    },
    {
      "path": "Read/ceto/shaders_2026-11-13/entry_0_vertex_vk.spv",
      "bytes": 2520,
      "magic_ok": true
    },
    {
      "path": "Read/ceto/shaders_2026-11-13/entry_1_fragment_vk.spv",
      "bytes": 2396,
      "magic_ok": true
    },
    {
      "path": "Read/ceto/shaders_2026-11-13/entry_2_fragment_vk.spv",
      "bytes": 3608,
      "magic_ok": true
    },
    {
      "path": "Read/ceto/shaders_2026-11-13/entry_3_fragment_vk.spv",
      "bytes": 3636,
      "magic_ok": true
    },
    {
      "path": "Read/ceto/shaders_2026-11-13/entry_4_fragment_vk.spv",
      "bytes": 4712,
      "magic_ok": true
    },
    {
      "path": "Read/ceto/shaders_2026-11-13/entry_5_fragment_vk.spv",
      "bytes": 4740,
      "magic_ok": true
    },
    {
      "path": "Read/ceto/shaders_2026-11-13/entry_6_fragment_vk.spv",
      "bytes": 5760,
      "magic_ok": true
    },
    {
      "path": "Read/ceto/shaders_2026-11-13/entry_7_fragment_vk.spv",
      "bytes": 5788,
      "magic_ok": true
    }
  ],
  "python_files": 9
}
~~~

## Read_Original_Logic.zip
- Present: True
- Size: 17154199 bytes
- SHA-256: 886bc9e98c7865b2283b2e3e4cdbb4bfde86a8c074bb504e64ecacaa7b9d6a97
- ZIP entries: 16 (16 files, 0 directories)
- Uncompressed bytes: 17151733
- CRC errors: 0
- Unsafe paths: 0
- Extensions: .md=1, .mp4=1, .py=2, .txt=12

### Specialized checks
~~~json
{
  "apk_payload_files": [],
  "sha256_manifest_files": [
    "PInvoke_SHA256_MANIFEST.txt"
  ],
  "python_files": 2,
  "video_files": 1
}
~~~

## NYAMIST_ONEHIT_REPORTS.zip
- Present: True
- Size: 134796 bytes
- SHA-256: 33ec68093b62419364d3178c76311893bd9c4e98d2defcfa292c889c09344b59
- ZIP entries: 5 (5 files, 0 directories)
- Uncompressed bytes: 133724
- CRC errors: 0
- Unsafe paths: 0
- Extensions: .csv=4, .txt=1

### Specialized checks
~~~json
{
  "csv_files": {
    "NYAMIST_DEEP_ONEHIT_20261115_161102_ERRORS.csv": {
      "rows_excluding_header": 0,
      "header": [
        "scope",
        "path",
        "error"
      ]
    },
    "NYAMIST_DEEP_ONEHIT_20261115_161102_MANAGED_MANIFEST.csv": {
      "rows_excluding_header": 119,
      "header": [
        "status",
        "manifest_relative_path",
        "expected_sha256",
        "original_hash_status",
        "original_sha256",
        "original_bytes",
        "world_hash_candidates",
        "world_exact_candidates",
        "world_exact_path",
        "note"
      ]
    },
    "NYAMIST_DEEP_ONEHIT_20261115_161102_ORIGINAL.csv": {
      "rows_excluding_header": 217,
      "header": [
        "status",
        "original_path",
        "filename",
        "bytes",
        "sha256",
        "world_exact_match",
        "original_alias_count",
        "world_candidate_count",
        "world_exact_count",
        "alias_integrity"
      ]
    },
    "NYAMIST_DEEP_ONEHIT_20261115_161102_WORLD_CANDIDATES.csv": {
      "rows_excluding_header": 347,
      "header": [
        "sha256",
        "bytes",
        "world_path",
        "byte_result",
        "difference_offset_or_error"
      ]
    }
  }
}
~~~

## Interpretation
- ZIP CRC and path checks validate archive integrity/safety only.
- SPIR-V header checks do not prove shader validation, pipeline compatibility, or rendering correctness.
- Static archive contents do not prove runtime EOS, Vulkan, or gameplay behavior.
- APK inventory findings are based on archive payloads, not transcript references.
