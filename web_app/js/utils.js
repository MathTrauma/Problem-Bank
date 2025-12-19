/**
 * utils.js - 유틸리티 함수
 */

// solution에서 SVG 마커 추출하여 폴드아웃 버튼 HTML 생성
function extractSvgButtons(solution) {
    if (!solution) return '';

    const svgMarkers = [];
    const regex = /%\s*\[SVG:\s*([^\]]+)\]/g;
    let match;

    while ((match = regex.exec(solution)) !== null) {
        svgMarkers.push(match[1].trim());
    }

    if (svgMarkers.length === 0) return '';

    let buttonsHtml = '';
    svgMarkers.forEach((filename, index) => {
        const svgPath = `data/svg/${filename}`;
        const label = svgMarkers.length > 1 ? `그림 ${index + 1} 보기` : '그림 보기';
        buttonsHtml += `
            <div class="figure-toggle" data-svg="${svgPath}">
                <div class="figure-toggle-icon">
                    <svg viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z"/>
                    </svg>
                </div>
                <span class="figure-toggle-text">${label}</span>
            </div>
            <div class="figure-content">
                <img src="${svgPath}" alt="그림" loading="lazy">
            </div>
        `;
    });

    return buttonsHtml;
}

// LaTeX를 HTML로 변환 (수식 보호)
function convertLatexToHtml(latex) {
    if (!latex) return '';

    let html = latex;

    // 1. 수식을 임시로 보호 (치환)
    const mathPlaceholders = [];
    let mathIndex = 0;

    // Display math $$...$$ 보호
    html = html.replace(/\$\$([\s\S]*?)\$\$/g, (match) => {
        const placeholder = `___DISPLAYMATH_${mathIndex}___`;
        mathPlaceholders.push({ placeholder, content: match });
        mathIndex++;
        return placeholder;
    });

    // Inline math $...$ 보호
    html = html.replace(/\$([^\$]+?)\$/g, (match) => {
        const placeholder = `___INLINEMATH_${mathIndex}___`;
        mathPlaceholders.push({ placeholder, content: match });
        mathIndex++;
        return placeholder;
    });

    // 2. LaTeX 명령어 처리
    // \numbering 제거
    html = html.replace(/\\numbering\s*/g, '<strong>문제.</strong> ');

    // 환경 변환
    html = html.replace(/\\begin\{problem\}/g, '<div class="problem-box">');
    html = html.replace(/\\end\{problem\}/g, '</div>');
    html = html.replace(/\\begin\{center\}/g, '<div style="text-align:center;">');
    html = html.replace(/\\end\{center\}/g, '</div>');
    html = html.replace(/\\begin\{figure\}(\[.*?\])?/g, '<div class="figure">');
    html = html.replace(/\\end\{figure\}/g, '</div>');

    // 줄바꿈 (문장 끝의 \\만 변환)
    html = html.replace(/\\\\(?=\s*$)/gm, '<br>');
    html = html.replace(/\\\\(?=\s*\n)/g, '<br>');
    html = html.replace(/\\newline/g, '<br>');

    // \vfill, \vspace 등 제거
    html = html.replace(/\\vfill/g, '');
    html = html.replace(/\\vspace\{[^}]*\}/g, '');
    html = html.replace(/\\hspace\{[^}]*\}/g, '');

    // 단락 구분
    html = html.replace(/\n\n+/g, '</p><p>');

    // 3. 수식 복원
    mathPlaceholders.forEach(({ placeholder, content }) => {
        html = html.replace(placeholder, content);
    });

    // 4. 마침표 다음 줄바꿈을 <br>로 변환
    html = html.replace(/\.\s*\n\s*([가-힣A-Za-z0-9$])/g, '.<br>$1');

    // 5. 수식 뒤에 공백 추가 (수식 바로 뒤 한글/영문이 오면)
    html = html.replace(/(\$[^\$]+?\$)([가-힣a-zA-Z])/g, '$1 $2');
    html = html.replace(/(\$\$[^\$]+?\$\$)([가-힣a-zA-Z])/g, '$1 $2');

    // 6. 단락으로 감싸기
    if (!html.startsWith('<div') && !html.startsWith('<p')) {
        html = '<p>' + html + '</p>';
    }

    // 빈 단락 제거
    html = html.replace(/<p>\s*<\/p>/g, '');

    // 7. SVG 마커를 폴드아웃 버튼으로 변환
    html = html.replace(/%\s*\[SVG:\s*([^\]]+)\]/g, (match, filename) => {
        const svgPath = `data/svg/${filename.trim()}`;
        return `
            <div class="figure-toggle" data-svg="${svgPath}">
                <div class="figure-toggle-icon">
                    <svg viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z"/>
                    </svg>
                </div>
                <span class="figure-toggle-text">그림 보기</span>
            </div>
            <div class="figure-content">
                <img src="${svgPath}" alt="그림" loading="lazy">
            </div>
        `;
    });

    return html;
}

// 폴드아웃 버튼 이벤트 설정
function setupFigureToggles() {
    document.querySelectorAll('.figure-toggle').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const content = this.nextElementSibling;
            const isExpanded = content.classList.contains('show');

            if (isExpanded) {
                content.classList.remove('show');
                this.classList.remove('expanded');
                this.querySelector('.figure-toggle-text').textContent = '그림 보기';
            } else {
                content.classList.add('show');
                this.classList.add('expanded');
                this.querySelector('.figure-toggle-text').textContent = '그림 숨기기';
            }
        });
    });
}

// 토스트 알림
function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
