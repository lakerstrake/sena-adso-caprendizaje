/**
 * SGVA SENA ADSO - Executive Application Core
 * Architecture: Clean Modular State-Driven Architecture
 * Security: OWASP Compliant (Strict Context Escaping, Safe DOM manipulation)
 * Accessibility: WCAG 2.1 AA / ISO 9241-210 Compliant
 */

'use strict';

// ---------------------------------------------------------
// 1. Candidate Context & Application Constants
// ---------------------------------------------------------
const CANDIDATE_PROFILE = Object.freeze({
    name: "Juan Manuel Lagos Monroy",
    phone: "(+57) 300 727 9875",
    email: "jmlagos2003@gmail.com",
    github: "https://github.com/lakerstrake",
    linkedin: "https://linkedin.com/in/juan-manuel-lagos-monroy",
    cvDrive: "https://drive.google.com/drive/folders/1BZ-qBNdPeYsxW84zIq_ls97UkPlQcHyN",
    program: "Tecnólogo en Análisis y Desarrollo de Software (ADSO) - SENA",
    availability: "Etapa Productiva (Septiembre 2026 - Marzo 2027)"
});

// ---------------------------------------------------------
// 2. Application State Management
// ---------------------------------------------------------
class AppStore {
    constructor(initialData = []) {
        this.rawData = Array.isArray(initialData) ? initialData : [];
        this.filteredData = [...this.rawData];
        this.activeTier = '';
        this.activeStack = '';
        this.filterFavs = false;
        this.viewMode = 'table'; // 'table' | 'cards'
        this.currentPage = 1;
        this.pageSize = 50;
        this.sortCol = 'ranking_posicion';
        this.sortAsc = true;
        this.activeItem = null;
        this.activeChannel = 'email';
        
        // Persistent State
        this.favorites = this.loadStorage('cap_favs', []);
        this.compareList = this.loadStorage('cap_comp', []);
        this.theme = this.loadStorage('cap_theme', 'dark');
    }

    loadStorage(key, fallback) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : fallback;
        } catch (e) {
            console.warn(`[Storage] Failed to read ${key}:`, e);
            return fallback;
        }
    }

    saveStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn(`[Storage] Failed to save ${key}:`, e);
        }
    }

    toggleFavorite(id) {
        const strId = String(id);
        if (this.favorites.includes(strId)) {
            this.favorites = this.favorites.filter(x => x !== strId);
        } else {
            this.favorites.push(strId);
        }
        this.saveStorage('cap_favs', this.favorites);
    }

    isFavorite(id) {
        return this.favorites.includes(String(id));
    }

    toggleCompare(id) {
        const strId = String(id);
        if (this.compareList.includes(strId)) {
            this.compareList = this.compareList.filter(x => x !== strId);
            this.saveStorage('cap_comp', this.compareList);
            return { status: 'removed' };
        } else {
            if (this.compareList.length >= 3) {
                return { status: 'limit_reached' };
            }
            this.compareList.push(strId);
            this.saveStorage('cap_comp', this.compareList);
            return { status: 'added' };
        }
    }

    isCompared(id) {
        return this.compareList.includes(String(id));
    }

    clearCompare() {
        this.compareList = [];
        this.saveStorage('cap_comp', this.compareList);
    }
}

// ---------------------------------------------------------
// 3. Security & Utility Helper Functions (OWASP)
// ---------------------------------------------------------
const SecurityUtils = {
    escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    },

    encodeMailParam(str) {
        return encodeURIComponent(str || '').replace(/%20/g, '+');
    }
};

// ---------------------------------------------------------
// 4. Main Application Controller
// ---------------------------------------------------------
class AppController {
    constructor() {
        const data = window.RAW_DATA || [];
        this.store = new AppStore(data);
        this.dom = {};
    }

    init() {
        this.cacheDomElements();
        this.initTheme();
        this.populateFilterDropdowns();
        this.bindEvents();
        this.updateFavCounter();
        this.updateCompareDock();
        this.applyFilters();
    }

    cacheDomElements() {
        this.dom = {
            html: document.documentElement,
            themeIcon: document.getElementById('themeIcon'),
            themeBtn: document.getElementById('themeBtn'),
            
            // Navigation
            pillDirectory: document.getElementById('pillDirectory'),
            pillStrategy: document.getElementById('pillStrategy'),
            pillFavs: document.getElementById('pillFavs'),
            pillTotalCount: document.getElementById('pillTotalCount'),
            pillFavCount: document.getElementById('pillFavCount'),
            
            // Sections
            sectionDirectory: document.getElementById('sectionDirectory'),
            sectionStrategy: document.getElementById('sectionStrategy'),
            
            // Filters
            mainSearch: document.getElementById('mainSearch'),
            secondaryFiltersRow: document.getElementById('secondaryFiltersRow'),
            toggleFiltersBtn: document.getElementById('toggleFiltersBtn'),
            activeFilterBadge: document.getElementById('activeFilterBadge'),
            filterChannel: document.getElementById('filterChannel'),
            filterCompetition: document.getElementById('filterCompetition'),
            filterDpto: document.getElementById('filterDpto'),
            filterCity: document.getElementById('filterCity'),
            filterSort: document.getElementById('filterSort'),
            
            // View wrappers
            tableCardWrap: document.getElementById('tableCardWrap'),
            cardsGridWrap: document.getElementById('cardsGridWrap'),
            tableBody: document.getElementById('tableBody'),
            lblVisibleCount: document.getElementById('lblVisibleCount'),
            lblTotalCount: document.getElementById('lblTotalCount'),
            lblPagination: document.getElementById('lblPagination'),
            paginationPages: document.getElementById('paginationPages'),
            btnLayoutTable: document.getElementById('btnLayoutTable'),
            btnLayoutCards: document.getElementById('btnLayoutCards'),
            
            // Comparison Dock & Modal
            comparisonDock: document.getElementById('comparisonDock'),
            dockCount: document.getElementById('dockCount'),
            dockList: document.getElementById('dockList'),
            compareModal: document.getElementById('compareModal'),
            compareTable: document.getElementById('compareTable'),
            
            // Detail Modal
            detailModal: document.getElementById('detailModal'),
            mTitle: document.getElementById('mTitle'),
            mSubtitle: document.getElementById('mSubtitle'),
            mScore: document.getElementById('mScore'),
            mEsc: document.getElementById('mEsc'),
            mRating: document.getElementById('mRating'),
            mSupport: document.getElementById('mSupport'),
            mFavBtn: document.getElementById('mFavBtn'),
            
            // Modal Sub Tabs
            mTabOutreach: document.getElementById('mTabOutreach'),
            mTabInterview: document.getElementById('mTabInterview'),
            mTabCareer: document.getElementById('mTabCareer'),
            mTabDetails: document.getElementById('mTabDetails'),
            mSecOutreach: document.getElementById('mSecOutreach'),
            mSecInterview: document.getElementById('mSecInterview'),
            mSecCareer: document.getElementById('mSecCareer'),
            mSecDetails: document.getElementById('mSecDetails'),
            
            // Modal Outreach
            mChEmail: document.getElementById('mChEmail'),
            mChWA: document.getElementById('mChWA'),
            mChLinkedIn: document.getElementById('mChLinkedIn'),
            mOutreachHeading: document.getElementById('mOutreachHeading'),
            mOutreachBody: document.getElementById('mOutreachBody'),
            mOutreachActions: document.getElementById('mOutreachActions'),
            mContactName: document.getElementById('mContactName'),
            mContactEmail: document.getElementById('mContactEmail'),
            mContactPhone: document.getElementById('mContactPhone'),
            mContactModalidad: document.getElementById('mContactModalidad'),
            
            // Modal Interview & Career
            mInterviewList: document.getElementById('mInterviewList'),
            mCurvaTitulo: document.getElementById('mCurvaTitulo'),
            mCurvaDetalle: document.getElementById('mCurvaDetalle'),
            mTimelineGrid: document.getElementById('mTimelineGrid'),
            mFinAcumulado5A: document.getElementById('mFinAcumulado5A'),
            mFinDiferencial: document.getElementById('mFinDiferencial'),
            mPerfil: document.getElementById('mPerfil'),
            mFunciones: document.getElementById('mFunciones'),
            mClosingDate: document.getElementById('mClosingDate'),
            
            // Feedback
            toastMsg: document.getElementById('toastMsg')
        };
    }

    initTheme() {
        const theme = this.store.theme;
        this.dom.html.setAttribute('data-theme', theme);
        if (this.dom.themeIcon) {
            this.dom.themeIcon.className = theme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        }
    }

    toggleTheme() {
        const current = this.dom.html.getAttribute('data-theme') || 'dark';
        const next = current === 'dark' ? 'light' : 'dark';
        this.dom.html.setAttribute('data-theme', next);
        this.store.theme = next;
        this.store.saveStorage('cap_theme', next);
        if (this.dom.themeIcon) {
            this.dom.themeIcon.className = next === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        }
    }

    populateFilterDropdowns() {
        const dptos = [...new Set(this.store.rawData.map(d => d.departamento).filter(Boolean))].sort();
        if (this.dom.filterDpto) {
            dptos.forEach(d => {
                const opt = document.createElement('option');
                opt.value = d;
                opt.textContent = d;
                this.dom.filterDpto.appendChild(opt);
            });

            this.dom.filterDpto.addEventListener('change', () => {
                this.populateCityDropdown(this.dom.filterDpto.value);
            });
        }
    }

    populateCityDropdown(selectedDpto) {
        if (!this.dom.filterCity) return;
        this.dom.filterCity.innerHTML = '<option value="">Todas</option>';
        const dataset = selectedDpto 
            ? this.store.rawData.filter(d => d.departamento === selectedDpto)
            : this.store.rawData;
        const cities = [...new Set(dataset.map(d => (d.ciudad || '').trim()).filter(Boolean))].sort();
        cities.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            this.dom.filterCity.appendChild(opt);
        });
    }

    bindEvents() {
        // Search Input
        if (this.dom.mainSearch) {
            this.dom.mainSearch.addEventListener('input', () => {
                this.store.currentPage = 1;
                this.applyFilters();
            });
        }

        // Secondary Filters
        ['filterChannel', 'filterCompetition', 'filterDpto', 'filterCity', 'filterSort'].forEach(id => {
            const el = this.dom[id];
            if (el) {
                el.addEventListener('change', () => {
                    this.updateFilterBadge();
                    this.store.currentPage = 1;
                    this.applyFilters();
                });
            }
        });

        // Global Keydown (Escape handler)
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeDetailModal();
                this.closeCompareModal();
            }
        });
    }

    updateFilterBadge() {
        let count = 0;
        if (this.dom.filterChannel?.value) count++;
        if (this.dom.filterCompetition?.value) count++;
        if (this.dom.filterDpto?.value) count++;
        if (this.dom.filterCity?.value) count++;
        if (this.dom.filterSort?.value && this.dom.filterSort.value !== 'ranking_asc') count++;
        if (this.dom.activeFilterBadge) {
            this.dom.activeFilterBadge.textContent = count;
        }
    }

    switchNavTab(tab) {
        document.querySelectorAll('.nav-pill-btn').forEach(b => b.classList.remove('active'));
        if (tab === 'directory') {
            this.dom.pillDirectory?.classList.add('active');
            this.dom.sectionDirectory.style.display = 'flex';
            this.dom.sectionStrategy.style.display = 'none';
            this.store.filterFavs = false;
            this.applyFilters();
        } else if (tab === 'strategy') {
            this.dom.pillStrategy?.classList.add('active');
            this.dom.sectionDirectory.style.display = 'none';
            this.dom.sectionStrategy.style.display = 'flex';
        } else if (tab === 'favs') {
            this.dom.pillFavs?.classList.add('active');
            this.dom.sectionDirectory.style.display = 'flex';
            this.dom.sectionStrategy.style.display = 'none';
            this.store.filterFavs = true;
            this.applyFilters();
        }
    }

    setTierFilter(tier, targetBtn) {
        this.store.activeTier = tier;
        document.querySelectorAll('.tier-seg-btn').forEach(b => b.classList.remove('active'));
        if (targetBtn) targetBtn.closest('.tier-seg-btn')?.classList.add('active');
        this.store.currentPage = 1;
        this.applyFilters();
    }

    setStackChipFilter(tag, targetBtn) {
        this.store.activeStack = tag;
        document.querySelectorAll('.chip-btn').forEach(b => b.classList.remove('active'));
        if (targetBtn) targetBtn.classList.add('active');
        this.store.currentPage = 1;
        this.applyFilters();
    }

    toggleSecondaryFilters() {
        const row = this.dom.secondaryFiltersRow;
        const btn = this.dom.toggleFiltersBtn;
        if (!row || !btn) return;
        if (row.style.display === 'none' || row.style.display === '') {
            row.style.display = 'grid';
            btn.classList.add('btn-primary');
        } else {
            row.style.display = 'none';
            btn.classList.remove('btn-primary');
        }
    }

    resetFilters() {
        if (this.dom.mainSearch) this.dom.mainSearch.value = '';
        if (this.dom.filterChannel) this.dom.filterChannel.value = '';
        if (this.dom.filterCompetition) this.dom.filterCompetition.value = '';
        if (this.dom.filterDpto) this.dom.filterDpto.value = '';
        if (this.dom.filterCity) this.dom.filterCity.value = '';
        if (this.dom.filterSort) this.dom.filterSort.value = 'ranking_asc';
        
        this.store.activeTier = '';
        this.store.activeStack = '';
        this.store.filterFavs = false;
        
        document.querySelectorAll('.tier-seg-btn').forEach(b => b.classList.remove('active'));
        document.querySelector('.tier-seg-btn')?.classList.add('active');
        
        document.querySelectorAll('.chip-btn').forEach(b => b.classList.remove('active'));
        document.querySelector('.chip-btn')?.classList.add('active');
        
        this.updateFilterBadge();
        this.store.currentPage = 1;
        this.applyFilters();
        this.showToast('Filtros restablecidos');
    }

    applyFilters() {
        const query = (this.dom.mainSearch?.value || '').toLowerCase().trim();
        const ch = this.dom.filterChannel?.value || '';
        const comp = this.dom.filterCompetition?.value || '';
        const dpto = this.dom.filterDpto?.value || '';
        const city = this.dom.filterCity?.value || '';
        const sort = this.dom.filterSort?.value || 'ranking_asc';

        this.store.filteredData = this.store.rawData.filter(it => {
            if (this.store.filterFavs && !this.store.isFavorite(it.solicitud_id)) return false;
            if (this.store.activeTier && it.cat_id !== this.store.activeTier) return false;
            if (this.store.activeStack && (!it.stack_tags || !it.stack_tags.includes(this.store.activeStack))) return false;
            if (ch === 'WHATSAPP' && !it.is_whatsapp) return false;
            if (ch === 'EMAIL' && (!it.email || !it.email.includes('@'))) return false;
            if (comp && it.facilidad_code !== comp) return false;

            if (query) {
                const combined = `${it.empresa} ${it.nit} ${it.ciudad} ${it.departamento} ${it.funciones} ${it.perfil_requerido} ${it.contacto} ${it.email} ${it.telefono}`.toLowerCase();
                if (!combined.includes(query)) return false;
            }

            if (dpto && it.departamento !== dpto) return false;
            if (city && (it.ciudad || '').trim() !== city) return false;

            return true;
        });

        // Sorting
        this.store.filteredData.sort((a, b) => {
            if (sort === 'ranking_asc') return (a.ranking_posicion || 0) - (b.ranking_posicion || 0);
            if (sort === 'escalabilidad_desc') return (b.escalabilidad_score || 0) - (a.escalabilidad_score || 0);
            if (sort === 'reputation_desc') return (b.reputacion_rating || 0) - (a.reputacion_rating || 0);
            if (sort === 'comp_asc') return (a.competencia_ratio || 0) - (b.competencia_ratio || 0);
            if (sort === 'vacancies_desc') return (b.vacantes || 0) - (a.vacantes || 0);
            return 0;
        });

        if (this.dom.lblVisibleCount) {
            this.dom.lblVisibleCount.textContent = this.store.filteredData.length;
        }

        if (this.store.viewMode === 'table') {
            this.renderTable();
        } else {
            this.renderCards();
        }
    }

    renderTable() {
        const tbody = this.dom.tableBody;
        if (!tbody) return;
        tbody.innerHTML = '';

        const total = this.store.filteredData.length;
        const totalPages = Math.ceil(total / this.store.pageSize) || 1;
        if (this.store.currentPage > totalPages) this.store.currentPage = totalPages;

        const start = (this.store.currentPage - 1) * this.store.pageSize;
        const pageSlice = this.store.filteredData.slice(start, start + this.store.pageSize);

        if (total === 0) {
            tbody.innerHTML = `<tr><td colspan="11" style="text-align: center; padding: 2.5rem; color: var(--text-dim);">No se encontraron vacantes con los criterios seleccionados.</td></tr>`;
            if (this.dom.lblPagination) this.dom.lblPagination.textContent = '0 resultados';
            if (this.dom.paginationPages) this.dom.paginationPages.innerHTML = '';
            return;
        }

        pageSlice.forEach(it => {
            const tr = document.createElement('tr');
            tr.onclick = () => this.openDetailModal(it);

            const isFav = this.store.isFavorite(it.solicitud_id);
            const isComp = this.store.isCompared(it.solicitud_id);
            const favIcon = isFav ? 'fa-solid fa-bookmark' : 'fa-regular fa-bookmark';
            const favColor = isFav ? 'color: var(--tier-3);' : '';

            let tierClass = 'pill-tier-1';
            if (it.cat_id === 'TIER_2') tierClass = 'pill-tier-2';
            else if (it.cat_id === 'TIER_3') tierClass = 'pill-tier-3';
            else if (it.cat_id === 'TIER_4') tierClass = 'pill-tier-4';
            else if (it.cat_id === 'TIER_5') tierClass = 'pill-tier-5';

            let dotClass = 'ratio-green';
            if (it.competencia_ratio > 5.0) dotClass = 'ratio-rose';
            else if (it.competencia_ratio > 2.0) dotClass = 'ratio-amber';
            else if (it.competencia_ratio > 1.0) dotClass = 'ratio-blue';

            const hasEmail = it.email && it.email.includes('@');
            const cleanApoyo = "$1.423.500 COP";
            const cleanTecho5A = it.techo_salarial_5anios ? it.techo_salarial_5anios.split('(')[0].replace('COP','').trim() : '$10M-$22M';
            const posFormatted = (it.ranking_posicion || 1) < 10 ? '0' + it.ranking_posicion : it.ranking_posicion;

            tr.innerHTML = `
                <td style="text-align: center;" onclick="event.stopPropagation();">
                    <input type="checkbox" ${isComp ? 'checked' : ''} onchange="app.handleToggleCompare('${SecurityUtils.escapeHtml(it.solicitud_id)}', event)">
                </td>
                <td onclick="event.stopPropagation();">
                    <i class="${favIcon}" style="cursor: pointer; ${favColor}" onclick="app.handleToggleFavorite('${SecurityUtils.escapeHtml(it.solicitud_id)}', event)"></i>
                </td>
                <td style="font-family: var(--font-mono); font-weight: 700; color: var(--text-dim);">#${posFormatted}</td>
                <td>
                    <div class="cell-main">
                        <span class="cell-title" title="${SecurityUtils.escapeHtml(it.empresa)}">${SecurityUtils.escapeHtml(it.empresa)}</span>
                        <span class="cell-sub">${SecurityUtils.escapeHtml(it.ciudad || '')}, ${SecurityUtils.escapeHtml(it.departamento || '')} • NIT: ${SecurityUtils.escapeHtml(it.nit || 'N/A')}</span>
                    </div>
                </td>
                <td><span class="pill-badge ${tierClass}">${SecurityUtils.escapeHtml(it.cat_badge || 'Tier')}</span></td>
                <td><strong style="color: var(--tier-1); font-family: var(--font-mono);">${it.puntaje_exito || 0}</strong><span style="color: var(--text-dim); font-size: 0.62rem;">/100</span></td>
                <td><span class="rating-chip"><i class="fa-solid fa-star"></i> ${(it.reputacion_rating || 3.8).toFixed(1)}</span></td>
                <td><strong style="color: var(--tier-2); font-family: var(--font-mono);">${it.escalabilidad_score || 70}/100</strong></td>
                <td>
                    <span style="display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.7rem; white-space: nowrap;">
                        <span class="ratio-dot ${dotClass}"></span>
                        <span>${it.vacantes || 1} vac · ${it.postulados || 0} post</span>
                    </span>
                </td>
                <td>
                    <div class="cell-main" style="white-space: nowrap;">
                        <span style="color: var(--brand-primary); font-weight: 600; font-family: var(--font-mono); font-size: 0.7rem;">${cleanApoyo}</span>
                        <span style="color: var(--tier-1); font-size: 0.62rem; font-weight: 600;">5A: ${SecurityUtils.escapeHtml(cleanTecho5A)}</span>
                    </div>
                </td>
                <td style="text-align: right;" onclick="event.stopPropagation();">
                    <div class="row-actions">
                        ${hasEmail ? `<a href="mailto:${SecurityUtils.escapeHtml(it.email)}?subject=Postulaci%C3%B3n+Contrato+ADSO+-+Juan+Manuel+Lagos&body=${encodeURIComponent(it.correo_formal_completo || '')}" class="mini-btn mini-mail" title="Enviar correo formal"><i class="fa-solid fa-envelope"></i></a>` : ''}
                        ${it.is_whatsapp && it.whatsapp_url ? `<a href="${SecurityUtils.escapeHtml(it.whatsapp_url)}" target="_blank" rel="noopener noreferrer" class="mini-btn mini-wa" title="WhatsApp"><i class="fa-brands fa-whatsapp"></i></a>` : ''}
                        ${it.linkedin_contact_search_url ? `<a href="${SecurityUtils.escapeHtml(it.linkedin_contact_search_url)}" target="_blank" rel="noopener noreferrer" class="mini-btn" title="LinkedIn"><i class="fa-brands fa-linkedin" style="color: var(--linkedin-color);"></i></a>` : ''}
                        <button class="mini-btn" style="font-weight: 700;" onclick="app.openDetailModalById('${SecurityUtils.escapeHtml(it.solicitud_id)}')">Detalle</button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });

        if (this.dom.lblPagination) {
            this.dom.lblPagination.textContent = `Mostrando ${start + 1}-${Math.min(start + this.store.pageSize, total)} de ${total} vacantes`;
        }

        this.renderPagination(totalPages);
    }

    renderPagination(totalPages) {
        if (!this.dom.paginationPages) return;
        let pagesHtml = '';
        for (let i = 1; i <= totalPages; i++) {
            if (totalPages > 6 && Math.abs(i - this.store.currentPage) > 2 && i !== 1 && i !== totalPages) continue;
            const activeStyle = i === this.store.currentPage ? 'background: var(--brand-primary); color: #fff;' : '';
            pagesHtml += `<button class="btn" style="padding: 0.15rem 0.45rem; font-size: 0.68rem; ${activeStyle}" onclick="app.goToPage(${i})">${i}</button>`;
        }
        this.dom.paginationPages.innerHTML = pagesHtml;
    }

    goToPage(p) {
        this.store.currentPage = p;
        this.renderTable();
    }

    renderCards() {
        const grid = this.dom.cardsGridWrap;
        if (!grid) return;
        grid.innerHTML = '';
        this.store.filteredData.forEach(it => {
            const card = document.createElement('article');
            card.className = 'clean-card';
            card.onclick = () => this.openDetailModal(it);
            card.innerHTML = `
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.35rem;">
                        <span class="pill-badge pill-tier-1">${SecurityUtils.escapeHtml(it.cat_badge || 'Tier')}</span>
                        <span class="rating-chip"><i class="fa-solid fa-star"></i> ${(it.reputacion_rating || 3.8).toFixed(1)}</span>
                    </div>
                    <h3 style="font-size: 0.82rem; font-weight: 700; color: var(--text-main); line-height: 1.3;">${SecurityUtils.escapeHtml(it.empresa)}</h3>
                    <div style="font-size: 0.66rem; color: var(--text-dim); margin-top: 0.15rem;">${SecurityUtils.escapeHtml(it.ciudad || '')}, ${SecurityUtils.escapeHtml(it.departamento || '')}</div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.3rem; background: var(--bg-canvas); padding: 0.35rem; border-radius: var(--radius-xs); text-align: center;">
                    <div><span style="font-size: 0.58rem; color: var(--text-dim);">PUNTOS</span><div style="font-weight: 700; color: var(--tier-1);">${it.puntaje_exito || 0}</div></div>
                    <div><span style="font-size: 0.58rem; color: var(--text-dim);">ESCALA</span><div style="font-weight: 700; color: var(--tier-2);">${it.escalabilidad_score || 70}</div></div>
                    <div><span style="font-size: 0.58rem; color: var(--text-dim);">VACANTES</span><div style="font-weight: 700; color: var(--brand-primary);">${it.vacantes || 1}</div></div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.66rem; color: var(--text-muted); border-top: 1px solid var(--border-muted); padding-top: 0.35rem;">
                    <span><strong>Práctica:</strong> $1.423.500 COP</span>
                    <span style="color: var(--tier-1); font-weight: 600;">5A: ${SecurityUtils.escapeHtml(it.techo_salarial_5anios ? it.techo_salarial_5anios.split('(')[0].trim() : '')}</span>
                </div>
            `;
            grid.appendChild(card);
        });
    }

    setLayout(mode) {
        this.store.viewMode = mode;
        if (mode === 'cards') {
            this.dom.tableCardWrap.style.display = 'none';
            this.dom.cardsGridWrap.style.display = 'grid';
            this.dom.btnLayoutCards?.classList.add('active');
            this.dom.btnLayoutTable?.classList.remove('active');
            this.renderCards();
        } else {
            this.dom.tableCardWrap.style.display = 'flex';
            this.dom.cardsGridWrap.style.display = 'none';
            this.dom.btnLayoutTable?.classList.add('active');
            this.dom.btnLayoutCards?.classList.remove('active');
            this.renderTable();
        }
    }

    handleToggleFavorite(id, event) {
        if (event) event.stopPropagation();
        this.store.toggleFavorite(id);
        this.updateFavCounter();
        if (this.store.filterFavs) {
            this.applyFilters();
        } else {
            if (this.store.viewMode === 'table') this.renderTable();
            else this.renderCards();
        }
        if (this.store.activeItem && String(this.store.activeItem.solicitud_id) === String(id)) {
            this.updateModalFavBtn();
        }
    }

    updateFavCounter() {
        if (this.dom.pillFavCount) {
            this.dom.pillFavCount.textContent = this.store.favorites.length;
        }
    }

    handleToggleCompare(id, event) {
        if (event) event.stopPropagation();
        const res = this.store.toggleCompare(id);
        if (res.status === 'limit_reached') {
            this.showToast('Máximo 3 empresas para comparar');
            return;
        }
        this.updateCompareDock();
        if (this.store.viewMode === 'table') this.renderTable();
        else this.renderCards();
    }

    updateCompareDock() {
        const dock = this.dom.comparisonDock;
        if (!dock) return;
        const count = this.store.compareList.length;
        if (this.dom.dockCount) this.dom.dockCount.textContent = count;

        if (count === 0) {
            dock.style.display = 'none';
            return;
        }
        dock.style.display = 'flex';

        let html = '';
        this.store.compareList.forEach(id => {
            const it = this.store.rawData.find(d => String(d.solicitud_id) === String(id));
            if (it) {
                html += `<span class="pill-badge pill-tier-1">${SecurityUtils.escapeHtml(it.empresa.substring(0, 14))}... <i class="fa-solid fa-xmark" style="cursor: pointer; margin-left: 2px;" onclick="app.handleToggleCompare('${SecurityUtils.escapeHtml(it.solicitud_id)}', event)"></i></span>`;
            }
        });
        if (this.dom.dockList) this.dom.dockList.innerHTML = html;
    }

    clearComparison() {
        this.store.clearCompare();
        this.updateCompareDock();
        if (this.store.viewMode === 'table') this.renderTable();
        else this.renderCards();
    }

    openCompareModal() {
        if (this.store.compareList.length < 2) {
            this.showToast('Selecciona al menos 2 empresas');
            return;
        }
        const items = this.store.compareList.map(id => this.store.rawData.find(d => String(d.solicitud_id) === String(id))).filter(Boolean);
        const tbl = this.dom.compareTable;
        if (!tbl) return;

        let html = '<thead><tr><th style="padding: 0.5rem; text-align: left;">Criterio</th>';
        items.forEach(it => {
            html += `<th style="padding: 0.5rem; text-align: left;"><strong style="color: var(--brand-primary);">${SecurityUtils.escapeHtml(it.empresa)}</strong><div style="font-size: 0.65rem; color: var(--text-dim);">#${it.ranking_posicion} • ${SecurityUtils.escapeHtml(it.cat_badge || '')}</div></th>`;
        });
        html += '</tr></thead><tbody>';

        const fields = [
            { label: "Afinidad & Puntos", fn: it => `<strong style="color: var(--tier-1);">${it.puntaje_exito} / 100</strong>` },
            { label: "Reputación Web", fn: it => `★ ${(it.reputacion_rating || 3.8).toFixed(1)} (${SecurityUtils.escapeHtml(it.reputacion_fuente || 'Web')})` },
            { label: "Escalabilidad", fn: it => `<strong style="color: var(--tier-2);">${it.escalabilidad_score || 70}/100</strong> (${SecurityUtils.escapeHtml(it.escalabilidad_nivel || 'Media')})` },
            { label: "Apoyo Práctica", fn: it => `<strong style="color: var(--brand-primary);">$1.423.500 COP</strong>` },
            { label: "5A Salario & Acumulado", fn: it => `<strong>${SecurityUtils.escapeHtml(it.techo_salarial_5anios || '')}</strong><div style="font-size: 0.65rem; color: var(--brand-primary);">${SecurityUtils.escapeHtml(it.finanzas_5anios?.acumulado_5a || '')}</div>` },
            { label: "Competencia", fn: it => `${it.vacantes || 1} vac. vs ${it.postulados || 0} post. (Ratio: ${it.competencia_ratio || 0})` },
            { label: "Contacto Directo", fn: it => `${SecurityUtils.escapeHtml(it.contacto || 'RRHH')} • ${SecurityUtils.escapeHtml(it.email || '')} • ${SecurityUtils.escapeHtml(it.telefono || '')}` }
        ];

        fields.forEach(f => {
            html += `<tr style="border-bottom: 1px solid var(--border-muted);"><td style="padding: 0.5rem; font-weight: 600; color: var(--text-dim);">${f.label}</td>`;
            items.forEach(it => { html += `<td style="padding: 0.5rem;">${f.fn(it)}</td>`; });
            html += '</tr>';
        });
        html += '</tbody>';
        tbl.innerHTML = html;
        if (this.dom.compareModal) this.dom.compareModal.style.display = 'flex';
    }

    closeCompareModal() {
        if (this.dom.compareModal) this.dom.compareModal.style.display = 'none';
    }

    openDetailModalById(solId) {
        const it = this.store.rawData.find(d => String(d.solicitud_id) === String(solId));
        if (it) this.openDetailModal(it);
    }

    openDetailModal(it) {
        this.store.activeItem = it;
        const setTxt = (el, val) => { if (el) el.textContent = val || ''; };

        setTxt(this.dom.mTitle, it.empresa);
        setTxt(this.dom.mSubtitle, `${it.ciudad?.trim() || ''}, ${it.departamento || ''} • NIT: ${it.nit || 'No registrado'}`);
        setTxt(this.dom.mScore, `${it.puntaje_exito || 0} / 100`);
        setTxt(this.dom.mEsc, `${it.escalabilidad_score || 75} / 100`);
        setTxt(this.dom.mRating, `★ ${(it.reputacion_rating || 3.8).toFixed(1)}`);
        setTxt(this.dom.mSupport, '$1.423.500 COP');

        setTxt(this.dom.mContactName, it.contacto || 'Equipo de Selección y Gestión Humana');
        setTxt(this.dom.mContactEmail, it.email || 'No registrado');
        setTxt(this.dom.mContactPhone, it.telefono || 'No registrado');
        setTxt(this.dom.mContactModalidad, it.modalidad || 'Presencial / Híbrido');

        setTxt(this.dom.mCurvaTitulo, it.curva_aprendizaje_titulo || 'Desarrollo de Software');
        setTxt(this.dom.mCurvaDetalle, it.curva_aprendizaje_detalle || '');
        setTxt(this.dom.mPerfil, it.perfil_requerido || 'No registrado');
        setTxt(this.dom.mFunciones, it.funciones || 'No registrado');
        setTxt(this.dom.mClosingDate, it.fecha_cierre || 'No registrada');

        if (it.finanzas_5anios) {
            setTxt(this.dom.mFinAcumulado5A, it.finanzas_5anios.acumulado_5a);
            setTxt(this.dom.mFinDiferencial, it.finanzas_5anios.diferencial_vs_pyme);
        }

        // Timeline
        const tl = this.dom.mTimelineGrid;
        if (tl && it.hitos_carrera) {
            let html = '';
            it.hitos_carrera.forEach(h => {
                html += `<div style="background: var(--bg-canvas); border: 1px solid var(--border-muted); border-radius: var(--radius-xs); padding: 0.45rem; font-size: 0.68rem;">
                    <span style="color: var(--text-dim); text-transform: uppercase; font-weight: 700; font-size: 0.6rem;">${SecurityUtils.escapeHtml(h.periodo)}</span>
                    <div style="font-weight: 700; color: var(--text-main); margin: 2px 0;">${SecurityUtils.escapeHtml(h.rol)}</div>
                    <div style="color: var(--brand-primary); font-family: var(--font-mono); font-weight: 700;">${SecurityUtils.escapeHtml(h.salario)}</div>
                </div>`;
            });
            tl.innerHTML = html;
        }

        // Interview Simulator
        const qaList = this.dom.mInterviewList;
        if (qaList && it.preguntas_entrevista) {
            let html = '';
            it.preguntas_entrevista.forEach((q, idx) => {
                html += `
                    <div style="background: var(--bg-canvas); border: 1px solid var(--border-muted); border-radius: var(--radius-sm); padding: 0.65rem; font-size: 0.72rem;">
                        <strong style="color: var(--tier-2);">#${idx + 1} ${SecurityUtils.escapeHtml(q.pregunta)}</strong>
                        <div style="color: var(--text-muted); margin: 0.3rem 0; line-height: 1.4;">${SecurityUtils.escapeHtml(q.respuesta_modelo)}</div>
                        <div style="color: var(--brand-primary); font-size: 0.68rem;"><i class="fa-brands fa-github"></i> ${SecurityUtils.escapeHtml(q.tip_github)}</div>
                    </div>
                `;
            });
            qaList.innerHTML = html;
        }

        this.updateModalFavBtn();
        this.setModalTab('outreach');
        this.setChannel('email');
        if (this.dom.detailModal) this.dom.detailModal.style.display = 'flex';
    }

    closeDetailModal() {
        if (this.dom.detailModal) this.dom.detailModal.style.display = 'none';
    }

    updateModalFavBtn() {
        if (this.dom.mFavBtn && this.store.activeItem) {
            const isFav = this.store.isFavorite(this.store.activeItem.solicitud_id);
            this.dom.mFavBtn.innerHTML = isFav 
                ? '<i class="fa-solid fa-bookmark" style="color: var(--tier-3);"></i>' 
                : '<i class="fa-regular fa-bookmark"></i>';
        }
    }

    setModalTab(tab) {
        document.querySelectorAll('.modal-tab-item').forEach(b => b.classList.remove('active'));
        [this.dom.mSecOutreach, this.dom.mSecInterview, this.dom.mSecCareer, this.dom.mSecDetails].forEach(el => {
            if (el) el.style.display = 'none';
        });

        if (tab === 'outreach') {
            this.dom.mTabOutreach?.classList.add('active');
            if (this.dom.mSecOutreach) this.dom.mSecOutreach.style.display = 'flex';
        } else if (tab === 'interview') {
            this.dom.mTabInterview?.classList.add('active');
            if (this.dom.mSecInterview) this.dom.mSecInterview.style.display = 'flex';
        } else if (tab === 'career') {
            this.dom.mTabCareer?.classList.add('active');
            if (this.dom.mSecCareer) this.dom.mSecCareer.style.display = 'flex';
        } else if (tab === 'details') {
            this.dom.mTabDetails?.classList.add('active');
            if (this.dom.mSecDetails) this.dom.mSecDetails.style.display = 'flex';
        }
    }

    setChannel(ch) {
        this.store.activeChannel = ch;
        const it = this.store.activeItem;
        if (!it) return;

        if (this.dom.mChEmail) this.dom.mChEmail.className = ch === 'email' ? 'btn btn-primary' : 'btn';
        if (this.dom.mChWA) this.dom.mChWA.className = ch === 'wa' ? 'btn btn-whatsapp active' : 'btn';
        if (this.dom.mChLinkedIn) this.dom.mChLinkedIn.className = ch === 'linkedin' ? 'btn btn-linkedin active' : 'btn';

        if (ch === 'email') {
            if (this.dom.mOutreachHeading) this.dom.mOutreachHeading.textContent = 'Carta Formal de Postulación Institucional';
            if (this.dom.mOutreachBody) this.dom.mOutreachBody.textContent = it.correo_formal_completo || '';
            const hasEmail = it.email && it.email.includes('@');
            const mailtoLink = hasEmail ? `mailto:${SecurityUtils.escapeHtml(it.email)}?subject=Postulaci%C3%B3n+Contrato+ADSO+-+Juan+Manuel+Lagos&body=${encodeURIComponent(it.correo_formal_completo || '')}` : '#';
            if (this.dom.mOutreachActions) {
                this.dom.mOutreachActions.innerHTML = `
                    <button class="btn" style="padding: 0.2rem 0.5rem;" onclick="app.copyToClipboard('mOutreachBody')"><i class="fa-regular fa-copy"></i> Copiar Correo</button>
                    ${hasEmail ? `<a href="${mailtoLink}" class="btn btn-primary" style="padding: 0.2rem 0.5rem;"><i class="fa-solid fa-paper-plane"></i> Abrir en Mi Correo</a>` : '<span style="font-size: 0.68rem; color: var(--text-dim);">Sin correo registrado</span>'}
                `;
            }
        } else if (ch === 'wa') {
            if (this.dom.mOutreachHeading) this.dom.mOutreachHeading.textContent = 'Mensaje de WhatsApp Directo';
            if (this.dom.mOutreachBody) this.dom.mOutreachBody.textContent = it.whatsapp_message || '';
            if (this.dom.mOutreachActions) {
                this.dom.mOutreachActions.innerHTML = `
                    <button class="btn" style="padding: 0.2rem 0.5rem;" onclick="app.copyToClipboard('mOutreachBody')"><i class="fa-regular fa-copy"></i> Copiar Mensaje</button>
                    ${it.is_whatsapp && it.whatsapp_url ? `<a href="${SecurityUtils.escapeHtml(it.whatsapp_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-whatsapp" style="padding: 0.2rem 0.5rem;"><i class="fa-brands fa-whatsapp"></i> Abrir Chat</a>` : '<span style="font-size: 0.68rem; color: var(--text-dim);">Teléfono fijo (usa correo)</span>'}
                `;
            }
        } else if (ch === 'linkedin') {
            if (this.dom.mOutreachHeading) this.dom.mOutreachHeading.textContent = 'Nota de Conexión en LinkedIn (< 300 Caracteres)';
            if (this.dom.mOutreachBody) this.dom.mOutreachBody.textContent = it.linkedin_connect_message || '';
            if (this.dom.mOutreachActions) {
                this.dom.mOutreachActions.innerHTML = `
                    <button class="btn" style="padding: 0.2rem 0.5rem;" onclick="app.copyToClipboard('mOutreachBody')"><i class="fa-regular fa-copy"></i> Copiar Nota</button>
                    <a href="${SecurityUtils.escapeHtml(it.linkedin_contact_search_url || '')}" target="_blank" rel="noopener noreferrer" class="btn btn-linkedin" style="padding: 0.2rem 0.5rem;"><i class="fa-brands fa-linkedin"></i> Buscar Reclutador</a>
                `;
            }
        }
    }

    copyToClipboard(elementId) {
        const el = document.getElementById(elementId);
        if (el) {
            navigator.clipboard.writeText(el.textContent).then(() => {
                this.showToast('Texto copiado al portapapeles');
            }).catch(() => {
                this.showToast('No se pudo copiar');
            });
        }
    }

    showToast(msg) {
        const t = this.dom.toastMsg;
        if (t) {
            t.textContent = msg;
            t.style.display = 'block';
            setTimeout(() => { t.style.display = 'none'; }, 2000);
        }
    }

    exportData(fmt) {
        if (typeof XLSX !== 'undefined') {
            const ws = XLSX.utils.json_to_sheet(this.store.filteredData);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "ADSO_SENA");
            if (fmt === 'xlsx') XLSX.writeFile(wb, "postulaciones_adso_sena.xlsx");
            else XLSX.writeFile(wb, "postulaciones_adso_sena.csv");
            this.showToast(`Exportando datos en ${fmt.toUpperCase()}...`);
        } else {
            this.showToast('Librería de exportación no disponible');
        }
    }
}

// Global App Instance
const app = new AppController();

document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
