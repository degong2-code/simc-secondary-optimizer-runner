#!/usr/bin/env python3
"""v624: ONE 70961 signed E0 Chrome user session to full 64/95% result and reopen.

Reuses the original v621 real source/option/browser cancel+resume path and
the existing v344 full-result checks. No new SimC executor or simulation.
The v621 partial probe retains its original default, receipts and behavior.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import p1_v621_real_70961_browser_enchant_cancel_resume_once as previous


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--simc",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    args=p.parse_args(argv)
    return previous.run(args.simc,args.out,complete_after_resume=True)


if __name__=="__main__":
    sys.exit(main())
