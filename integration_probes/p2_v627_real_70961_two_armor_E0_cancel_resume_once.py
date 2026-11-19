#!/usr/bin/env python3
"""P2 v627 one bounded real 70961 Chrome two signed E0 armor test.

Reuses v621 exact-source cached SimC/Chrome/Cancel/HTTP restart/Resume.
No new solver, no full 64-case run, no local AI runtime.
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
    return prior.run(x.simc,x.out,multi_armor=True)

if __name__=="__main__":
    sys.exit(main())
