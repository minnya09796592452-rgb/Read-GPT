# Android Porting Readiness Audit

- Date: 2026-11-16
- Repository: `minnya09796592452-rgb/Read-GPT`
- Audited ref: `main`
- Audited commit: `3906bf8fc3e10f25853778829fc7341b83ecd2de`
- Audit mode: read-only inspection of repository tree, README, archive audit, logic inspection report, and available archive contents.
- Scope: determine whether the PC-side logic and the existing Android APK can be ported together without changing the existing shader input contract.
- No APK, original archive, shader, or `main` branch file was modified.

## Executive result

**Porting implementation is BLOCKED by missing implementation inputs.** The repository contains useful extracted Ceto/Ocean and Fourier evidence, shader assets, a Real3D APK binary, and a PC executable. It does not currently contain the Android APK's buildable source project or the PC game's original managed assembly. Therefore an actual, verifiable source-level port cannot yet be implemented from this checkout.

This is not a judgment that the APK is broken. The repository README says the existing APK is working; that runtime claim is not independently re-tested by this static audit.

## Verified repository inventory

The recursive Git tree at the audited commit contains:

- `CastawayDepths_Real3D.apk` — 10,863,224 bytes.
- `Stranded_Deep.exe` — 653,824 bytes.
- `Read.zip` — 2,106,592 bytes.
- `Read_Original_Logic.zip` — 17,154,199 bytes.
- `NYAMIST_LOGIC_PARTS_DETAILED_20261115.zip` — 43,035 bytes, stored both at repository root and under `reports/`.
- `NYAMIST_ONEHIT_REPORTS.zip` — 134,796 bytes.
- Static inventory files: `unity_files.txt`, `binary_metadata.txt`, `startup_strings.txt`, `runtime_directories.txt`, and `SUMMARY.txt`.
- Existing reports: `reports/logic_pipeline_inspection.md`, `reports/logic_pipeline_inspection.json`, `reports/read_gpt_archive_audit.md`, and `reports/read_gpt_archive_audit.json`.
- Existing GitHub Actions workflows for the detailed logic archive inspection and archive audit.

### Important absence from the repository tree

The current tree has no buildable Android project files or source directories such as:

- `settings.gradle`, `build.gradle`, `gradlew`
- `AndroidManifest.xml` in a source project
- `src/main/java` or `src/main/kotlin`
- `CMakeLists.txt`, native C/C++ source, JNI bridge source
- Vulkan renderer source or engine integration source

The README mentions three APK variants (`CastawayDepths_3D.apk`, `CastawayDepths_Real3D.apk`, and `CastawayDepths_UI.apk`), but the audited tree currently contains only `CastawayDepths_Real3D.apk`. The other two variants are not present at this ref.

## What the logic archives actually contain

### `Read.zip`

The archive audit records 300 ZIP entries: 194 files and 106 directories, with no CRC errors and no unsafe paths. The non-`.git` payload includes:

- `Read/ceto/source_records_2026-11-13/ceto_ocean_core_il.txt`
- `Read/ceto/source_records_2026-11-13/ceto_ocean_core_il_resolved.txt`
- `Read/ceto/source_records_2026-11-13/ceto_ocean_metadata.txt`
- `Read/ceto/source_records_2026-11-13/ceto_ocean_method_index.txt`
- Fourier GPU/support IL and resolved token reports
- Nine GLSL shader files and nine SPIR-V files
- Mesh and audio inventory/index records
- Extraction and inspection scripts

This is valuable extracted IL, metadata, shader and asset evidence. It is **not** the original complete PC game C# source tree and does not include the original `Assembly-CSharp.dll` binary.

### `Read_Original_Logic.zip`

The archive contains 16 files: text reports, two P/Invoke scanning scripts, a SHA-256 manifest, and one MP4 recording. Its archive audit reports no APK payload files. It is supporting inspection evidence, not a buildable Android project or a complete PC game source package.

### Detailed Python report ZIP

The 27 entries are 25 Python AST summary reports plus an index and SHA-256 manifest. The existing generated inspection report explicitly classifies all five integration phases as partial and says these are static summaries, not original source files. Keyword matches do not establish runtime execution or successful integration.

### Existing shader evidence

The archive audit found nine GLSL files and nine SPIR-V files, and all nine SPIR-V files have valid magic headers. This establishes basic binary-header integrity only. It does not establish descriptor compatibility, pipeline creation, render-pass compatibility, synchronization correctness, or visual equivalence.

## Porting architecture that should be used

Do not force Windows and Android to use the same native startup sequence. Keep their platform-specific lifecycles and connect the shared logic through a defined adapter boundary.

```text
PC / Unity-side source and extracted Ceto logic
        |
        v
Platform-neutral logic contract
        |
        +-----------------------------+
        |                             |
        v                             v
Windows/Unity adapter          Android adapter
(Unity lifecycle)              (APK lifecycle / JNI)
                                      |
                                      v
                              Existing Android renderer
                                      |
                                      v
                              Existing Vulkan resources
                                      |
                                      v
                              Existing shader interface
```

This is the intended design, not an implemented or verified connection.

## Non-negotiable compatibility constraints

1. Preserve existing APK startup, JNI lifecycle, render loop, and resource ownership unless source inspection proves a specific change is required.
2. Preserve the existing shader contract. Do not rename, reorder, or silently reinterpret shader inputs, descriptor set/binding numbers, push constants, uniform/storage buffer layouts, vertex attributes, texture formats, or render-target expectations.
3. Do not substitute the Windows Unity lifecycle for Android's lifecycle. Map lifecycle events and scheduling explicitly.
4. Keep the original PC logic as the behavioral reference. Any platform-specific replacement must have documented input/output equivalence.
5. Keep future shader integration possible; do not invent missing shader inputs or change contracts to fit an unverified adapter.
6. Keep all work on a dedicated integration branch. Do not modify `main`, the existing APK binary, or original archives during the source-inspection stage.

## Exact inputs needed to unblock implementation

### A. Existing Android APK source project

Provide the project used to build `CastawayDepths_Real3D.apk`, including, where applicable:

- Gradle project and wrapper
- Android manifest and Java/Kotlin application/activity code
- JNI bridge and C/C++ source
- CMake/NDK configuration
- Native engine and Vulkan renderer source
- Shader compilation/resource packaging configuration
- Existing descriptor, buffer, image, render-pass and synchronization definitions

If the project source is unavailable, a read-only APK decompilation and native-library inventory can help identify binary interfaces, but it does not automatically provide a maintainable or complete source project.

### B. PC logic implementation inputs

Provide the actual PC managed assemblies and required dependencies, especially:

- `Stranded_Deep_Data/Managed/Assembly-CSharp.dll`
- Relevant Ceto/managed dependencies
- Matching Unity version/runtime metadata
- Any original source or complete IL/decompiler output that is available

The current `unity_files.txt` records paths on the user's device; it is an inventory, not the DLL payload itself.

### C. Target and baseline evidence

Retain the known-working APK as an immutable baseline and record:

- APK SHA-256 and package/version identity
- Android version and ABI
- GPU/driver information for the target device
- Existing render output or screen recording for visual comparison
- Any known-good shader input/binding manifest

## Implementation sequence after inputs arrive

1. Inspect the APK project and identify its real startup, lifecycle, renderer, and resource ownership.
2. Inspect the original managed assembly and reconstruct the relevant main execution spine and subsystem dependencies.
3. Create an explicit PC-to-Android mapping for lifecycle, scheduler, data types, resource formats, and error handling.
4. Freeze and machine-check the existing shader input contract before changing integration code.
5. Implement the smallest adapter/bridge in the dedicated branch; keep original logic and APK baseline untouched.
6. Add CI checks for contract drift, build/link failures, shader reflection/interface mismatches, and required tests.
7. Build a candidate APK and test it on an emulator for development feedback and on the actual target device for final validation.
8. Compare rendered output and record performance, validation errors, and known limitations.

## Current phase status

| Phase | Status | Reason |
|---|---|---|
| 1. Logic evidence inventory | Partial | Ceto/Fourier IL and assets exist; complete PC source/assemblies are absent |
| 2. APK architecture mapping | Blocked | APK binary exists; buildable Android project/native source is absent |
| 3. Compatibility bridge design | Not yet verifiable | Actual APK renderer contracts and complete PC input/output contracts are unavailable |
| 4. Porting implementation | Not started | Required source inputs are missing |
| 5. Build and runtime validation | Not run | No integrated source/build target exists in this repository |

## Files changed by this audit

Only this report is intended to be added on the dedicated branch:

- `PORTING_READINESS_AUDIT_20261116.md`

No application source, APK, shader, archive, report input, or `main` branch file is changed by this audit.

## Conclusion

The next correct engineering action is **not** to guess JNI calls, invent a Vulkan bridge, or patch the APK binary. It is to obtain the exact Android project source and the original PC managed assemblies, then map their real interfaces before implementing the adapter.

This keeps the working APK safe, preserves the shader input contract, and makes CI capable of rejecting a genuine interface mismatch rather than merely passing archive-integrity checks.
