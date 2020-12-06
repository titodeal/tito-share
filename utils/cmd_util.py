import subprocess
from subprocess import PIPE


def run_subprocess(cmd):
    proc = subprocess.run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    return (
            proc.returncode,
            proc.stdout.decode().strip(),
            proc.stderr.decode().strip()
            )

