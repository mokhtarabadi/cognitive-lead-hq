---
tags: [skills, opencode]
---
# Global skills copy must exclude DECISIONS.md and README.md

`cp -r skill-templates/*` copies DECISIONS.md + README.md into global skills; OpenChamber counts them as fake skills (27 shown for 25 real). Always rm the two files after copy; verify global count equals repo skill-dir count (currently 25).