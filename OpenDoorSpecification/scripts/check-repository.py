#!/usr/bin/env python3
import subprocess,sys
cmds=[[sys.executable,'-m','unittest','discover','-s','tests'],[sys.executable,'-m','unittest','discover','-s','tools/ods-tools/tests']]
for cmd in cmds: subprocess.run(cmd,check=True)
print('Repository checks passed.')
