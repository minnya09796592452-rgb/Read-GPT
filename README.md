# Read-GPT — Castaway Depths Logic Integration

## Project Goal

Integrate the complete extracted logic set into the existing Castaway Depths Editor APK architecture while preserving the Editor's current functionality.

The goal is **not** to insert one isolated logic module or replace the existing engine. The goal is to understand and connect the complete logic pipeline—including its dependencies, shaders, buffers, scene data, and rendering stages—to the APK's existing engine.

This README defines the five-phase engineering plan. It does not claim that integration is already complete or that success is guaranteed before implementation and runtime verification.

## Core Engineering Rules

- Inspect the existing code and project structure before making changes.
- Preserve the complete original logic and its module dependencies.
- Keep the APK Editor's existing features and behavior intact.
- Prefer adapting interfaces over rewriting working logic.
- Do not infer behavior from filenames or static references alone.
- Separate confirmed evidence from assumptions and unverified items.
- Make changes only within the agreed scope.
- Run relevant tests after each implementation stage.
- Never report a test as passed unless it was actually executed successfully.
- Do not promise 100% success before the required source, implementation, and runtime evidence exist.

## Five-Phase Integration Plan

### Phase 1 — Full Logic Mapping

**Objective:** Build a complete inventory and dependency map of the original logic.

Tasks:

- Inventory all extracted logic modules and source files.
- Identify module dependencies, initialization order, update order, and shutdown behavior.
- Trace the complete Ocean lifecycle and scheduler.
- Map wave spectrum generation, Fourier/FFT processing, butterfly lookup, and ping-pong buffers.
- Map displacement, projected-grid, mesh, and wave-query logic.
- Map reflection, depth, mask, overlay, and underwater stages.
- Identify all shaders, shader variants, uniforms, descriptors, textures, buffers, and expected formats.
- Identify physics or gameplay consumers such as buoyancy and surface queries.
- Record missing source, unresolved dependencies, and behavior that cannot be established from available evidence.

**Deliverable:** A complete logic inventory, dependency graph, execution-order map, and evidence/unknowns register.

**Exit criteria:** Every discovered module is classified, dependencies and execution order are documented, and unresolved items are explicitly listed.

### Phase 2 — APK Editor Architecture Mapping

**Objective:** Identify the actual extension and integration points in the target APK Editor.

Tasks:

- Inspect the Editor's available source project and build configuration.
- Trace application startup, scene lifecycle, editor state, and camera state.
- Trace JNI entry points and native-engine initialization where applicable.
- Map the native render loop and frame lifecycle.
- Identify existing mesh, material, texture, buffer, and render-pass abstractions.
- Identify resource ownership, threading, synchronization, and surface recreation behavior.
- Compare the architecture of each supplied APK variant; do not assume the variants are identical.
- Identify supported extension points and the smallest safe integration boundary.

**Deliverable:** An APK architecture map and a verified list of integration points.

**Exit criteria:** The target APK variant and the exact source-level locations for integration are identified. Any unavailable source or opaque component is documented rather than guessed.

### Phase 3 — Compatibility and Bridge Design

**Objective:** Specify how the original logic will communicate with the APK's existing engine.

Tasks:

- Map original lifecycle callbacks to the Editor's lifecycle and frame loop.
- Define the scheduler, update ordering, and synchronization strategy.
- Map original textures and render targets to the engine's GPU image resources.
- Map buffers, descriptors, samplers, and shader parameters.
- Map shader inputs/outputs, formats, layouts, and render-pass dependencies.
- Define the Fourier/FFT pass sequence and intermediate resource ownership.
- Define integration for displacement, ocean surface rendering, reflection, depth, mask, overlays, and underwater effects.
- Map Editor camera, transforms, scene state, and material parameters to the logic inputs.
- Define error handling, device/surface recreation, and resource cleanup.
- Identify required API replacements or compatibility wrappers for dependencies on Unity APIs.

**Deliverable:** A compatibility specification, interface definitions, resource map, render-graph plan, and implementation checklist.

**Exit criteria:** Every required connection has a defined source, destination, data contract, lifecycle, and validation method. Unknown contracts remain marked as blockers.

### Phase 4 — Full Logic Integration

**Objective:** Implement the complete logic integration without discarding unrelated Editor functionality.

Tasks:

- Implement the agreed compatibility and adapter layers.
- Connect the original logic modules in their required dependency and execution order.
- Connect the GPU processing stages to the existing rendering backend.
- Integrate ocean mesh and displacement output with the Editor scene.
- Integrate reflection, depth, mask, overlay, and underwater stages where supported by the target architecture.
- Preserve required query and physics interfaces, including buoyancy-related consumers.
- Handle resource lifetime, synchronization, resize, pause/resume, and shutdown.
- Keep changes scoped and reviewable; avoid unrelated refactoring.
- Build incrementally and record each integration result.

**Deliverable:** An integrated source implementation and a buildable APK candidate.

**Exit criteria:** The integrated modules compile and link, required interfaces are connected, and the APK candidate builds. A successful build alone does not count as proof of correct rendering.

### Phase 5 — Testing, Optimization, and Final APK

**Objective:** Verify correctness, stability, compatibility, and performance.

Tasks:

- Run source-level and unit tests for logic modules where available.
- Validate shader compilation and Vulkan pipeline/resource compatibility.
- Test Fourier/FFT intermediate outputs and final displacement data.
- Verify ocean surface rendering and each enabled rendering stage independently.
- Test camera movement, scene changes, resize, surface recreation, pause/resume, and shutdown.
- Check synchronization, resource lifetime, memory use, and validation-layer errors.
- Test on the intended target device and record device/driver details.
- Compare Editor behavior before and after integration to detect regressions.
- Profile frame time and GPU/CPU cost; optimize only after correctness is established.
- Produce the final APK and a test report with reproducible results.

**Deliverable:** A final APK candidate, test evidence, known-limitations list, and build/release record.

**Exit criteria:** Required tests have actually run, critical failures are resolved or explicitly accepted, and the final report distinguishes verified behavior from unverified behavior.

## Current Evidence and Known Limitations

The repository contains three APK variants:

- `CastawayDepths_3D.apk`
- `CastawayDepths_Real3D.apk`
- `CastawayDepths_UI.apk`

The repository also contains the logic/archive inputs and previous archive-audit reports.

Previously collected static records indicate:

- The extracted Ceto logic includes Ocean lifecycle/scheduling, Fourier shader passes, wave buffers, displacement, projected-grid, reflection, depth/mask, overlays, underwater behavior, and related query/physics logic.
- The Real3D native-rendering records include Vulkan render-loop references and JNI surface lifecycle entry points.
- The extracted shader set includes one vertex shader and eight fragment shader variants.
- Earlier shader-module acceptance records are evidence of shader-module acceptance only; they do not prove graphics-pipeline compatibility or correct rendered output.

Important limitations:

- The static records do not yet prove that the Ceto logic is connected to the APK render loop.
- The internal source-level architecture of all three APK variants has not yet been fully mapped.
- The existence of APK files in the repository does not establish their internal behavior.
- A Vulkan function reference does not prove that a corresponding rendering path executes successfully.
- Shader-module acceptance does not prove descriptor, render-pass, attachment, synchronization, or visual correctness.
- Full runtime integration and device testing have not yet been demonstrated.

## Working Status

| Phase | Status | Evidence required next |
|---|---|---|
| 1. Full Logic Mapping | In progress | Complete module/dependency/execution-order map |
| 2. APK Architecture Mapping | Pending full source inspection | Editor and native-engine integration-point map |
| 3. Compatibility & Bridge Design | Pending | Verified interface/resource/render-graph specification |
| 4. Full Logic Integration | Not started | Integrated source and build evidence |
| 5. Testing & Final APK | Not started | Executed test results and runtime evidence |

Statuses must be updated only when the corresponding evidence exists.

## Change-Control Policy

Before implementation:

1. State the intended files and components to be changed.
2. Explain the implementation approach and expected impact.
3. Keep unrelated files untouched.
4. Preserve original inputs and maintain traceability.
5. Report the exact files changed, commands/tests executed, results, and remaining unverified items.

No source or APK modification is authorized merely by this planning document. Implementation changes must follow the project's agreed change-control process.

## Definition of Done

The project is complete only when:

- The full original logic set and its dependencies are accounted for.
- The target Editor APK architecture and integration points are verified.
- Required compatibility bridges are implemented.
- The complete intended logic pipeline is integrated.
- The resulting APK builds successfully.
- Required runtime and regression tests are executed on the target environment.
- The final report clearly records verified results, limitations, and remaining risks.

**No 100% success guarantee is made in advance.** The project will be judged by implementation evidence and reproducible test results, not assumptions.
