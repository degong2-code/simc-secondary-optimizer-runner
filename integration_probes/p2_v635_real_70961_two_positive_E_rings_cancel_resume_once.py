#!/usr/bin/env python3
"""P2 v635 one real 70961 user flow, signed E+ on two rings + E0 chest.

Reuses v621 Chrome (with exact pre-gate state capture), actual Zero-Source v633 v212 installation,
v096/v098 existing adaptive runner, cancel/resume/cache. No 64-case repeat.
"""
import argparse
import pathlib
import sys
import p1_v621_real_70961_browser_enchant_cancel_resume_once as prior

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--simc",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    x=p.parse_args()
    return prior.run(x.simc,x.out,positive_rings=True)

if __name__=="__main__":
    sys.exit(main())
