from pathlib import Path
import re, argparse
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Generate an evidence checklist from a local requirements brief.')
parser.add_argument('brief',type=Path,help='Path to the local requirements Markdown file')
args=parser.parse_args()
brief=args.brief.read_text(encoding='utf-8')
rows=[]
for line in brief.splitlines():
    if re.match(r'\| (R[1-8]|[A-G][1-7]) \|',line):
        cells=[s.strip() for s in line.strip('|').split('|')]
        code=cells[0]
        rows.append(f'| {code} | {cells[1]} | Pending final verification | |')
text='# Requirements and evidence\n\nAll statuses describe actual verified work. A working scaffold does not close final artistic, documentation or delivery requirements.\n\n| Criterion | Requirement / points | Status | Evidence |\n|---|---|---|---|\n'+'\n'.join(rows)
text+='\n\n## Verified first checkpoint\n\n- C++17 / OpenGL 3.3 core build succeeds with project-local LLVM-MinGW and CMake.\n- The application rendered 360 frames on the RTX 5060 without OpenGL errors.\n- Initial math/game tests cover boundary and rotated point/box tests, standing/crouching, alarm, reset, pause and safe victory.\n- Screenshot: evidence/screenshots/checkpoint-greybox.png. This is a greybox, not final art.\n- Raw diagnostics: evidence/runtime-info.txt.\n\n## Pending external assessment\n\nTA hardware performance, exact course-starter compatibility, live oral defense and the author\'s understanding cannot be certified by local automated checks.\n'
(root/'docs'/'requirements-evidence.md').write_text(text,encoding='utf-8')
