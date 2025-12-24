# Cloudflare Workers R2 CDN

R2 버킷을 Public CDN처럼 제공하는 Workers 스크립트

## 파일 구조

```
cloudflare-workers/
├── r2-cdn.js        # Workers 스크립트 (~100줄)
├── wrangler.toml    # Workers 설정
└── README.md        # 이 파일
```

## 배포 방법

### 1. Wrangler CLI 설치 (한 번만)

```bash
npm install -g wrangler
```

### 2. Cloudflare 로그인

```bash
wrangler login
```

브라우저가 열리면 Cloudflare 계정으로 로그인

### 3. Workers 배포

```bash
cd cloudflare-workers
wrangler deploy
```

### 4. 배포 완료!

배포가 성공하면 다음과 같은 URL을 받게 됩니다:

```
https://r2-cdn.<your-subdomain>.workers.dev
```

## 사용 방법

### 파일 접근

```
https://r2-cdn.<subdomain>.workers.dev/metadata.json
https://r2-cdn.<subdomain>.workers.dev/problems/001.json
https://r2-cdn.<subdomain>.workers.dev/svg/001_fig1.svg
```

### 테스트

```bash
curl https://r2-cdn.<subdomain>.workers.dev/metadata.json
```

## 기능

✅ **자동 MIME 타입** - JSON, SVG 등 자동 인식
✅ **CORS 지원** - 웹앱에서 접근 가능
✅ **브라우저 캐싱** - Cache-Control 헤더 (1시간)
✅ **에러 처리** - 404, 500 적절히 처리
✅ **HEAD 요청** - 메타데이터만 조회 가능

## 무료 티어 제한

- 하루 10만 요청
- 월 10만 요청 (Free plan)
- 이 프로젝트에는 충분함

## 다음 단계

1. Workers 배포 후 URL 확인
2. 웹앱 `web_app/js/data.js`에서 CDN URL로 변경
3. 웹앱 재배포
