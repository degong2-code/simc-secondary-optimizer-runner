#!/usr/bin/env python3
"""v036 read-only admission gate for the *original* v032 adaptive source archive.

This is NOT an optimizer, a native SimC test or v032 code reconstruction.
No extracted executable code is imported or executed here.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import stat
import sys
import zipfile

EXPECTED_ARCHIVE = 'SIMC_SECONDARY_OPTIMIZER_OMNIUM_ADAPTIVE_v032.zip'
EXPECTED_SOURCE = 'SIMC_OMNIUM_CHMV_ADAPTIVE_v032.py'
MAX_ENTRIES = 1000
MAX_FILE_BYTES = 50 * 1024 * 1024
MAX_TOTAL_BYTES = 200 * 1024 * 1024
SENSITIVE_NAMES = frozenset({'.env', '.env.local', '.env.production', 'id_rsa', 'id_ed25519', 'credentials.json', 'token.json'})
ALLOWED_SUFFIXES = frozenset({'.py', '.md', '.txt', '.json', '.ps1', '.bat', '.simc', '.zip', '.csv', '.yml', '.yaml', '.sha256', '.ini', '.toml', '.cfg', '.log', '.html', '.xml', '.tsv', '.jsonl'})


class GateRejected(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def digest_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def normalize_zip_path(name: str) -> str:
    if not name or '\\' in name or '\x00' in name or name.startswith('/'):
        raise GateRejected('UNSAFE_ARCHIVE_PATH')
    components = name.rstrip('/').split('/')
    if any(x in ('', '.', '..') for x in components) or re.match(r'^[A-Za-z]:', name):
        raise GateRejected('UNSAFE_ARCHIVE_PATH')
    return '/'.join(components)


def inspect(archive: pathlib.Path, expected_sha256: str | None = None) -> dict:
    """Check archive shape and identity; never execute code in the candidate.

    Returns SOURCE_CANDIDATE_INSPECTED (not VERIFIED_V032). An expected SHA
    authenticates the exact bytes only if supplied from trusted provenance.
    """
    if archive.name != EXPECTED_ARCHIVE:
        raise GateRejected('UNEXPECTED_ARCHIVE_BASENAME')
    if not archive.is_file():
        raise GateRejected('SOURCE_PACKAGE_REQUIRED')
    if archive.stat().st_size > MAX_TOTAL_BYTES:
        raise GateRejected('ARCHIVE_TOO_LARGE')
    archive_sha = digest_file(archive)
    if expected_sha256 is not None:
        if not re.fullmatch(r'[a-f0-9]{64}', expected_sha256):
            raise GateRejected('BAD_EXPECTED_SHA256')
        if archive_sha != expected_sha256:
            raise GateRejected('SOURCE_SHA256_MISMATCH')
    try:
        with zipfile.ZipFile(archive) as z:
            infos = z.infolist()
            if len(infos) == 0 or len(infos) > MAX_ENTRIES:
                raise GateRejected('INVALID_ARCHIVE_ENTRY_COUNT')
            total = 0
            seen = set()
            sources = []
            files = []
            for info in infos:
                name = normalize_zip_path(info.filename)
                key = name.casefold()
                if key in seen:
                    raise GateRejected('DUPLICATE_NORMALIZED_ARCHIVE_PATH')
                seen.add(key)
                mode = info.external_attr >> 16
                if stat.S_ISLNK(mode) or (mode and stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR)):
                    raise GateRejected('UNSAFE_ARCHIVE_ENTRY_TYPE')
                if info.flag_bits & 0x1:
                    raise GateRejected('ENCRYPTED_ARCHIVE_ENTRY')
                if info.is_dir():
                    continue
                if info.file_size > MAX_FILE_BYTES:
                    raise GateRejected('OVERSIZED_ARCHIVE_ENTRY')
                total += info.file_size
                if total > MAX_TOTAL_BYTES:
                    raise GateRejected('EXCESSIVE_UNCOMPRESSED_SIZE')
                leaf = pathlib.PurePosixPath(name).name
                if leaf.lower() in SENSITIVE_NAMES or leaf.lower().startswith('.env.') or leaf.endswith(('.pem', '.key', '.p12', '.pfx')):
                    raise GateRejected('SENSITIVE_FILENAME_PRESENT')
                if pathlib.PurePosixPath(name).suffix.lower() not in ALLOWED_SUFFIXES and leaf not in ('.gitignore', 'MANIFEST'):
                    raise GateRejected('UNEXPECTED_FILE_EXTENSION')
                # Integrity checking streams bytes, but never writes/extracts candidate files.
                h = hashlib.sha256()
                with z.open(info) as f:
                    for block in iter(lambda: f.read(65536), b''):
                        h.update(block)
                entry = {'path': name, 'size_bytes': info.file_size, 'sha256': h.hexdigest()}
                files.append(entry)
                if leaf == EXPECTED_SOURCE:
                    sources.append(entry)
            if len(sources) != 1:
                raise GateRejected('V032_ORIGINAL_ENGINE_ENTRY_NOT_UNIQUE')
    except (zipfile.BadZipFile, EOFError, RuntimeError, OSError) as e:
        raise GateRejected('INVALID_ZIP_OR_CORRUPT_MEMBER') from e
    return {
        'schema': 'v036_source_admission_v1',
        'status': 'SOURCE_CANDIDATE_INSPECTED',
        'native_simc_run': False,
        'v032_regression_run': False,
        'v032_code_executed': False,
        'v032_identity_proven': False,  # Shape and hash are necessary, never sufficient.
        'expected_hash_provided': expected_sha256 is not None,
        'archive_name': archive.name,
        'archive_sha256': archive_sha,
        'archive_size_bytes': archive.stat().st_size,
        'file_count': len(files),
        'uncompressed_bytes': total,
        'engine_entry': sources[0],
        'file_manifest': files,
        'next_gate': 'INDEPENDENT_SOURCE_REVIEW_AND_V032_REGRESSION',
    }


def write_receipt(output: pathlib.Path, result: dict) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + '\n', encoding='utf-8')


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=pathlib.Path, default=pathlib.Path('_incoming_v032') / EXPECTED_ARCHIVE)
    parser.add_argument('--expected-sha256', type=str, default=None)
    parser.add_argument('--receipt', type=pathlib.Path, default=pathlib.Path('run-output') / 'V036_SOURCE_ADMISSION.json')
    args = parser.parse_args(argv)
    try:
        record = inspect(args.source, args.expected_sha256)
        code = 0
    except GateRejected as e:
        record = {'schema': 'v036_source_admission_v1', 'status': 'BLOCKED', 'reason': e.code,
                  'native_simc_run': False, 'v032_regression_run': False,
                  'v032_code_executed': False, 'v032_identity_proven': False}
        code = 3
    record['evaluated_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    write_receipt(args.receipt, record)
    print(record['status'], record.get('reason', record.get('archive_sha256', '')))
    return code


if __name__ == '__main__':
    raise SystemExit(run())
