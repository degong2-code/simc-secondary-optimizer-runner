"""Offline checks for the exact Docker image digest -> SimC revision hint.

No Docker pull, registry HTTP, Native or newly assumed season ItemID.
"""
import json
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"integration_probes")]
from integration_probes import p3_fs_simc_image_revision as pin

DIGEST="sha256:"+"a"*64
OTHER="sha256:"+"b"*64
REF="simulationcraftorg/simc@"+DIGEST
BUILD="12.1.5.70783"


class Response:
    status=200
    def __init__(self, payload):self.payload=payload
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,n):return self.payload[:n]


class ImageToPinnedSourceHint(unittest.TestCase):
    def records(self,with_tag=True):
        return {"results":[
            {"name":"latest","digest":DIGEST},
            {"name":"1215-2026-11-05-1abc234","digest":DIGEST,
             "images":[{"architecture":"amd64","os":"linux",
                        "digest":DIGEST}]} if with_tag else
            {"name":"1215-2026-11-05-1abc234","digest":OTHER},
            {"name":"1215-2026-10-20-7ff7fff","digest":OTHER},
            {"name":"1210-2026-11-05-1abc234","digest":DIGEST}
        ]}

    def test_digest_matched_tag_is_only_revision_hint(self):
        d=pin.select_from_tags(document=self.records(),image_ref=REF,
                               game_build=BUILD)
        self.assertEqual(d["revision_hint"],"1abc234")
        self.assertEqual(d["image_digest"],DIGEST)
        self.assertEqual(d["source_tag"],"1215-2026-11-05-1abc234")
        self.assertTrue(d[
            "source_identity_not_binary_or_season_attestation"])
        calls=[]
        def fetch(req,timeout):
            calls.append((req.full_url,timeout))
            return Response(json.dumps(self.records()).encode())
        got=pin.discover(image_ref=REF,game_build=BUILD,fetch=fetch)
        self.assertEqual(got,d)
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0][1],25)

    def test_no_guess_if_digest_or_build_is_unmatched(self):
        with self.assertRaisesRegex(
                pin.SimCImageRevisionPending,
                "SIMC_IMAGE_MATCHING_TAG_REVISION"):
            pin.select_from_tags(document=self.records(with_tag=False),
                                 image_ref=REF,game_build=BUILD)
        with self.assertRaisesRegex(
                pin.SimCImageRevisionPending,
                "SIMC_IMAGE_MATCHING_TAG_REVISION"):
            pin.select_from_tags(document=self.records(),image_ref=REF,
                                 game_build="12.2.0.70783")
        with self.assertRaisesRegex(
                pin.SimCImageRevisionPending,
                "SIMC_PINNED_IMAGE_OR_BUILD_REQUIRED"):
            pin.select_from_tags(document=self.records(),
                                 image_ref="simulationcraftorg/simc:latest",
                                 game_build=BUILD)

    def test_ambiguous_revision_same_digest_is_pending(self):
        rows=self.records()
        rows["results"].append({
            "name":"1215-2026-11-06-d00dd00","digest":DIGEST})
        with self.assertRaisesRegex(
                pin.SimCImageRevisionPending,
                "SIMC_IMAGE_MATCHING_TAG_REVISION"):
            pin.select_from_tags(document=rows,image_ref=REF,
                                 game_build=BUILD)

    def test_http_error_is_pending_without_untrusted_fallback(self):
        class Fail(Response):status=503
        with self.assertRaisesRegex(
                pin.SimCImageRevisionPending,"HTTP_STATUS_NOT_SUCCESS"):
            pin.discover(image_ref=REF,game_build=BUILD,
                         fetch=lambda *_args,**_kw:Fail(b"{}"))
        with self.assertRaisesRegex(
                pin.SimCImageRevisionPending,"SOURCE_NOT_AVAILABLE"):
            pin.discover(image_ref=REF,game_build=BUILD,
                         fetch=lambda *_args,**_kw:Response(b"not-json"))


if __name__=="__main__":
    unittest.main()
