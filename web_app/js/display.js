/**
 * display.js - 문제 번호 표시 로직
 */

/**
 * KMO 출처 파싱
 * 입력: "제38회(2024) KMO 중등부 1차 4번"
 * 출력: { round: "38", year: "2024", number: "4" }
 */
function parseKMOSource(source) {
    if (!source) return null;

    const pattern = /제?(\d+)회\((\d{4})\)\s*KMO\s*중등부\s*1차\s*(\d+)번/;
    const match = source.match(pattern);

    if (match) {
        return {
            round: match[1],
            year: match[2],
            number: match[3]
        };
    }

    return null;
}

/**
 * 미분류 문제 일련번호 매핑 생성
 * 출력: { "002": "001", "004": "002", ... }
 */
function buildUnclassifiedNumberMap(allProblems) {
    const unclassifiedProblems = allProblems
        .filter(p => !p.source || p.source.trim() === '')
        .sort((a, b) => parseInt(a.id) - parseInt(b.id));

    const map = {};
    unclassifiedProblems.forEach((problem, index) => {
        const serialNumber = String(index + 1).padStart(3, '0');
        map[problem.id] = serialNumber;
    });

    return map;
}

/**
 * 문제 표시 번호 생성
 */
function getProblemDisplayNumber(problem, unclassifiedMap = null) {
    const source = problem.source || '';

    // 1. KMO 중등부 1차
    const kmoData = parseKMOSource(source);
    if (kmoData) {
        return `${kmoData.round}회(${kmoData.year}) ${kmoData.number}번`;
    }

    // 2. 출처 미분류
    if (!source.trim()) {
        if (unclassifiedMap && unclassifiedMap[problem.id]) {
            return unclassifiedMap[problem.id];
        }
        return problem.id;
    }

    // 3. 기타 출처
    return source;
}

/**
 * 미리보기 텍스트 (사이드바용)
 */
function getProblemPreview(problem, unclassifiedMap = null) {
    const source = problem.source || '';

    const kmoData = parseKMOSource(source);
    if (kmoData) {
        return `${kmoData.round}회(${kmoData.year}) ${kmoData.number}번`;
    }

    if (!source.trim()) {
        if (unclassifiedMap && unclassifiedMap[problem.id]) {
            return unclassifiedMap[problem.id];
        }
        return problem.id;
    }

    return source.length > 30 ? source.substring(0, 30) + '...' : source;
}
