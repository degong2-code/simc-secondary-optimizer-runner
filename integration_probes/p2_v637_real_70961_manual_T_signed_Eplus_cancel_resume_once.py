#!/usr/bin/env python3
"""One real Chrome authoritative manual T=3500 with signed E+ ring pair.

Reuse v621/v635 and v636 original 70961 source, signed v212 E, normal
v096/v098/v093/v094 worker and browser restore. No new optimizer or
64-budget rerun. Confirm B=T=3500, E=58 floors and Native cache resume.
"""
import argparse
import pathlib
import sys
import p1_v621_real_70961_browser_enchant_cancel_resume_once as prior

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--simc",required=True,type=pathlib.Path)
    parser.add_argument("--out",required=True,type=pathlib.Path)
    args=parser.parse_args()
    return prior.run(args.simc,args.out,positive_rings=True,
                     manual_final_T=3500)

if __name__=="__main__":
    sys.exit(main())
