/**
 * render.js - UI 렌더링
 */

// 문제 목록 렌더링
function renderProblemList(problems) {
    const listContainer = document.getElementById('problemList');
    listContainer.innerHTML = '';

    if (!App.currentFilteredProblems) {
        // Normal mode: hierarchical view
        App.problemHierarchy = buildHierarchy(problems);
        renderHierarchy(listContainer, App.problemHierarchy);
    } else {
        // Search mode: grouped flat list
        renderSearchResults(listContainer, problems);
    }
}

function renderHierarchy(container, hierarchy) {
    // Render KMO category with year sub-folders
    if (hierarchy.kmo_middle_1.count > 0) {
        renderCategoryFolder(container, 'kmo_middle_1', hierarchy.kmo_middle_1, true);
    }

    // Render 출처 미분류
    if (hierarchy.no_source.count > 0) {
        renderCategoryFolder(container, 'no_source', hierarchy.no_source, false);
    }

    // Render 기타 문제
    if (hierarchy.other.count > 0) {
        renderCategoryFolder(container, 'other', hierarchy.other, false);
    }
}

function renderCategoryFolder(container, categoryId, category, hasSubFolders) {
    const isExpanded = isFolderExpanded(categoryId);

    const folderDiv = document.createElement('div');
    folderDiv.className = 'folder-item category-folder';
    folderDiv.innerHTML = `
        <div class="folder-header" data-folder-id="${categoryId}">
            <span class="folder-icon ${isExpanded ? 'expanded' : ''}">${isExpanded ? '▼' : '▶'}</span>
            <span class="folder-label">${category.label}</span>
            <span class="folder-count">(${category.count})</span>
        </div>
    `;

    folderDiv.querySelector('.folder-header').onclick = (e) => {
        e.stopPropagation();
        toggleFolder(categoryId);
        renderProblemList(App.allProblems);
    };

    container.appendChild(folderDiv);

    if (isExpanded) {
        const contentDiv = document.createElement('div');
        contentDiv.className = 'folder-content';

        if (hasSubFolders) {
            // Render year folders (최신 연도 먼저)
            Object.keys(category.folders).sort((a, b) => b - a).forEach(year => {
                renderYearFolder(contentDiv, categoryId, year, category.folders[year]);
            });
        } else {
            // Render problems directly
            category.problems.forEach(problem => {
                renderProblemItem(contentDiv, problem, 1);
            });
        }

        container.appendChild(contentDiv);
    }
}

function renderYearFolder(container, parentId, year, yearData) {
    const folderId = `${parentId}_${year}`;
    const isExpanded = isFolderExpanded(folderId);

    const folderDiv = document.createElement('div');
    folderDiv.className = 'folder-item year-folder';
    folderDiv.innerHTML = `
        <div class="folder-header" data-folder-id="${folderId}">
            <span class="folder-icon ${isExpanded ? 'expanded' : ''}">${isExpanded ? '▼' : '▶'}</span>
            <span class="folder-label">${year}</span>
            <span class="folder-count">(${yearData.count})</span>
        </div>
    `;

    folderDiv.querySelector('.folder-header').onclick = (e) => {
        e.stopPropagation();
        toggleFolder(folderId);
        renderProblemList(App.allProblems);
    };

    container.appendChild(folderDiv);

    if (isExpanded) {
        const contentDiv = document.createElement('div');
        contentDiv.className = 'folder-content';

        yearData.problems.forEach(problem => {
            renderProblemItem(contentDiv, problem, 2);
        });

        container.appendChild(contentDiv);
    }
}

function renderProblemItem(container, problem, indentLevel) {
    const item = document.createElement('div');
    item.className = 'problem-item';
    item.style.paddingLeft = `${15 + (indentLevel * 20)}px`;

    if (App.currentProblemId === problem.id) {
        item.classList.add('active');
    }

    item.onclick = () => selectProblem(problem.id);

    let badges = '';
    if (problem.has_tikz) badges += '<span class="badge badge-tikz">TikZ</span>';
    if (problem.solution) badges += '<span class="badge badge-solution">풀이</span>';
    if (problem.source) badges += '<span class="badge badge-source">출처</span>';

    item.innerHTML = `
        <div class="problem-id">문제 ${problem.id}</div>
        <div class="problem-preview">${problem.source || problem.source_file || '원본 파일 없음'}</div>
        <div class="problem-badges">${badges}</div>
    `;

    container.appendChild(item);
}

function renderSearchResults(container, problems) {
    const classified = buildHierarchy(problems);

    // KMO problems
    if (classified.kmo_middle_1.count > 0) {
        const categoryHeader = document.createElement('div');
        categoryHeader.className = 'search-category-header';
        categoryHeader.textContent = `${classified.kmo_middle_1.label} (${classified.kmo_middle_1.count})`;
        container.appendChild(categoryHeader);

        Object.keys(classified.kmo_middle_1.folders).sort((a, b) => b - a).forEach(year => {
            const yearFolder = classified.kmo_middle_1.folders[year];
            const yearHeader = document.createElement('div');
            yearHeader.className = 'search-year-header';
            yearHeader.textContent = `${year} (${yearFolder.count})`;
            container.appendChild(yearHeader);

            yearFolder.problems.forEach(problem => {
                renderProblemItem(container, problem, 2);
            });
        });
    }

    // No source problems
    if (classified.no_source.count > 0) {
        const categoryHeader = document.createElement('div');
        categoryHeader.className = 'search-category-header';
        categoryHeader.textContent = `${classified.no_source.label} (${classified.no_source.count})`;
        container.appendChild(categoryHeader);

        classified.no_source.problems.forEach(problem => {
            renderProblemItem(container, problem, 1);
        });
    }

    // Other problems
    if (classified.other.count > 0) {
        const categoryHeader = document.createElement('div');
        categoryHeader.className = 'search-category-header';
        categoryHeader.textContent = `${classified.other.label} (${classified.other.count})`;
        container.appendChild(categoryHeader);

        classified.other.problems.forEach(problem => {
            renderProblemItem(container, problem, 1);
        });
    }
}

// 문제 상세 로드
async function loadProblem(problemId) {
    // 로딩 표시
    const viewTab = document.getElementById('tab-view');
    viewTab.innerHTML = '<div class="empty-state"><p>로딩 중...</p></div>';

    // R2 CDN에서 문제 상세 정보 로드
    const problem = await loadProblemDetail(problemId);
    if (!problem) {
        showToast('문제를 찾을 수 없습니다.');
        return;
    }

    // 제목 업데이트
    document.getElementById('currentProblemTitle').textContent = `문제 ${problemId}`;

    // 문제 내용 표시
    if (problem.content) {
        let contentHtml = convertLatexToHtml(problem.content);

        // solution에서 SVG 마커 추출하여 문제 아래에 추가
        if (problem.solution) {
            const svgButtons = extractSvgButtons(problem.solution);
            if (svgButtons) {
                contentHtml += svgButtons;
            }
        }

        viewTab.innerHTML = `<div class="problem-content">${contentHtml}</div>`;
    } else {
        viewTab.innerHTML = '<div class="empty-state"><p>문제 내용이 없습니다.</p></div>';
    }

    // 메타데이터 표시
    const metadataTab = document.getElementById('tab-metadata');
    metadataTab.innerHTML = `
        <div class="metadata-view">
            <div class="metadata-item">
                <strong>문제 ID</strong>
                ${problem.id}
            </div>
            ${problem.source ? `
            <div class="metadata-item">
                <strong>출처</strong>
                ${problem.source}
            </div>` : ''}
            ${problem.answer ? `
            <div class="metadata-item">
                <strong>답안</strong>
                ${problem.answer}
            </div>` : ''}
            ${problem.category ? `
            <div class="metadata-item">
                <strong>카테고리</strong>
                ${problem.category}
            </div>` : ''}
            ${problem.difficulty ? `
            <div class="metadata-item">
                <strong>난이도</strong>
                ${problem.difficulty}/5
            </div>` : ''}
            ${problem.tags && problem.tags.length > 0 ? `
            <div class="metadata-item">
                <strong>태그</strong>
                ${problem.tags.join(', ')}
            </div>` : ''}
            ${problem.note ? `
            <div class="metadata-item">
                <strong>메모</strong>
                ${problem.note}
            </div>` : ''}
            <div class="metadata-item">
                <strong>원본 파일</strong>
                ${problem.source_file}
            </div>
            <div class="metadata-item">
                <strong>TikZ 사용</strong>
                ${problem.has_tikz ? '예' : '아니오'}
            </div>
        </div>
    `;

    // MathJax 렌더링
    if (window.MathJax) {
        MathJax.typesetPromise([viewTab]);
    }

    // 폴드아웃 버튼 이벤트 설정
    setupFigureToggles();
}
