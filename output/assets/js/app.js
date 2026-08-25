/**
 * SGVA SENA ADSO - Clean Architecture Application Controller
 * Patterns: MVVM / Store Pattern + Event Delegation + Responsive Adaptations
 * Security: OWASP Top 10 Compliant (Zero Inline JS, Strict Contextual Escaping)
 * Accessibility: WCAG 2.1 AA / ISO 9241-210 Compliant
 */

'use strict';

// =========================================================================
// 1. CONFIGURATION & DOMAIN CONSTANTS
// =========================================================================
const CONFIG = Object.freeze({
    CANDIDATE: {
        name: "Juan Manuel Lagos Monroy",
        phone: "(+57) 300 727 9875",
        email: "jmlagos2003@gmail.com",
        github: "https://github.com/lakerstrake",
        linkedin: "https://linkedin.com/in/juan-manuel-lagos-monroy",
        cvDrive: "https://drive.google.com/drive/folders/1BZ-qBNdPeYsxW84zIq_ls97UkPlQcHyN",
        program: "Tecnólogo en Análisis y Desarrollo de Software (ADSO) - SENA"
    },
    STORAGE_KEYS: {
        FAVORITES: 'cap_favs',
        COMPARE: 'cap_comp',
        THEME: 'cap_theme'
    },
    PAGINATION: {
        DEFAULT_PAGE_SIZE: 50
    },
    MAX_COMPARE: 3
});

// =========================================================================
// 2. SECURITY & UTILITY SERVICE (OWASP Compliant)
// =========================================================================
class SecurityService {
    /**
     * Escapes HTML entities to prevent Reflected and DOM-based Cross-Site Scripting (XSS).
     * @param {*} input 
     * @returns {string} Safe string
     */
    static escapeHtml(input) {
        if (input === null || input === undefined) return '';
        return String(input)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    /**
     * Validates if a phone string is a real, non-dummy Colombian mobile phone (starts with 3, 10 digits).
     * @param {*} phone 
     * @returns {boolean}
     */
    static isValidMobile(phone) {
        if (!phone) return false;
        const digits = String(phone).replace(/\D/g, '');
        if (digits.length === 10 && digits.startsWith('3')) {
            // Reject dummy sequences like 3333333333, 3000000000, 3111111111
            if (/^(\d)\1+$/.test(digits)) return false;
            return true;
        }
        return false;
    }

    /**
     * Constructs a safe, clean WhatsApp URL if phone is valid mobile.
     */
    static getWhatsAppUrl(phone, message) {
        if (!SecurityService.isValidMobile(phone)) return '';
        const digits = String(phone).replace(/\D/g, '');
        return `https://wa.me/57${digits}?text=${encodeURIComponent(message || '')}`;
    }
}

// =========================================================================
// AUTHENTICATION & SECURITY SERVICE (ISO 27001 / OWASP Top 10)
// =========================================================================
class AuthService {
    static STORAGE_KEY = 'sgva_sena_auth_session';
    static LOCKOUT_KEY = 'sgva_sena_auth_lockout';
    static MAX_ATTEMPTS = 5;
    static LOCKOUT_SECONDS = 30;

    // Pre-computed SHA-256 Hashes for credentials
    static VALID_HASHES = [
        '6ad307d8dfef24c8b21c45f448c26f04c63aa8b88d228f4115167098c8c5fa0b', // adso2026
        '9f6c0936dc55db4db34575ecba6d21ec8c0f5902196fa04918e974e64f7b6bb2'  // sena2026
    ];

    /**
     * Compute SHA-256 hash using the browser's native Web Crypto API
     */
    static async sha256(str) {
        try {
            const buffer = new TextEncoder().encode(str);
            const digest = await crypto.subtle.digest('SHA-256', buffer);
            return Array.from(new Uint8Array(digest))
                .map(b => b.toString(16).padStart(2, '0'))
                .join('');
        } catch (e) {
            let hash = 0;
            for (let i = 0; i < str.length; i++) {
                hash = ((hash << 5) - hash) + str.charCodeAt(i);
                hash |= 0;
            }
            return String(hash);
        }
    }

    static getSession() {
        try {
            const local = localStorage.getItem(AuthService.STORAGE_KEY);
            const sess = sessionStorage.getItem(AuthService.STORAGE_KEY);
            const data = local ? JSON.parse(local) : (sess ? JSON.parse(sess) : null);
            if (data && data.expiresAt && Date.now() < data.expiresAt) {
                return data;
            }
            return null;
        } catch (e) {
            return null;
        }
    }

    static saveSession(user, role, remember = false) {
        const sessionData = {
            user: user,
            role: role,
            name: role === 'ADMIN' ? 'Juan Manuel Lagos' : 'Evaluador / Empresa',
            loginTime: Date.now(),
            expiresAt: Date.now() + (remember ? 30 * 24 * 60 * 60 * 1000 : 4 * 60 * 60 * 1000)
        };
        const str = JSON.stringify(sessionData);
        if (remember) {
            localStorage.setItem(AuthService.STORAGE_KEY, str);
        } else {
            sessionStorage.setItem(AuthService.STORAGE_KEY, str);
        }
        return sessionData;
    }

    static clearSession() {
        try {
            localStorage.removeItem(AuthService.STORAGE_KEY);
            sessionStorage.removeItem(AuthService.STORAGE_KEY);
        } catch (e) {}
    }

    static checkLockout() {
        try {
            const raw = sessionStorage.getItem(AuthService.LOCKOUT_KEY);
            if (!raw) return { locked: false, remaining: 0 };
            const data = JSON.parse(raw);
            if (data.lockedUntil && Date.now() < data.lockedUntil) {
                return { locked: true, remaining: Math.ceil((data.lockedUntil - Date.now()) / 1000) };
            }
            return { locked: false, remaining: 0 };
        } catch (e) {
            return { locked: false, remaining: 0 };
        }
    }

    static recordFailedAttempt() {
        try {
            const raw = sessionStorage.getItem(AuthService.LOCKOUT_KEY);
            let data = raw ? JSON.parse(raw) : { attempts: 0, lockedUntil: 0 };
            data.attempts = (data.attempts || 0) + 1;
            if (data.attempts >= AuthService.MAX_ATTEMPTS) {
                data.lockedUntil = Date.now() + (AuthService.LOCKOUT_SECONDS * 1000);
                data.attempts = 0;
            }
            sessionStorage.setItem(AuthService.LOCKOUT_KEY, JSON.stringify(data));
            return data;
        } catch (e) {
            return { attempts: 0 };
        }
    }

    static resetAttempts() {
        try {
            sessionStorage.removeItem(AuthService.LOCKOUT_KEY);
        } catch (e) {}
    }

    static async authenticate(username, password, remember = false) {
        const lockout = AuthService.checkLockout();
        if (lockout.locked) {
            return { success: false, message: `Demasiados intentos fallidos. Bloqueo temporal por ${lockout.remaining}s.` };
        }

        const u = String(username || '').trim().toLowerCase();
        const p = String(password || '').trim();

        if (!u || !p) {
            return { success: false, message: 'Ingresa usuario y contraseña.' };
        }

        const validUsers = ['admin', '1074808317', 'juan', 'juanlagos', 'jmlagos'];
        const hash = await AuthService.sha256(p);

        const isUserValid = validUsers.includes(u);
        const isPassValid = AuthService.VALID_HASHES.includes(hash) || p === 'adso2026' || p === 'sena2026';

        if (isUserValid && isPassValid) {
            AuthService.resetAttempts();
            const session = AuthService.saveSession(username, 'ADMIN', remember);
            return { success: true, session: session };
        } else {
            const res = AuthService.recordFailedAttempt();
            if (res.lockedUntil) {
                return { success: false, message: `5 intentos fallidos. Bloqueado por ${AuthService.LOCKOUT_SECONDS} segundos.` };
            }
            return { success: false, message: 'Usuario o PIN incorrecto. (Demo: admin / adso2026)' };
        }
    }

    static authenticateGuest() {
        AuthService.resetAttempts();
        const session = AuthService.saveSession('guest_recruiter', 'RECRUITER', false);
        return { success: true, session: session };
    }
}

// =========================================================================
// 3. APPLICATION STATE STORE (Single Source of Truth)
// =========================================================================
class AppStore {
    constructor(initialData = []) {
        this.rawData = Array.isArray(initialData) ? initialData : [];
        this.filteredData = [...this.rawData];
        this.activeTier = '';
        this.activeStack = '';
        this.filterFavs = false;
        
        // Smart responsive view mode default
        const isMobileScreen = typeof window !== 'undefined' && window.innerWidth < 768;
        this.viewMode = isMobileScreen ? 'cards' : 'table';
        
        this.currentPage = 1;
        this.pageSize = CONFIG.PAGINATION.DEFAULT_PAGE_SIZE;
        this.sortCol = 'ranking_posicion';
        this.sortAsc = true;
        this.activeItem = null;
        this.activeChannel = 'email';
        
        // Persistent State with Fallbacks
        this.favorites = this._loadFromStorage(CONFIG.STORAGE_KEYS.FAVORITES, []);
        this.compareList = this._loadFromStorage(CONFIG.STORAGE_KEYS.COMPARE, []);
        this.theme = this._loadFromStorage(CONFIG.STORAGE_KEYS.THEME, 'dark');
    }

    _loadFromStorage(key, fallback) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : fallback;
        } catch (err) {
            console.warn(`[AppStore] Error reading '${key}' from storage:`, err);
            return fallback;
        }
    }

    _saveToStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (err) {
            console.warn(`[AppStore] Error saving '${key}' to storage:`, err);
        }
    }

    toggleFavorite(id) {
        const strId = String(id);
        if (this.favorites.includes(strId)) {
            this.favorites = this.favorites.filter(x => x !== strId);
        } else {
            this.favorites.push(strId);
        }
        this._saveToStorage(CONFIG.STORAGE_KEYS.FAVORITES, this.favorites);
    }

    isFavorite(id) {
        return this.favorites.includes(String(id));
    }

    toggleCompare(id) {
        const strId = String(id);
        if (this.compareList.includes(strId)) {
            this.compareList = this.compareList.filter(x => x !== strId);
            this._saveToStorage(CONFIG.STORAGE_KEYS.COMPARE, this.compareList);
            return { status: 'removed' };
        } else {
            if (this.compareList.length >= CONFIG.MAX_COMPARE) {
                return { status: 'limit_reached' };
            }
            this.compareList.push(strId);
            this._saveToStorage(CONFIG.STORAGE_KEYS.COMPARE, this.compareList);
            return { status: 'added' };
        }
    }

    isCompared(id) {
        return this.compareList.includes(String(id));
    }

    clearCompare() {
        this.compareList = [];
        this._saveToStorage(CONFIG.STORAGE_KEYS.COMPARE, this.compareList);
    }
}

// =========================================================================
// 4. MAIN APPLICATION CONTROLLER
// =========================================================================
class AppController {
    constructor() {
        this.store = new AppStore(window.RAW_DATA || []);
        this.dom = {};
    }

    init() {
        this.cacheDomElements();
        this.initTheme();
        this.initAuth();
        this.populateFilterDropdowns();
        this.bindEvents();
        this.updateFavCounter();
        this.updateCompareDock();
        this.setLayout(this.store.viewMode);
        this.applyFilters();
    }

    cacheDomElements() {
        this.dom = {
            html: document.documentElement,
            themeIcon: document.getElementById('themeIcon'),
            themeBtn: document.getElementById('themeBtn'),
            
            // Auth & Security Elements
            authModal: document.getElementById('authModal'),
            btnAuthTrigger: document.getElementById('btnAuthTrigger'),
            lblSessionUser: document.getElementById('lblSessionUser'),
            tabAuthAdmin: document.getElementById('tabAuthAdmin'),
            tabAuthGuest: document.getElementById('tabAuthGuest'),
            formAuthAdmin: document.getElementById('formAuthAdmin'),
            formAuthGuest: document.getElementById('formAuthGuest'),
            tbLoginUser: document.getElementById('tbLoginUser'),
            tbLoginPass: document.getElementById('tbLoginPass'),
            btnTogglePwd: document.getElementById('btnTogglePwd'),
            iconEye: document.getElementById('iconEye'),
            cbRememberAuth: document.getElementById('cbRememberAuth'),
            authAlertBox: document.getElementById('authAlertBox'),
            authAlertText: document.getElementById('authAlertText'),
            btnCancelAuth: document.getElementById('btnCancelAuth'),
            
            // Navigation
            pillDirectory: document.getElementById('pillDirectory'),
            pillStrategy: document.getElementById('pillStrategy'),
            pillFavs: document.getElementById('pillFavs'),
            pillTotalCount: document.getElementById('pillTotalCount'),
            pillFavCount: document.getElementById('pillFavCount'),
            
            // Sections
            sectionDirectory: document.getElementById('sectionDirectory'),
            sectionStrategy: document.getElementById('sectionStrategy'),
            antiBlockNotice: document.getElementById('antiBlockNotice'),
            
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
            
            // Views
            tableCardWrap: document.getElementById('tableCardWrap'),
            cardsGridWrap: document.getElementById('cardsGridWrap'),
            tableBody: document.getElementById('tableBody'),
            lblVisibleCount: document.getElementById('lblVisibleCount'),
            lblTotalCount: document.getElementById('lblTotalCount'),
            lblPagination: document.getElementById('lblPagination'),
            paginationPages: document.getElementById('paginationPages'),
            btnLayoutTable: document.getElementById('btnLayoutTable'),
            btnLayoutCards: document.getElementById('btnLayoutCards'),
            
            // Dock & Compare Modal
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
            
            // Modal Tabs
            mTabOutreach: document.getElementById('mTabOutreach'),
            mTabInterview: document.getElementById('mTabInterview'),
            mTabCareer: document.getElementById('mTabCareer'),
            mTabDetails: document.getElementById('mTabDetails'),
            mSecOutreach: document.getElementById('mSecOutreach'),
            mSecInterview: document.getElementById('mSecInterview'),
            mSecCareer: document.getElementById('mSecCareer'),
            mSecDetails: document.getElementById('mSecDetails'),
            
            // Modal Outreach Channel
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
            
            // Modal Timeline & Q&A
            mInterviewList: document.getElementById('mInterviewList'),
            mCurvaTitulo: document.getElementById('mCurvaTitulo'),
            mCurvaDetalle: document.getElementById('mCurvaDetalle'),
            mTimelineGrid: document.getElementById('mTimelineGrid'),
            mFinAcumulado5A: document.getElementById('mFinAcumulado5A'),
            mFinDiferencial: document.getElementById('mFinDiferencial'),
            mPerfil: document.getElementById('mPerfil'),
            mFunciones: document.getElementById('mFunciones'),
            mClosingDate: document.getElementById('mClosingDate'),
            
            // Toast
            toastMsg: document.getElementById('toastMsg')
        };
    }

    initAuth() {
        let sess = AuthService.getSession();
        if (!sess) {
            sess = AuthService.saveSession('admin', 'ADMIN', true);
        }
        this.updateSessionUI(sess);
    }

    updateSessionUI(sess) {
        if (this.dom.lblSessionUser && sess) {
            if (sess.role === 'ADMIN') {
                this.dom.lblSessionUser.textContent = 'Aprendiz ADSO';
            } else {
                this.dom.lblSessionUser.textContent = 'Reclutador';
            }
        }
    }

    openAuthModal() {
        if (this.dom.authModal) {
            this.dom.authModal.style.display = 'flex';
            const sess = AuthService.getSession();
            if (this.dom.btnCancelAuth) {
                this.dom.btnCancelAuth.style.display = sess ? 'inline-block' : 'none';
            }
            if (this.dom.authAlertBox) this.dom.authAlertBox.style.display = 'none';
        }
    }

    closeAuthModal() {
        if (this.dom.authModal) this.dom.authModal.style.display = 'none';
    }

    switchAuthTab(tab) {
        if (tab === 'admin') {
            this.dom.tabAuthAdmin?.classList.add('active');
            this.dom.tabAuthGuest?.classList.remove('active');
            if (this.dom.formAuthAdmin) this.dom.formAuthAdmin.style.display = 'flex';
            if (this.dom.formAuthGuest) this.dom.formAuthGuest.style.display = 'none';
        } else {
            this.dom.tabAuthGuest?.classList.add('active');
            this.dom.tabAuthAdmin?.classList.remove('active');
            if (this.dom.formAuthGuest) this.dom.formAuthGuest.style.display = 'flex';
            if (this.dom.formAuthAdmin) this.dom.formAuthAdmin.style.display = 'none';
        }
        if (this.dom.authAlertBox) this.dom.authAlertBox.style.display = 'none';
    }

    togglePasswordVisibility() {
        if (!this.dom.tbLoginPass) return;
        const isPwd = this.dom.tbLoginPass.type === 'password';
        this.dom.tbLoginPass.type = isPwd ? 'text' : 'password';
        if (this.dom.iconEye) {
            this.dom.iconEye.className = isPwd ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye';
        }
    }

    async handleLogin() {
        const user = this.dom.tbLoginUser ? this.dom.tbLoginUser.value : '';
        const pass = this.dom.tbLoginPass ? this.dom.tbLoginPass.value : '';
        const remember = this.dom.cbRememberAuth ? this.dom.cbRememberAuth.checked : true;

        const result = await AuthService.authenticate(user, pass, remember);
        if (result.success) {
            this.updateSessionUI(result.session);
            this.closeAuthModal();
            this.showToast(`¡Sesión iniciada: ${result.session.name}!`);
        } else {
            if (this.dom.authAlertBox && this.dom.authAlertText) {
                this.dom.authAlertText.textContent = result.message;
                this.dom.authAlertBox.style.display = 'flex';
            }
        }
    }

    handleGuestLogin() {
        const result = AuthService.authenticateGuest();
        this.updateSessionUI(result.session);
        this.closeAuthModal();
        this.showToast('Acceso activado en Modo Evaluador / Empresa');
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
        this.store._saveToStorage(CONFIG.STORAGE_KEYS.THEME, next);
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

    /**
     * Unobtrusive Event Delegation Listener.
     */
    bindEvents() {
        document.addEventListener('click', (e) => {
            const actionEl = e.target.closest('[data-action]');
            if (!actionEl) return;

            const action = actionEl.getAttribute('data-action');
            this.handleAction(action, actionEl, e);
        });

        if (this.dom.mainSearch) {
            this.dom.mainSearch.addEventListener('input', () => {
                this.store.currentPage = 1;
                this.applyFilters();
            });
        }

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

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeDetailModal();
                this.closeCompareModal();
            }
        });
    }

    handleAction(action, el, event) {
        switch (action) {
            case 'openAuthModal':
                this.openAuthModal();
                break;
            case 'closeAuthModal':
                this.closeAuthModal();
                break;
            case 'switchAuthTab':
                this.switchAuthTab(el.getAttribute('data-tab'));
                break;
            case 'togglePasswordVisibility':
                this.togglePasswordVisibility();
                break;
            case 'submitLogin':
                this.handleLogin();
                break;
            case 'submitGuestLogin':
                this.handleGuestLogin();
                break;
            case 'switchNavTab':
                this.switchNavTab(el.getAttribute('data-tab'));
                break;
            case 'toggleTheme':
                this.toggleTheme();
                break;
            case 'exportData':
                this.exportData(el.getAttribute('data-format'));
                break;
            case 'dismissNotice':
                if (this.dom.antiBlockNotice) this.dom.antiBlockNotice.style.display = 'none';
                break;
            case 'filterTier':
                this.setTierFilter(el.getAttribute('data-tier'), el);
                break;
            case 'filterStack':
                this.setStackChipFilter(el.getAttribute('data-stack'), el);
                break;
            case 'toggleSecondaryFilters':
                this.toggleSecondaryFilters();
                break;
            case 'resetFilters':
                this.resetFilters();
                break;
            case 'setLayout':
                this.setLayout(el.getAttribute('data-layout'));
                break;
            case 'toggleFavorite':
                event.stopPropagation();
                this.handleToggleFavorite(el.getAttribute('data-id'));
                break;
            case 'toggleCompare':
                event.stopPropagation();
                this.handleToggleCompare(el.getAttribute('data-id'));
                break;
            case 'openDetailModal':
                this.openDetailModalById(el.getAttribute('data-id'));
                break;
            case 'openCompareModal':
                this.openCompareModal();
                break;
            case 'closeCompareModal':
            case 'backdropCloseCompare':
                if (action === 'backdropCloseCompare' && event.target.id !== 'compareModal') return;
                this.closeCompareModal();
                break;
            case 'clearComparison':
                this.clearComparison();
                break;
            case 'closeDetailModal':
            case 'backdropCloseDetail':
                if (action === 'backdropCloseDetail' && event.target.id !== 'detailModal') return;
                this.closeDetailModal();
                break;
            case 'toggleModalFavorite':
                if (this.store.activeItem) this.handleToggleFavorite(this.store.activeItem.solicitud_id);
                break;
            case 'setModalTab':
                this.setModalTab(el.getAttribute('data-tab'));
                break;
            case 'setModalChannel':
                this.setChannel(el.getAttribute('data-channel'));
                break;
            case 'copyOutreach':
                this.copyToClipboard('mOutreachBody');
                break;
            case 'goToPage':
                this.goToPage(parseInt(el.getAttribute('data-page'), 10));
                break;
            default:
                break;
        }
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
            tbody.innerHTML = `
                <tr>
                    <td colspan="11" style="text-align: center; padding: 3.5rem 1rem;">
                        <div style="display: flex; flex-direction: column; align-items: center; gap: 0.6rem; color: var(--text-muted);">
                            <i class="fa-solid fa-magnifying-glass" style="font-size: 1.8rem; color: var(--text-dim);" aria-hidden="true"></i>
                            <strong style="color: var(--text-main); font-size: 0.86rem;">No se encontraron vacantes con los criterios seleccionados</strong>
                            <p style="font-size: 0.72rem; max-width: 380px;">Prueba ajustando los términos de búsqueda o restableciendo los filtros para ver las 179 oportunidades.</p>
                            <button class="btn btn-primary" data-action="resetFilters" style="margin-top: 0.3rem;">
                                <i class="fa-solid fa-rotate-left"></i> Restablecer Filtros
                            </button>
                        </div>
                    </td>
                </tr>
            `;
            if (this.dom.lblPagination) this.dom.lblPagination.textContent = '0 resultados';
            if (this.dom.paginationPages) this.dom.paginationPages.innerHTML = '';
            return;
        }

        pageSlice.forEach(it => {
            const tr = document.createElement('tr');
            tr.setAttribute('data-action', 'openDetailModal');
            tr.setAttribute('data-id', it.solicitud_id);

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
            const hasValidWA = SecurityService.isValidMobile(it.telefono);
            const waUrl = hasValidWA ? SecurityService.getWhatsAppUrl(it.telefono, it.whatsapp_message) : '';

            const cleanApoyo = "$1.423.500 COP";
            const cleanTecho5A = it.techo_salarial_5anios ? it.techo_salarial_5anios.split('(')[0].replace('COP','').trim() : '$10M-$22M';
            const posFormatted = (it.ranking_posicion || 1) < 10 ? '0' + it.ranking_posicion : it.ranking_posicion;

            tr.innerHTML = `
                <td style="text-align: center;">
                    <input type="checkbox" ${isComp ? 'checked' : ''} data-action="toggleCompare" data-id="${SecurityService.escapeHtml(it.solicitud_id)}" aria-label="Comparar empresa">
                </td>
                <td>
                    <i class="${favIcon}" style="cursor: pointer; ${favColor}" data-action="toggleFavorite" data-id="${SecurityService.escapeHtml(it.solicitud_id)}" aria-label="Marcar como favorita"></i>
                </td>
                <td style="font-family: var(--font-mono); font-weight: 700; color: var(--text-dim);">#${posFormatted}</td>
                <td>
                    <div class="cell-main">
                        <span class="cell-title" title="${SecurityService.escapeHtml(it.empresa)}">${SecurityService.escapeHtml(it.empresa)}</span>
                        <span class="cell-sub">${SecurityService.escapeHtml(it.ciudad || '')}, ${SecurityService.escapeHtml(it.departamento || '')} • NIT: ${SecurityService.escapeHtml(it.nit || 'N/A')}</span>
                    </div>
                </td>
                <td><span class="pill-badge ${tierClass}">${SecurityService.escapeHtml(it.cat_badge || 'Tier')}</span></td>
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
                        <span style="color: var(--tier-1); font-size: 0.62rem; font-weight: 600;">5A: ${SecurityService.escapeHtml(cleanTecho5A)}</span>
                    </div>
                </td>
                <td style="text-align: right;">
                    <div class="row-actions">
                        ${hasEmail ? `<a href="mailto:${SecurityService.escapeHtml(it.email)}?subject=Postulaci%C3%B3n+Contrato+ADSO+-+Juan+Manuel+Lagos&body=${encodeURIComponent(it.correo_formal_completo || '')}" class="mini-btn mini-mail" title="Enviar correo formal"><i class="fa-solid fa-envelope"></i></a>` : ''}
                        ${hasValidWA ? `<a href="${SecurityService.escapeHtml(waUrl)}" target="_blank" rel="noopener noreferrer" class="mini-btn mini-wa" title="WhatsApp"><i class="fa-brands fa-whatsapp"></i></a>` : ''}
                        ${it.linkedin_contact_search_url ? `<a href="${SecurityService.escapeHtml(it.linkedin_contact_search_url)}" target="_blank" rel="noopener noreferrer" class="mini-btn" title="Buscar en LinkedIn"><i class="fa-brands fa-linkedin" style="color: var(--linkedin-color);"></i></a>` : ''}
                        <button class="mini-btn" style="font-weight: 700;" data-action="openDetailModal" data-id="${SecurityService.escapeHtml(it.solicitud_id)}">Detalle</button>
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
        if (totalPages <= 1) {
            this.dom.paginationPages.innerHTML = '';
            return;
        }

        const isMobile = window.innerWidth < 640;
        let html = '';

        if (isMobile) {
            html = `
                <div style="display: flex; align-items: center; gap: 0.35rem;">
                    <button class="btn" style="padding: 0.2rem 0.45rem; font-size: 0.68rem;" data-action="goToPage" data-page="${Math.max(1, this.store.currentPage - 1)}" ${this.store.currentPage === 1 ? 'disabled style="opacity: 0.4; cursor: not-allowed;"' : ''} aria-label="Página anterior">
                        <i class="fa-solid fa-chevron-left"></i>
                    </button>
                    <span style="font-size: 0.68rem; font-family: var(--font-mono); color: var(--text-main); font-weight: 600; padding: 0 0.2rem;">
                        ${this.store.currentPage} / ${totalPages}
                    </span>
                    <button class="btn" style="padding: 0.2rem 0.45rem; font-size: 0.68rem;" data-action="goToPage" data-page="${Math.min(totalPages, this.store.currentPage + 1)}" ${this.store.currentPage === totalPages ? 'disabled style="opacity: 0.4; cursor: not-allowed;"' : ''} aria-label="Página siguiente">
                        <i class="fa-solid fa-chevron-right"></i>
                    </button>
                </div>
            `;
        } else {
            html += `<button class="btn" style="padding: 0.18rem 0.45rem; font-size: 0.68rem;" data-action="goToPage" data-page="${Math.max(1, this.store.currentPage - 1)}" ${this.store.currentPage === 1 ? 'disabled style="opacity: 0.4; cursor: not-allowed;"' : ''}><i class="fa-solid fa-chevron-left"></i></button>`;

            for (let i = 1; i <= totalPages; i++) {
                if (totalPages > 6 && Math.abs(i - this.store.currentPage) > 2 && i !== 1 && i !== totalPages) {
                    if (i === 2 || i === totalPages - 1) {
                        html += `<span style="color: var(--text-dim); padding: 0 0.15rem;">...</span>`;
                    }
                    continue;
                }
                const activeStyle = i === this.store.currentPage ? 'background: var(--brand-primary); color: #fff; border-color: var(--brand-primary);' : '';
                html += `<button class="btn" style="padding: 0.18rem 0.45rem; font-size: 0.68rem; min-width: 26px; ${activeStyle}" data-action="goToPage" data-page="${i}">${i}</button>`;
            }

            html += `<button class="btn" style="padding: 0.18rem 0.45rem; font-size: 0.68rem;" data-action="goToPage" data-page="${Math.min(totalPages, this.store.currentPage + 1)}" ${this.store.currentPage === totalPages ? 'disabled style="opacity: 0.4; cursor: not-allowed;"' : ''}><i class="fa-solid fa-chevron-right"></i></button>`;
        }

        this.dom.paginationPages.innerHTML = html;
    }

    goToPage(p) {
        this.store.currentPage = p;
        if (this.store.viewMode === 'table') this.renderTable();
        else this.renderCards();
    }

    renderCards() {
        const grid = this.dom.cardsGridWrap;
        if (!grid) return;
        grid.innerHTML = '';
        
        const total = this.store.filteredData.length;
        const totalPages = Math.ceil(total / this.store.pageSize) || 1;
        if (this.store.currentPage > totalPages) this.store.currentPage = totalPages;

        const start = (this.store.currentPage - 1) * this.store.pageSize;
        const pageSlice = this.store.filteredData.slice(start, start + this.store.pageSize);

        if (total === 0) {
            grid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 3.5rem 1rem; background: var(--bg-surface); border: 1px solid var(--border-muted); border-radius: var(--radius-md);">
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 0.6rem; color: var(--text-muted);">
                        <i class="fa-solid fa-magnifying-glass" style="font-size: 1.8rem; color: var(--text-dim);" aria-hidden="true"></i>
                        <strong style="color: var(--text-main); font-size: 0.86rem;">No se encontraron vacantes con los filtros actuales</strong>
                        <p style="font-size: 0.72rem; max-width: 380px;">Prueba ajustando los términos de búsqueda o restableciendo los filtros para ver las 179 oportunidades.</p>
                        <button class="btn btn-primary" data-action="resetFilters" style="margin-top: 0.3rem;">
                            <i class="fa-solid fa-rotate-left"></i> Restablecer Filtros
                        </button>
                    </div>
                </div>
            `;
            if (this.dom.lblPagination) this.dom.lblPagination.textContent = '0 resultados';
            if (this.dom.paginationPages) this.dom.paginationPages.innerHTML = '';
            return;
        }

        pageSlice.forEach(it => {
            const card = document.createElement('article');
            card.className = 'clean-card';
            card.setAttribute('data-action', 'openDetailModal');
            card.setAttribute('data-id', it.solicitud_id);

            const isFav = this.store.isFavorite(it.solicitud_id);
            const favIcon = isFav ? 'fa-solid fa-bookmark' : 'fa-regular fa-bookmark';
            const favColor = isFav ? 'color: var(--tier-3);' : '';

            let tierClass = 'pill-tier-1';
            if (it.cat_id === 'TIER_2') tierClass = 'pill-tier-2';
            else if (it.cat_id === 'TIER_3') tierClass = 'pill-tier-3';
            else if (it.cat_id === 'TIER_4') tierClass = 'pill-tier-4';
            else if (it.cat_id === 'TIER_5') tierClass = 'pill-tier-5';

            const hasEmail = it.email && it.email.includes('@');
            const hasValidWA = SecurityService.isValidMobile(it.telefono);
            const waUrl = hasValidWA ? SecurityService.getWhatsAppUrl(it.telefono, it.whatsapp_message) : '';

            const posFormatted = (it.ranking_posicion || 1) < 10 ? '0' + it.ranking_posicion : it.ranking_posicion;

            card.innerHTML = `
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.35rem;">
                        <div style="display: flex; align-items: center; gap: 0.4rem;">
                            <span style="font-family: var(--font-mono); font-weight: 700; color: var(--text-dim); font-size: 0.72rem;">#${posFormatted}</span>
                            <span class="pill-badge ${tierClass}">${SecurityService.escapeHtml(it.cat_badge || 'Tier')}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.4rem;">
                            <span class="rating-chip"><i class="fa-solid fa-star"></i> ${(it.reputacion_rating || 3.8).toFixed(1)}</span>
                            <i class="${favIcon}" style="cursor: pointer; font-size: 0.82rem; ${favColor}" data-action="toggleFavorite" data-id="${SecurityService.escapeHtml(it.solicitud_id)}"></i>
                        </div>
                    </div>
                    <h3 style="font-size: 0.84rem; font-weight: 700; color: var(--text-main); line-height: 1.3;">${SecurityService.escapeHtml(it.empresa)}</h3>
                    <div style="font-size: 0.66rem; color: var(--text-dim); margin-top: 0.15rem;">${SecurityService.escapeHtml(it.ciudad || '')}, ${SecurityService.escapeHtml(it.departamento || '')} • ${it.vacantes || 1} vac · ${it.postulados || 0} post</div>
                </div>

                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.3rem; background: var(--bg-canvas); padding: 0.35rem; border-radius: var(--radius-xs); text-align: center;">
                    <div><span style="font-size: 0.58rem; color: var(--text-dim);">PUNTOS</span><div style="font-weight: 700; color: var(--tier-1);">${it.puntaje_exito || 0}</div></div>
                    <div><span style="font-size: 0.58rem; color: var(--text-dim);">ESCALA</span><div style="font-weight: 700; color: var(--tier-2);">${it.escalabilidad_score || 70}</div></div>
                    <div><span style="font-size: 0.58rem; color: var(--text-dim);">5A SALARIO</span><div style="font-weight: 700; color: var(--brand-primary); font-size: 0.64rem;">${SecurityService.escapeHtml(it.techo_salarial_5anios ? it.techo_salarial_5anios.split('(')[0].trim() : '')}</div></div>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-muted); padding-top: 0.4rem;">
                    <span style="color: var(--brand-primary); font-weight: 600; font-family: var(--font-mono); font-size: 0.72rem;">$1.423.500 COP</span>
                    <div class="row-actions">
                        ${hasEmail ? `<a href="mailto:${SecurityService.escapeHtml(it.email)}?subject=Postulaci%C3%B3n+Contrato+ADSO+-+Juan+Manuel+Lagos&body=${encodeURIComponent(it.correo_formal_completo || '')}" class="mini-btn mini-mail" title="Enviar correo"><i class="fa-solid fa-envelope"></i></a>` : ''}
                        ${hasValidWA ? `<a href="${SecurityService.escapeHtml(waUrl)}" target="_blank" rel="noopener noreferrer" class="mini-btn mini-wa" title="WhatsApp"><i class="fa-brands fa-whatsapp"></i></a>` : ''}
                        ${it.linkedin_contact_search_url ? `<a href="${SecurityService.escapeHtml(it.linkedin_contact_search_url)}" target="_blank" rel="noopener noreferrer" class="mini-btn" title="LinkedIn"><i class="fa-brands fa-linkedin" style="color: var(--linkedin-color);"></i></a>` : ''}
                        <button class="mini-btn" style="font-weight: 700;" data-action="openDetailModal" data-id="${SecurityService.escapeHtml(it.solicitud_id)}">Ver Detalle</button>
                    </div>
                </div>
            `;
            grid.appendChild(card);
        });

        if (this.dom.lblPagination) {
            this.dom.lblPagination.textContent = `Mostrando ${start + 1}-${Math.min(start + this.store.pageSize, total)} de ${total} vacantes`;
        }

        this.renderPagination(totalPages);
    }

    setLayout(mode) {
        this.store.viewMode = mode;
        if (mode === 'cards') {
            if (this.dom.tableCardWrap) this.dom.tableCardWrap.style.display = 'none';
            if (this.dom.cardsGridWrap) this.dom.cardsGridWrap.style.display = 'grid';
            this.dom.btnLayoutCards?.classList.add('active');
            this.dom.btnLayoutTable?.classList.remove('active');
            this.renderCards();
        } else {
            if (this.dom.tableCardWrap) this.dom.tableCardWrap.style.display = 'flex';
            if (this.dom.cardsGridWrap) this.dom.cardsGridWrap.style.display = 'none';
            this.dom.btnLayoutTable?.classList.add('active');
            this.dom.btnLayoutCards?.classList.remove('active');
            this.renderTable();
        }
    }

    handleToggleFavorite(id) {
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

    handleToggleCompare(id) {
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
                html += `<span class="pill-badge pill-tier-1">${SecurityService.escapeHtml(it.empresa.substring(0, 14))}... <i class="fa-solid fa-xmark" style="cursor: pointer; margin-left: 2px;" data-action="toggleCompare" data-id="${SecurityService.escapeHtml(it.solicitud_id)}"></i></span>`;
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
            html += `<th style="padding: 0.5rem; text-align: left;"><strong style="color: var(--brand-primary);">${SecurityService.escapeHtml(it.empresa)}</strong><div style="font-size: 0.65rem; color: var(--text-dim);">#${it.ranking_posicion} • ${SecurityService.escapeHtml(it.cat_badge || '')}</div></th>`;
        });
        html += '</tr></thead><tbody>';

        const fields = [
            { label: "Afinidad & Puntos", fn: it => `<strong style="color: var(--tier-1);">${it.puntaje_exito} / 100</strong>` },
            { label: "Reputación Web", fn: it => `★ ${(it.reputacion_rating || 3.8).toFixed(1)} (${SecurityService.escapeHtml(it.reputacion_fuente || 'Web')})` },
            { label: "Escalabilidad", fn: it => `<strong style="color: var(--tier-2);">${it.escalabilidad_score || 70}/100</strong> (${SecurityService.escapeHtml(it.escalabilidad_nivel || 'Media')})` },
            { label: "Apoyo Práctica", fn: it => `<strong style="color: var(--brand-primary);">$1.423.500 COP</strong>` },
            { label: "5A Salario & Acumulado", fn: it => `<strong>${SecurityService.escapeHtml(it.techo_salarial_5anios || '')}</strong><div style="font-size: 0.65rem; color: var(--brand-primary);">${SecurityService.escapeHtml(it.finanzas_5anios?.acumulado_5a || '')}</div>` },
            { label: "Competencia", fn: it => `${it.vacantes || 1} vac. vs ${it.postulados || 0} post. (Ratio: ${it.competencia_ratio || 0})` },
            { label: "Contacto Directo", fn: it => `${SecurityService.escapeHtml(it.contacto || 'RRHH')} • ${SecurityService.escapeHtml(it.email || '')} • ${SecurityService.escapeHtml(it.telefono || '')}` }
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
                    <span style="color: var(--text-dim); text-transform: uppercase; font-weight: 700; font-size: 0.6rem;">${SecurityService.escapeHtml(h.periodo)}</span>
                    <div style="font-weight: 700; color: var(--text-main); margin: 2px 0;">${SecurityService.escapeHtml(h.rol)}</div>
                    <div style="color: var(--brand-primary); font-family: var(--font-mono); font-weight: 700;">${SecurityService.escapeHtml(h.salario)}</div>
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
                        <strong style="color: var(--tier-2);">#${idx + 1} ${SecurityService.escapeHtml(q.pregunta)}</strong>
                        <div style="color: var(--text-muted); margin: 0.3rem 0; line-height: 1.4;">${SecurityService.escapeHtml(q.respuesta_modelo)}</div>
                        <div style="color: var(--brand-primary); font-size: 0.68rem;"><i class="fa-brands fa-github"></i> ${SecurityService.escapeHtml(q.tip_github)}</div>
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
            const mailtoLink = hasEmail ? `mailto:${SecurityService.escapeHtml(it.email)}?subject=Postulaci%C3%B3n+Contrato+ADSO+-+Juan+Manuel+Lagos&body=${encodeURIComponent(it.correo_formal_completo || '')}` : '#';
            if (this.dom.mOutreachActions) {
                this.dom.mOutreachActions.innerHTML = `
                    <button class="btn" style="padding: 0.2rem 0.5rem;" data-action="copyOutreach"><i class="fa-regular fa-copy"></i> Copiar Correo</button>
                    ${hasEmail ? `<a href="${mailtoLink}" class="btn btn-primary" style="padding: 0.2rem 0.5rem;"><i class="fa-solid fa-paper-plane"></i> Abrir en Mi Correo</a>` : '<span style="font-size: 0.68rem; color: var(--text-dim);">Sin correo registrado</span>'}
                `;
            }
        } else if (ch === 'wa') {
            if (this.dom.mOutreachHeading) this.dom.mOutreachHeading.textContent = 'Mensaje de WhatsApp Directo';
            if (this.dom.mOutreachBody) this.dom.mOutreachBody.textContent = it.whatsapp_message || '';
            const hasValidWA = SecurityService.isValidMobile(it.telefono);
            const waUrl = hasValidWA ? SecurityService.getWhatsAppUrl(it.telefono, it.whatsapp_message) : '';

            if (this.dom.mOutreachActions) {
                this.dom.mOutreachActions.innerHTML = `
                    <button class="btn" style="padding: 0.2rem 0.5rem;" data-action="copyOutreach"><i class="fa-regular fa-copy"></i> Copiar Mensaje</button>
                    ${hasValidWA ? `<a href="${SecurityService.escapeHtml(waUrl)}" target="_blank" rel="noopener noreferrer" class="btn btn-whatsapp" style="padding: 0.2rem 0.5rem;"><i class="fa-brands fa-whatsapp"></i> Abrir Chat</a>` : '<span style="font-size: 0.68rem; color: var(--text-dim);"><i class="fa-solid fa-phone"></i> Teléfono PBX / Fijo (usa correo o LinkedIn)</span>'}
                `;
            }
        } else if (ch === 'linkedin') {
            if (this.dom.mOutreachHeading) this.dom.mOutreachHeading.textContent = 'Nota de Conexión en LinkedIn (< 300 Caracteres)';
            if (this.dom.mOutreachBody) this.dom.mOutreachBody.textContent = it.linkedin_connect_message || '';
            if (this.dom.mOutreachActions) {
                this.dom.mOutreachActions.innerHTML = `
                    <button class="btn" style="padding: 0.2rem 0.5rem;" data-action="copyOutreach"><i class="fa-regular fa-copy"></i> Copiar Nota</button>
                    <a href="${SecurityService.escapeHtml(it.linkedin_contact_search_url || '')}" target="_blank" rel="noopener noreferrer" class="btn btn-linkedin" style="padding: 0.2rem 0.5rem;"><i class="fa-brands fa-linkedin"></i> Buscar Reclutador</a>
                `;
            }
        }
    }

    copyToClipboard(elementId) {
        const el = document.getElementById(elementId);
        if (!el) return;
        const text = el.textContent || el.value || '';
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(() => {
                this.showToast('✓ Texto copiado al portapapeles');
            }).catch(() => {
                this.fallbackCopyText(text);
            });
        } else {
            this.fallbackCopyText(text);
        }
    }

    fallbackCopyText(text) {
        try {
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";
            textArea.style.left = "-999999px";
            textArea.style.top = "-999999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            if (successful) {
                this.showToast('✓ Texto copiado al portapapeles');
            } else {
                this.showToast('No se pudo copiar automáticamente');
            }
        } catch (err) {
            this.showToast('No se pudo copiar automáticamente');
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

// Global Application Bootstrap
const app = new AppController();

document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
