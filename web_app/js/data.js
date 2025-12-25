/**
 * data.js - 데이터 로드 및 분류
 */

// Cloudflare Workers CDN URL
const CDN_URL = 'https://r2-cdn.painfultrauma.workers.dev';

// 문제 메타데이터 로드 (R2 CDN)
async function loadProblems() {
    try {
        const response = await fetch(`${CDN_URL}/metadata.json`);
        const data = await response.json();

        App.allProblems = data.problems;

        // 빠른 조회를 위한 맵 생성 (메타데이터만)
        App.problemsData = {};
        App.allProblems.forEach(p => {
            App.problemsData[p.id] = p;
        });

        // 미분류 번호 매핑 생성
        App.unclassifiedNumberMap = buildUnclassifiedNumberMap(App.allProblems);

        updateStats(data);
        renderProblemList(App.allProblems);
    } catch (error) {
        console.error('Failed to load problems:', error);
        showToast('문제 목록을 불러오는데 실패했습니다.');
    }
}

// 개별 문제 상세 정보 로드 (필요할 때만)
async function loadProblemDetail(problemId) {
    try {
        // 이미 로드된 경우 스킵
        if (App.problemsData[problemId]?.content !== undefined) {
            return App.problemsData[problemId];
        }

        const response = await fetch(`${CDN_URL}/problems/${problemId}.json`);
        const problemData = await response.json();

        // 캐시에 저장
        App.problemsData[problemId] = {
            ...App.problemsData[problemId],
            ...problemData
        };

        return App.problemsData[problemId];
    } catch (error) {
        console.error(`Failed to load problem ${problemId}:`, error);
        showToast('문제를 불러오는데 실패했습니다.');
        return null;
    }
}

// 문제 분류 함수
function classifyProblem(problem) {
    const source = problem.source || '';

    // KMO 중등부 1차: Extract year from "제38회(2024) KMO 중등부 1차 N번" or "38회(2024) KMO 중등부 1차 N번"
    const kmoMatch = source.match(/제?(\d+)회\((\d{4})\)\s*KMO\s*중등부\s*1차/);
    if (kmoMatch) {
        return { category: 'kmo_middle_1', year: kmoMatch[2], problem };
    }

    // Empty source
    if (!source.trim()) {
        return { category: 'no_source', year: null, problem };
    }

    // Everything else
    return { category: 'other', year: null, problem };
}

// 계층 구조 빌더
function buildHierarchy(problems) {
    const hierarchy = {
        kmo_middle_1: { label: 'KMO 중등부 1차', folders: {}, count: 0 },
        no_source: { label: '출처 미분류', problems: [], count: 0 },
        other: { label: '기타 문제', problems: [], count: 0 }
    };

    problems.forEach(problem => {
        const { category, year } = classifyProblem(problem);

        if (category === 'kmo_middle_1') {
            if (!hierarchy.kmo_middle_1.folders[year]) {
                hierarchy.kmo_middle_1.folders[year] = {
                    label: year,
                    problems: [],
                    count: 0
                };
            }
            hierarchy.kmo_middle_1.folders[year].problems.push(problem);
            hierarchy.kmo_middle_1.folders[year].count++;
            hierarchy.kmo_middle_1.count++;
        } else {
            hierarchy[category].problems.push(problem);
            hierarchy[category].count++;
        }
    });

    // Sort years descending (2025 → 2010)
    const sortedYears = Object.keys(hierarchy.kmo_middle_1.folders).sort((a, b) => b - a);
    const sortedFolders = {};
    sortedYears.forEach(year => {
        sortedFolders[year] = hierarchy.kmo_middle_1.folders[year];
    });
    hierarchy.kmo_middle_1.folders = sortedFolders;

    return hierarchy;
}

// 통계 업데이트
function updateStats(data) {
    const total = data.total_problems;
    const withSolution = App.allProblems.filter(p => p.solution).length;
    const completionRate = total > 0 ? Math.round(withSolution / total * 100) : 0;

    document.getElementById('stats').textContent =
        `전체: ${total} | 풀이: ${withSolution} | 완료율: ${completionRate}%`;
}
