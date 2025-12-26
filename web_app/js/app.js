/**
 * app.js - 메인 앱 초기화 및 상태 관리
 */

// 전역 앱 상태
const App = {
    currentProblemId: null,
    allProblems: [],
    problemsData: {},
    problemHierarchy: null,
    expandedFolders: new Set(),
    currentFilteredProblems: null,
    unclassifiedNumberMap: null
};

// 초기화
window.addEventListener('DOMContentLoaded', () => {
    loadProblems();
    setupTabs();
    setupSearch();
    setupMobileMenu();
});

// 폴더 상태 관리
function toggleFolder(folderId) {
    if (App.expandedFolders.has(folderId)) {
        App.expandedFolders.delete(folderId);
    } else {
        App.expandedFolders.add(folderId);
    }
    if (!App.currentFilteredProblems) {
        renderProblemList(App.allProblems);
    }
}

function isFolderExpanded(folderId) {
    return App.expandedFolders.has(folderId);
}

// 문제 선택
function selectProblem(problemId) {
    App.currentProblemId = problemId;

    // 목록에서 선택 표시
    document.querySelectorAll('.problem-item').forEach(item => {
        item.classList.remove('active');
        const idText = item.querySelector('.problem-id')?.textContent;
        if (idText && idText.includes(problemId)) {
            item.classList.add('active');
        }
    });

    loadProblem(problemId);
}

// 탭 설정
function setupTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;

            // 탭 활성화
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // 콘텐츠 표시
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`tab-${tabName}`).classList.add('active');
        });
    });
}

// 검색 설정
function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();

        if (query.trim() === '') {
            // Clear search mode
            App.currentFilteredProblems = null;
            renderProblemList(App.allProblems);
            return;
        }

        // Filter problems
        const filtered = App.allProblems.filter(p => {
            const displayNumber = getProblemDisplayNumber(p, App.unclassifiedNumberMap);

            return p.id.includes(query) ||
                   displayNumber.toLowerCase().includes(query) ||
                   (p.source && p.source.toLowerCase().includes(query)) ||
                   (p.source_file && p.source_file.toLowerCase().includes(query)) ||
                   (p.tags && p.tags.some(tag => tag.toLowerCase().includes(query)));
        });

        // Enter search mode
        App.currentFilteredProblems = filtered;
        renderProblemList(filtered);
    });
}

// 모바일 메뉴 설정
function setupMobileMenu() {
    const menuToggle = document.getElementById('mobileMenuToggle');
    const overlay = document.getElementById('mobileOverlay');
    const sidebar = document.querySelector('.sidebar');

    if (!menuToggle || !overlay || !sidebar) return;

    // 메뉴 열기/닫기 함수
    function openMenu() {
        sidebar.classList.add('mobile-open');
        overlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
        sidebar.classList.remove('mobile-open');
        overlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    // 햄버거 버튼 클릭
    menuToggle.addEventListener('click', () => {
        if (sidebar.classList.contains('mobile-open')) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    // 오버레이 클릭 시 메뉴 닫기
    overlay.addEventListener('click', closeMenu);

    // 문제 선택 시 모바일에서 메뉴 자동 닫기
    const originalSelectProblem = window.selectProblem;
    window.selectProblem = function(problemId) {
        if (originalSelectProblem) {
            originalSelectProblem(problemId);
        }
        // 모바일에서만 메뉴 닫기 (768px 이하)
        if (window.innerWidth <= 768) {
            closeMenu();
        }
    };
}
