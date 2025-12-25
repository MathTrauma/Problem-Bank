#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R2 증분 업로드 스크립트

dist/ 디렉토리의 파일들을 Cloudflare R2에 업로드
변경된 파일만 업로드 (파일 해시 기반)

환경변수 필요:
    export R2_ACCOUNT_ID="your_account_id"
    export R2_BUCKET_NAME="your_bucket_name"
    export R2_ACCESS_KEY_ID="your_access_key"
    export R2_SECRET_ACCESS_KEY="your_secret_key"

사용법:
    python3 upload_to_r2.py              # 증분 업로드
    python3 upload_to_r2.py --dry-run    # 시뮬레이션 (업로드 안 함)
    python3 upload_to_r2.py --force      # 강제 전체 업로드
"""

import argparse
import hashlib
import json
import os
import sys
import boto3
from pathlib import Path
from botocore.exceptions import ClientError

# R2 설정 (환경변수에서 읽기)
ACCOUNT_ID = os.getenv('R2_ACCOUNT_ID')
BUCKET_NAME = os.getenv('R2_BUCKET_NAME')

if not ACCOUNT_ID or not BUCKET_NAME:
    print("❌ R2 설정이 누락되었습니다.")
    print("\n다음 환경변수를 설정하세요:")
    print("  export R2_ACCOUNT_ID='your_account_id'")
    print("  export R2_BUCKET_NAME='your_bucket_name'")
    print("  export R2_ACCESS_KEY_ID='your_access_key'")
    print("  export R2_SECRET_ACCESS_KEY='your_secret_key'")
    sys.exit(1)

ENDPOINT_URL = f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com"

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
DIST_DIR = BASE_DIR / "dist"
UPLOAD_CACHE_FILE = BASE_DIR / ".upload_cache.json"


def compute_file_hash(filepath: Path) -> str:
    """파일의 SHA256 해시 계산"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_upload_cache() -> dict:
    """업로드 캐시 로드"""
    if UPLOAD_CACHE_FILE.exists():
        with open(UPLOAD_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_upload_cache(cache: dict):
    """업로드 캐시 저장"""
    with open(UPLOAD_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)


def get_r2_client():
    """R2 클라이언트 생성"""
    access_key = os.getenv('R2_ACCESS_KEY_ID')
    secret_key = os.getenv('R2_SECRET_ACCESS_KEY')

    if not access_key or not secret_key:
        print("❌ R2 환경변수가 설정되지 않았습니다.")
        print("\n다음 명령어로 설정하세요:")
        print("  export R2_ACCESS_KEY_ID='your_access_key'")
        print("  export R2_SECRET_ACCESS_KEY='your_secret_key'")
        return None

    try:
        client = boto3.client(
            's3',
            endpoint_url=ENDPOINT_URL,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='auto'
        )
        return client
    except Exception as e:
        print(f"❌ R2 클라이언트 생성 실패: {e}")
        return None


def get_content_type(filepath: Path) -> str:
    """파일 확장자에 따른 Content-Type 반환"""
    ext = filepath.suffix.lower()
    content_types = {
        '.json': 'application/json',
        '.svg': 'image/svg+xml',
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
    }
    return content_types.get(ext, 'application/octet-stream')


def upload_file(client, local_path: Path, r2_key: str, dry_run: bool = False) -> bool:
    """단일 파일 R2 업로드"""
    if dry_run:
        print(f"  [DRY-RUN] {r2_key}")
        return True

    try:
        content_type = get_content_type(local_path)

        with open(local_path, 'rb') as f:
            client.put_object(
                Bucket=BUCKET_NAME,
                Key=r2_key,
                Body=f,
                ContentType=content_type,
                CacheControl='public, max-age=3600'  # 1시간 캐시
            )

        size_kb = local_path.stat().st_size / 1024
        print(f"  ✅ {r2_key} ({size_kb:.1f} KB)")
        return True

    except ClientError as e:
        print(f"  ❌ {r2_key}: {e}")
        return False


def collect_files_to_upload(force: bool = False) -> list:
    """업로드할 파일 목록 수집 (증분)"""
    if not DIST_DIR.exists():
        print(f"❌ dist/ 디렉토리가 없습니다: {DIST_DIR}")
        print("   먼저 build_incremental.py를 실행하세요.")
        return []

    cache = {} if force else load_upload_cache()
    files_to_upload = []

    # dist/ 하위 모든 파일 스캔
    for filepath in DIST_DIR.rglob('*'):
        if not filepath.is_file():
            continue

        # R2 키 생성 (dist/ 이후 경로)
        r2_key = str(filepath.relative_to(DIST_DIR))

        # 파일 해시 계산
        file_hash = compute_file_hash(filepath)

        # 캐시 확인
        cache_key = r2_key
        if not force and cache.get(cache_key) == file_hash:
            continue  # 변경 없음, 스킵

        files_to_upload.append({
            'local_path': filepath,
            'r2_key': r2_key,
            'hash': file_hash,
            'size': filepath.stat().st_size
        })

    return files_to_upload


def upload_all(dry_run: bool = False, force: bool = False):
    """전체 업로드 프로세스"""
    print("=" * 70)
    print("R2 증분 업로드")
    print("=" * 70)
    print(f"Account ID: {ACCOUNT_ID}")
    print(f"Bucket: {BUCKET_NAME}")
    print(f"모드: {'시뮬레이션' if dry_run else '업로드'}")
    print(f"강제: {'예' if force else '아니오'}")
    print("=" * 70)

    # R2 클라이언트 생성
    client = get_r2_client()
    if not client and not dry_run:
        return

    # 업로드할 파일 수집
    print(f"\n📁 파일 스캔 중...")
    files_to_upload = collect_files_to_upload(force=force)

    if not files_to_upload:
        print("✅ 업로드할 파일이 없습니다 (모든 파일이 최신 상태)")
        return

    # 파일 크기 합계
    total_size = sum(f['size'] for f in files_to_upload) / 1024 / 1024
    print(f"📊 업로드 대상: {len(files_to_upload)}개 파일 ({total_size:.2f} MB)")

    # 카테고리별 분류
    by_type = {}
    for f in files_to_upload:
        ext = Path(f['r2_key']).suffix
        by_type.setdefault(ext, []).append(f)

    print("\n파일 유형별:")
    for ext, items in sorted(by_type.items()):
        count = len(items)
        size_mb = sum(i['size'] for i in items) / 1024 / 1024
        print(f"  {ext or '(없음)'}: {count}개 ({size_mb:.2f} MB)")

    # 업로드 실행
    print(f"\n{'=' * 70}")
    print("업로드 시작...")
    print("=" * 70)

    cache = load_upload_cache()
    success_count = 0
    fail_count = 0

    for file_info in files_to_upload:
        local_path = file_info['local_path']
        r2_key = file_info['r2_key']
        file_hash = file_info['hash']

        if upload_file(client, local_path, r2_key, dry_run=dry_run):
            success_count += 1
            if not dry_run:
                cache[r2_key] = file_hash
        else:
            fail_count += 1

    # 캐시 저장
    if not dry_run:
        save_upload_cache(cache)

    # 결과 출력
    print("\n" + "=" * 70)
    if dry_run:
        print(f"✅ 시뮬레이션 완료!")
        print(f"  업로드 예정: {success_count}개")
    else:
        print(f"✅ 업로드 완료!")
        print(f"  성공: {success_count}개")
        print(f"  실패: {fail_count}개")
        print(f"\nR2 버킷: https://pub-{ACCOUNT_ID}.r2.dev/")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description='R2 증분 업로드 스크립트',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--dry-run', action='store_true',
                        help='시뮬레이션 모드 (실제 업로드 안 함)')
    parser.add_argument('--force', action='store_true',
                        help='강제 전체 업로드 (캐시 무시)')

    args = parser.parse_args()

    upload_all(dry_run=args.dry_run, force=args.force)


if __name__ == '__main__':
    main()
