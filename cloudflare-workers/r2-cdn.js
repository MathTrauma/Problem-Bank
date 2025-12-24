/**
 * Cloudflare Workers R2 CDN
 *
 * R2 버킷을 CDN처럼 제공하는 간단한 프록시
 * 기능: MIME 타입, CORS, 캐싱
 */

// MIME 타입 매핑
const MIME_TYPES = {
  '.json': 'application/json',
  '.svg': 'image/svg+xml',
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.txt': 'text/plain',
};

// 파일 확장자에서 MIME 타입 가져오기
function getMimeType(path) {
  const ext = path.substring(path.lastIndexOf('.')).toLowerCase();
  return MIME_TYPES[ext] || 'application/octet-stream';
}

// CORS 헤더
const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Max-Age': '86400',
};

export default {
  async fetch(request, env) {
    // OPTIONS 요청 처리 (CORS preflight)
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: CORS_HEADERS,
      });
    }

    // GET, HEAD만 허용
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    try {
      // URL에서 경로 추출 (앞의 / 제거)
      const url = new URL(request.url);
      const key = url.pathname.slice(1);

      // 빈 경로 처리
      if (!key) {
        return new Response('Use: /metadata.json, /problems/{id}.json, /svg/{file}.svg', {
          status: 200,
          headers: { 'Content-Type': 'text/plain', ...CORS_HEADERS },
        });
      }

      // R2에서 파일 가져오기
      const object = await env.R2_BUCKET.get(key);

      // 파일 없음
      if (!object) {
        return new Response('Not Found', {
          status: 404,
          headers: { 'Content-Type': 'text/plain', ...CORS_HEADERS },
        });
      }

      // MIME 타입 결정
      const contentType = getMimeType(key);

      // 응답 헤더 설정
      const headers = {
        'Content-Type': contentType,
        'Cache-Control': 'public, max-age=3600', // 1시간 캐싱
        'ETag': object.httpEtag,
        ...CORS_HEADERS,
      };

      // HEAD 요청은 body 없이 헤더만
      if (request.method === 'HEAD') {
        return new Response(null, {
          status: 200,
          headers,
        });
      }

      // 정상 응답
      return new Response(object.body, {
        status: 200,
        headers,
      });

    } catch (error) {
      // 서버 오류
      console.error('R2 CDN Error:', error);
      return new Response('Internal Server Error', {
        status: 500,
        headers: { 'Content-Type': 'text/plain', ...CORS_HEADERS },
      });
    }
  },
};
