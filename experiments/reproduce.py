"""Run a recorded physical variant in a new directory with an installed PDK."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys

p = argparse.ArgumentParser()
p.add_argument('--variant', required=True)
p.add_argument('--pdk-root', type=Path, required=True)
p.add_argument('--template', type=Path, required=True)
p.add_argument('--work-dir', type=Path, required=True)
p.add_argument('--jobs', type=int, default=4)
args = p.parse_args()
repo = Path(__file__).resolve().parents[1]
source = repo/'experiments/configs'/f'{args.variant}.json'
config = json.loads(source.read_text())
work = args.work_dir.resolve()
work.mkdir(parents=True, exist_ok=False)
(work/'src').mkdir()
template_dir = work/'tt/tech/sky130A/def'
template_dir.mkdir(parents=True)
shutil.copyfile(args.template, template_dir/'tt_block_1x1_pg.def')
shutil.copyfile(repo/'src/project.v', work/'src/project.v')
(work/'src/config.json').write_text(json.dumps(config, indent=2)+'\n')
subprocess.run([sys.executable, '-m', 'librelane', '--manual-pdk',
                '--pdk-root', str(args.pdk_root.resolve()), '--pdk', 'sky130A',
                '--run-tag', args.variant, '-j', str(args.jobs), '--condensed',
                str(work/'src/config.json')], check=True)
