# Release packaging

A Windows package contains `LaserVaultHeist.exe`, `assets/` and `shaders/`.
These folders must remain beside the executable. Runtime libraries are linked
or included through the CMake project; authoring applications are not required.

The repository contains current source. Published release archives are immutable
versioned snapshots and may contain an earlier asset or document revision.

## Create a package

After a Release build and passing CTest run:

```powershell
cmake --install build --prefix dist/Windows-x64
```

The resulting folder can be distributed as a complete ZIP. The PDF report is
stored separately under `deliverables/report/`. Component origins and license
notices are recorded in `CREDITS.md` and `LICENSES/`.
