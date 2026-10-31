# Laser Vault Heist v1.0

A standalone C++17 / OpenGL 3.3 core game for topic 12: cross six laser barriers, crouch through the final gap, and open the safe. Includes the complete core and all three stretch goals: rotating spotlights, live CCTV and the safe-opening victory sequence.

## Downloads

- **LaserVaultHeist-Windows-x64.zip**: extract the entire folder and run LaserVaultHeist.exe. Assets and shaders must stay beside the executable. No engine, Blender or compiler is required.
- **LaserVaultHeist-Complete.zip**: source, vendored dependencies, original Blender scenes and rig, scripts, native/GLB exports, executable, report, slides, full demo, subtitle file and evidence.
- **Laser_Vault_Heist_Report.pdf**: 26 pages, 18 verified research references, implementation math and measured results.
- **Laser_Vault_Heist_Presentation.pptx / .pdf**: 10 slides with editable diagrams/chart and speaker notes targeting 8:40.
- **Laser_Vault_Heist_Demo.mp4 / .srt**: 3:30 real-time 1920x1080 capture at 30 fps with visible FPS and captions.
- **SHA256SUMS.txt**: integrity hashes for the release files.

## Verified locally

Clean Release build from a fresh clone; all three CTest suites pass. The portable ZIP passed CRC and file-hash checks and ran from a Unicode extraction path with an unrelated working directory. Its 40-second route run reached two safe-opening cycles without OpenGL errors. Original poses and all final document pages were visually reviewed; the complete MP4 decoded without errors.

Three uncapped 1280x720 runs on i5-13400F / RTX 5060 measured 1281.7, 1183.8 and 1215.8 average FPS. Raw frame times and method are included. These are whole-frame local measurements, not isolated GPU timings or a TA-machine guarantee.

## Remaining external checks

Native human keyboard/mouse usability, the unknown TA computer, exact course-starter compatibility, rehearsal and oral defense are not certified. No grade, classroom attendance, submission or live explanation is fabricated. See docs/requirements-evidence.md and docs/defense-guide.md.
