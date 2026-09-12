/**
 * SGVA SENA ADSO - Clean Architecture Application Controller
 * Patterns: MVVM / Store Pattern + Event Delegation + Responsive Adaptations
 * Security: OWASP Top 10 Compliant (Zero Inline JS, Strict Contextual Escaping)
 * Accessibility: WCAG 2.1 AA / ISO 9241-210 Compliant
 */

'use strict';

// =========================================================================
// 1. SECURITY & UTILITY SERVICE (OWASP Compliant)
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

    /**
     * Constructs a direct web compose URL for Gmail with prefilled recipient, subject and body.
     */
    static getGmailUrl(to, subject, body) {
        if (!to) return '#';
        const params = new URLSearchParams();
        params.set('view', 'cm');
        params.set('fs', '1');
        params.set('to', to);
        if (subject) params.set('su', subject);
        if (body) params.set('body', body);
        return `https://mail.google.com/mail/?${params.toString()}`;
    }

    /**
     * Reliable cross-platform detection for mobile devices, touch devices and mobile viewports (<= 768px).
     * @returns {boolean}
     */
    static isMobile() {
        if (typeof window === 'undefined') return false;
        const ua = (navigator.userAgent || navigator.vendor || window.opera || '').toLowerCase();
        const isMobileUA = /android|iphone|ipad|ipod|blackberry|iemobile|opera mini|mobile/i.test(ua);
        const isMobileViewport = window.innerWidth <= 768;
        const hasTouch = (typeof navigator.maxTouchPoints === 'number' && navigator.maxTouchPoints > 0) || ('ontouchstart' in window);
        return isMobileUA || isMobileViewport || (hasTouch && window.innerWidth <= 1024);
    }

    /**
     * Constructs an RFC 6068 compliant mailto URL with prefilled recipient, subject, and body.
     * Line breaks are converted to CRLF (%0D%0A) to ensure native mobile clients (Gmail, Apple Mail, Outlook)
     * preserve paragraph and newline formatting properly without opening a web browser.
     * @param {string} to
     * @param {string} subject
     * @param {string} body
     * @returns {string}
     */
    static getMailtoUrl(to, subject, body) {
        if (!to) return '#';
        const params = [];
        if (subject) {
            params.push(`subject=${encodeURIComponent(subject)}`);
        }
        if (body) {
            const normalizedBody = String(body).replace(/\r\n/g, '\n').replace(/\n/g, '\r\n');
            params.push(`body=${encodeURIComponent(normalizedBody)}`);
        }
        const qs = params.length > 0 ? `?${params.join('&')}` : '';
        return `mailto:${encodeURIComponent(to.trim())}${qs}`;
    }
}

// =========================================================================
// =========================================================================
// 2. CONFIGURATION & DOMAIN CONSTANTS
// =========================================================================
// 3. PERFIL DEL APRENDIZ (intercambiable, guardado en el navegador)
// =========================================================================
/**
 * Las cartas del dataset se redactaron con los datos de una persona concreta.
 * Este servicio guarda el perfil de quien usa la pagina y reescribe esos datos
 * al vuelo, de modo que cualquier aprendiz ADSO envie desde su propio nombre
 * sin tocar el dataset ni necesitar servidor.
 */
class ProfileService {
    static STORAGE_KEY = 'cap_perfil';

    /** Datos tal y como aparecen incrustados en el dataset original. */
    static SOURCE = Object.freeze({
        nombre: 'Juan Manuel Lagos Monroy',
        email: 'jmlagos2003@gmail.com',
        telefono: '(+57) 300 727 9875',
        cv: 'https://drive.google.com/file/d/1r89tS4JI4OKwSuzyyfPhGn4ylZTRlrln/view?usp=sharing',
        certificados: 'https://drive.google.com/drive/folders/1BZ-qBNdPeYsxW84zIq_ls97UkPlQcHyN?usp=sharing',
        github: 'https://github.com/lakerstrake',
        linkedin: 'https://linkedin.com/in/juan-manuel-lagos-monroy',
        formacion: '7 semestres de Ingeniería Mecatrónica y titulación como Técnico en Sistemas',
        profesion: '',
        experiencia: ''
    });

    static CAMPOS = ['nombre', 'profesion', 'experiencia', 'email', 'telefono',
                     'cv', 'certificados', 'github', 'linkedin', 'formacion'];

    static get() {
        try {
            const raw = localStorage.getItem(ProfileService.STORAGE_KEY);
            if (!raw) return { ...ProfileService.SOURCE, esPropio: false };
            const guardado = JSON.parse(raw);
            // Un campo que el aprendiz deja vacio queda vacio: heredar el del
            // ejemplo le atribuiria un GitHub o unos estudios que no son suyos.
            const perfil = { esPropio: true };
            ProfileService.CAMPOS.forEach(k => { perfil[k] = guardado[k] || ''; });
            return perfil;
        } catch (e) {
            return { ...ProfileService.SOURCE, esPropio: false };
        }
    }

    static save(datos) {
        const limpio = {};
        ProfileService.CAMPOS.forEach(k => {
            const v = String(datos[k] || '').trim();
            if (v) limpio[k] = v;
        });
        localStorage.setItem(ProfileService.STORAGE_KEY, JSON.stringify(limpio));
        return ProfileService.get();
    }

    static reset() {
        localStorage.removeItem(ProfileService.STORAGE_KEY);
        return ProfileService.get();
    }

    /** Solo se aceptan enlaces http(s): evita javascript: y data: en el correo. */
    static urlValida(u) {
        try {
            return ['http:', 'https:'].includes(new URL(u).protocol);
        } catch (e) {
            return false;
        }
    }

    /** Reescribe un texto del dataset con los datos del perfil activo. */
    static personalizar(texto) {
        if (!texto) return '';
        const p = ProfileService.get();
        if (!p.esPropio) return texto;

        const S = ProfileService.SOURCE;
        const nombres = S.nombre.split(' ');
        const soloNombre = p.nombre.split(' ').slice(0, 2).join(' ') || p.nombre;
        let out = String(texto);

        // El nombre aparece completo, en dos palabras y a secas: de mas largo a
        // mas corto, para que la forma corta no parta la larga.
        out = out.split(S.nombre).join(p.nombre);
        out = out.split(`${nombres[0]} ${nombres[1]} ${nombres[2]}`).join(p.nombre);
        out = out.split(`${nombres[0]} ${nombres[1]}`).join(soloNombre);
        out = out.split(`${nombres[0]}`).join(soloNombre.split(' ')[0]);

        out = out.split(S.email).join(p.email);
        out = out.split(S.telefono).join(p.telefono);
        out = out.split('300 727 9875').join(p.telefono.replace(/^\(\+57\)\s*/, ''));
        out = out.split(S.cv).join(p.cv);
        out = out.split(S.certificados).join(p.certificados);
        out = out.split(S.github).join(p.github);
        out = out.split(S.github.replace('https://', '')).join(p.github.replace(/^https?:\/\//, ''));
        out = out.split(S.linkedin).join(p.linkedin);
        out = out.split(S.linkedin.replace('https://', '')).join(p.linkedin.replace(/^https?:\/\//, ''));

        // Formacion previa: el dataset la menciona con tres redacciones. Si el
        // perfil no declara ninguna, la frase se retira en vez de atribuir
        // estudios ajenos a quien envia la carta.
        const F = p.formacion.trim();
        const fragmentos = [
            [', con una sólida base académica previa de 7 semestres de Ingeniería Mecatrónica y titulación como Técnico en Sistemas',
             F ? `, con formación previa en ${F}` : ''],
            [', 7 semestres de Ingeniería Mecatrónica y disponibilidad inmediata',
             F ? `, formación previa en ${F} y disponibilidad inmediata` : ', disponibilidad inmediata'],
            [' (background Mecatrónica)', F ? ` (${F})` : ''],
            ['7 semestres de Ingeniería Mecatrónica y titulación como Técnico en Sistemas',
             F || 'formación técnica complementaria'],
        ];
        fragmentos.forEach(([viejo, nuevo]) => { out = out.split(viejo).join(nuevo); });

        // Enlaces que el perfil deja en blanco: se retira su linea completa.
        [['github', '💻'], ['linkedin', '🔗'], ['certificados', '🎓']].forEach(([campo, icono]) => {
            if (!p[campo]) {
                out = out.replace(new RegExp('^' + icono + '.*\\n?', 'gm'), '');
            }
        });

        return out;
    }
}


// =========================================================================
// 4. MODOS DE BUSQUEDA (Software ADSO / Ingenieria Industrial)
// =========================================================================
/**
 * El mismo directorio de empresas sirve a dos perfiles distintos. En vez de
 * duplicar la aplicacion, cada modo decide como se agrupa, se ordena y se
 * redacta la postulacion sobre el mismo conjunto de empresas reales.
 *
 * El modo industrial se apoya en la actividad economica que cada empresa
 * declara en el registro mercantil (codigo CIIU), no en la etiqueta de
 * software con la que se enriquecio el dataset originalmente.
 */
class ModeService {
    static STORAGE_KEY = 'cap_modo';

    static MODOS = Object.freeze({
        software: {
            id: 'software',
            etiqueta: 'Software · ADSO',
            icono: 'fa-solid fa-code',
            titulo: 'Contratos de Aprendizaje ADSO',
            descripcion: 'Vacantes de aprendizaje SENA en análisis y desarrollo de software.',
            columnaGrupo: 'Categoría',
            columnaDetalle: 'Stack tecnológico',
            columnaScore: 'Afinidad IA',
            profesion: 'Aprendiz ADSO SENA',
            disponibilidad: 'Disponible Etapa Productiva',
            unidadPlural: 'vacantes',
            marca: 'SENA · ADSO',
            marcaSub: 'Directorio Estratégico'
        },
        industrial: {
            id: 'industrial',
            etiqueta: 'Ingeniería Industrial',
            icono: 'fa-solid fa-industry',
            titulo: 'Directorio Empresarial · Ingeniería Industrial',
            descripcion: 'Empresas colombianas verificadas en el registro mercantil, ordenadas por afinidad con procesos, producción y logística.',
            columnaGrupo: 'Sector económico',
            columnaDetalle: 'Actividad verificada (CIIU)',
            columnaScore: 'Relevancia',
            profesion: 'Ingeniero Industrial',
            disponibilidad: 'Disponible para vincularse',
            unidadPlural: 'empresas',
            marca: 'Directorio Industrial',
            marcaSub: 'Ingeniería Industrial · Colombia'
        }
    });

    /** Sectores ordenados por afinidad con el perfil de ingenieria industrial. */
    static SECTORES = Object.freeze([
        'Manufactura', 'Transporte y Logística', 'Minería y Petróleo', 'Energía',
        'Construcción', 'Agroindustria', 'Comercio y Distribución',
        'Consultoría e Ingeniería', 'Servicios a Empresas', 'Salud', 'Tecnología'
    ]);

    static get() {
        const guardado = localStorage.getItem(ModeService.STORAGE_KEY);
        return ModeService.MODOS[guardado] ? guardado : 'software';
    }

    static set(modo) {
        if (!ModeService.MODOS[modo]) return ModeService.get();
        localStorage.setItem(ModeService.STORAGE_KEY, modo);
        return modo;
    }

    static config() {
        return ModeService.MODOS[ModeService.get()];
    }

    static esIndustrial() {
        return ModeService.get() === 'industrial';
    }

    /**
     * Redacta la postulacion de ingenieria industrial con datos reales de la
     * empresa y del perfil activo. Se compone en el navegador en lugar de
     * viajar en el dataset: asi siempre refleja a quien esta usando la pagina
     * y no añade 200 KB de texto repetido a la descarga.
     */
    static cartaIndustrial(it, canal) {
        const p = ProfileService.get();
        const nombre = p.nombre || '[Tu nombre]';
        const profesion = p.profesion || 'Ingeniero(a) Industrial';
        // El registro trae nombres en mayusculas sostenidas: encabezar una carta
        // con "Estimado(a) MANUELA" se lee como correo masivo.
        const propio = (t) => String(t || '').toLowerCase()
            .replace(/(^|[\s'-])([a-záéíóúñ])/g, (m, sep, c) => sep + c.toUpperCase());
        const contacto = (it.contacto || '').trim();
        const saludo = contacto.length > 2
            ? 'Estimado(a) ' + propio(contacto.split(' ')[0])
            : 'Estimado equipo de Gestión Humana';
        const empresa = it.empresa || 'su compañía';
        const actividad = (it.ind_actividad || 'su sector').toLowerCase();
        const enfoque = it.ind_enfoque || 'la mejora de procesos y la productividad';
        const herramientas = it.ind_herramientas || 'gestión por procesos, análisis de datos e indicadores';
        const ciudad = it.ciudad ? ' en ' + it.ciudad : '';
        const experiencia = p.experiencia
            ? 'Cuento con ' + p.experiencia + '.'
            : 'Me encuentro en búsqueda activa de una oportunidad donde aportar desde el primer día.';

        if (canal === 'wa') {
            const wa = [
                saludo + ', un cordial saludo.',
                '',
                'Mi nombre es ' + nombre + ', ' + profesion + '. Me dirijo a ustedes con interés en vincularme a *' + empresa + '*.',
                '',
                'Conozco que su actividad se centra en ' + actividad + ', y mi perfil aporta en ' + enfoque + '.'
            ];
            if (p.cv) wa.push('', 'Hoja de vida: ' + p.cv);
            wa.push('', '¿Sería posible hacerles llegar mi perfil para sus procesos de selección? Quedo atento(a). Gracias por su tiempo.');
            return wa.join('\n');
        }

        if (canal === 'linkedin') {
            const corto = saludo + ', soy ' + nombre + ', ' + profesion +
                '. Me interesa aportar en ' + enfoque.split(',')[0] + ' en ' + empresa +
                '. Me encantaría conectar y compartirle mi perfil.';
            return corto.length > 290 ? corto.substring(0, 287) + '...' : corto;
        }

        const l = [
            saludo + ',',
            '',
            'Me dirijo a ustedes con el fin de postular mi perfil profesional a los procesos de selección de ' + empresa + ciudad + '.',
            '',
            'Soy ' + profesion + (p.formacion ? ', con formación complementaria en ' + p.formacion : '') + '. ' +
            experiencia + ' Mi perfil se orienta a ' + enfoque + ', apoyándome en ' + herramientas + '.',
            '',
            'Identifico que ' + empresa + ' desarrolla su actividad en ' + actividad +
            ', un entorno donde la ingeniería industrial aporta de forma directa en la estandarización de procesos, ' +
            'el control de indicadores y la reducción de costos operativos. Me interesa contribuir a esos frentes con ' +
            'rigor técnico y orientación a resultados medibles.',
            '',
            'Comparto mis datos para su consulta:'
        ];
        if (p.cv) l.push('Hoja de Vida: ' + p.cv);
        if (p.certificados) l.push('Certificados: ' + p.certificados);
        if (p.linkedin) l.push('LinkedIn: ' + p.linkedin);
        if (p.telefono) l.push('Teléfono: ' + p.telefono);
        if (p.email) l.push('Correo: ' + p.email);
        l.push(
            '',
            'Agradezco la atención prestada y quedo atento(a) a la posibilidad de una entrevista.',
            '',
            'Cordialmente,',
            nombre,
            profesion
        );
        return l.join('\n');
    }

    static asuntoIndustrial(it) {
        const p = ProfileService.get();
        return 'Postulación ' + (p.profesion || 'Ingeniería Industrial') +
               ' - ' + (p.nombre || '[Tu nombre]') + ' | ' + (it.empresa || '');
    }

    /** Texto de postulacion del modo activo, para cualquiera de los 3 canales. */
    static carta(it, canal) {
        if (ModeService.esIndustrial()) return ModeService.cartaIndustrial(it, canal);
        if (canal === 'wa') return ProfileService.personalizar(it.whatsapp_message);
        if (canal === 'linkedin') return ProfileService.personalizar(it.linkedin_connect_message);
        return ProfileService.personalizar(it.correo_formal_completo);
    }

    static asunto(it) {
        if (ModeService.esIndustrial()) return ModeService.asuntoIndustrial(it);
        return 'Postulación Contrato ADSO - ' + ProfileService.get().nombre;
    }
}

// =========================================================================
const CONFIG = Object.freeze({
    CANDIDATE: {
        name: "Juan Manuel Lagos Monroy",
        phone: "(+57) 300 727 9875",
        email: "jmlagos2003@gmail.com",
        github: "https://github.com/lakerstrake",
        linkedin: "https://linkedin.com/in/juan-manuel-lagos-monroy",
        cvDrive: "https://drive.google.com/file/d/1r89tS4JI4OKwSuzyyfPhGn4ylZTRlrln/view?usp=sharing",
        certsDrive: "https://drive.google.com/drive/folders/1BZ-qBNdPeYsxW84zIq_ls97UkPlQcHyN?usp=sharing",
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
        this._lastIsMobile = typeof window !== 'undefined' ? SecurityService.isMobile() : false;
        
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

    cacheDomElements() {
        this.dom = {
            html: document.documentElement,
            themeIcon: document.getElementById('themeIcon'),
            themeBtn: document.getElementById('themeBtn'),
            
            // Auth & Security Elements
            authModal: document.getElementById('authModal'),
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
            mTabPanorama: document.getElementById('mTabPanorama'),
            mTabOutreach: document.getElementById('mTabOutreach'),
            mTabInterview: document.getElementById('mTabInterview'),
            mTabDetails: document.getElementById('mTabDetails'),
            mSecPanorama: document.getElementById('mSecPanorama'),
            mSecOutreach: document.getElementById('mSecOutreach'),
            mSecInterview: document.getElementById('mSecInterview'),
            mSecDetails: document.getElementById('mSecDetails'),
            mTierText: document.getElementById('mTierText'),
            mVacantesText: document.getElementById('mVacantesText'),
            mModalidadText: document.getElementById('mModalidadText'),
            
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
            
            // Toast & CV Telemetry
            toastMsg: document.getElementById('toastMsg'),

            // SGVA Live Sync & Diagnostics Elements
            btnQuickSyncSgva: document.getElementById('btnQuickSyncSgva'),
            iconQuickSync: document.getElementById('iconQuickSync'),
            btnToolbarSyncSgva: document.getElementById('btnToolbarSyncSgva'),
            iconToolbarSync: document.getElementById('iconToolbarSync'),
            btnSgvaStatusBadge: document.getElementById('btnSgvaStatusBadge'),
            iconSyncStatusDot: document.getElementById('iconSyncStatusDot'),
            lblSgvaBadgeText: document.getElementById('lblSgvaBadgeText'),
            iconSyncModalHeader: document.getElementById('iconSyncModalHeader'),
            btnModalTriggerSync: document.getElementById('btnModalTriggerSync'),
            iconModalSync: document.getElementById('iconModalSync'),
            pipelineStepper: document.getElementById('pipelineStepper'),
            pipelineStatusBadge: document.getElementById('pipelineStatusBadge'),
            sgvaDate: document.getElementById('sgvaDate'),
            sgvaMsg: document.getElementById('sgvaMsg')
        };
    }

    init() {
        this.cacheDomElements();
        this.initTheme();
        this.populateFilterDropdowns();
        this.bindEvents();
        this.updateFavCounter();
        this.updateCompareDock();
        this.renderModeUI();

        // Mobile-first responsive optimization
        if (window.innerWidth < 768) {
            this.store.viewMode = 'cards';
        }

        this.setLayout(this.store.viewMode);
        this.initRepoStatus();
        this.renderCandidateBanner();
        this.applyFilters();
    }

    /**
     * El directorio es publico y la cabecera ya muestra nombre, correo, CV,
     * GitHub y LinkedIn del titular, asi que el modo invitado solo servia para
     * enmascarar esos mismos datos dentro de las cartas: obligaba a iniciar
     * sesion antes de poder escribir a una sola empresa. Se elimino.
     */
    renderCandidateBanner() {
        const banner = document.getElementById('candidateBanner');
        const dir = document.getElementById('sectionDirectory');
        if (dir) dir.style.display = 'flex';
        if (!banner) return;

        const p = ProfileService.get();
        const cfg = ModeService.config();
        const e = SecurityService.escapeHtml;
        const enlace = (url, clase, icono, texto, sufijo) => url
            ? `<a href="${e(url)}" target="_blank" rel="noopener noreferrer" class="${clase}"><i class="${icono}" aria-hidden="true"></i> <span>${texto}</span>${sufijo || ''}</a>`
            : '';

        const aviso = p.esPropio ? '' : `
            <span class="perfil-aviso">
                <i class="fa-solid fa-circle-info" aria-hidden="true"></i>
                Perfil de ejemplo. <button type="button" class="link-btn" data-action="openProfileModal">Pon tus datos</button> para que las cartas salgan a tu nombre.
            </span>`;

        banner.style.display = 'flex';
        banner.innerHTML = `
            <div class="candidate-banner-main">
                <div class="candidate-badge-photo" aria-hidden="true"><i class="fa-solid fa-user-gear"></i></div>
                <div class="candidate-meta">
                    <div class="candidate-name-row">
                        <h2>${e(p.nombre)}</h2>
                        <span class="status-pill status-ready"><i class="fa-solid fa-bolt" aria-hidden="true"></i> ${e(cfg.disponibilidad)}</span>
                    </div>
                    <p class="candidate-pitch">
                        ${e(p.profesion || cfg.profesion)}${p.experiencia ? ` · ${e(p.experiencia)}` : ''}${p.formacion ? ` · ${e(p.formacion)}` : ''}.
                        <span id="lblBannerTotal">${this.store.rawData.length}</span> ${e(cfg.unidadPlural)} en el directorio.
                        ${aviso}
                    </p>
                </div>
            </div>
            <div class="candidate-banner-actions">
                <button class="btn btn-primary" data-action="openProfileModal">
                    <i class="fa-solid fa-id-card" aria-hidden="true"></i> Mi perfil
                </button>
                ${enlace(p.cv, 'btn-cv-drive', 'fa-solid fa-file-pdf', 'Hoja de Vida', '<span class="cv-mini-badge">PDF</span>')}
                ${enlace(p.github, 'btn-github-link', 'fa-brands fa-github', 'GitHub')}
                ${enlace(p.linkedin, 'btn-linkedin', 'fa-brands fa-linkedin', 'LinkedIn')}
                ${enlace(p.certificados, 'btn-certs-link', 'fa-solid fa-graduation-cap', 'Certificados', '<span class="cv-mini-badge">Drive</span>')}
                <button class="btn-dismiss-banner" data-action="dismissNotice" title="Ocultar banner" aria-label="Ocultar banner">
                    <i class="fa-solid fa-xmark" aria-hidden="true"></i>
                </button>
            </div>
        `;
    }

    openProfileModal() {
        const modal = document.getElementById('profileModal');
        if (!modal) return;
        const p = ProfileService.get();
        ProfileService.CAMPOS.forEach(k => {
            const input = document.getElementById(`perfil_${k}`);
            if (input) input.value = p.esPropio ? (p[k] || '') : '';
        });
        const aviso = document.getElementById('perfilError');
        if (aviso) aviso.hidden = true;
        modal.style.display = 'flex';
        document.body.classList.add('modal-open');
        this.openModalFocus(modal);
    }

    closeProfileModal() {
        const modal = document.getElementById('profileModal');
        if (!modal) return;
        modal.style.display = 'none';
        document.body.classList.remove('modal-open');
        this.releaseModalFocus(modal);
    }

    saveProfile() {
        const datos = {};
        ProfileService.CAMPOS.forEach(k => {
            const input = document.getElementById(`perfil_${k}`);
            datos[k] = input ? input.value : '';
        });

        const aviso = document.getElementById('perfilError');
        const fallo = (msg) => {
            if (aviso) { aviso.textContent = msg; aviso.hidden = false; }
            return false;
        };

        if (!datos.nombre.trim()) return fallo('Escribe tu nombre completo: es lo que firma cada carta.');
        if (!datos.email.includes('@')) return fallo('El correo no parece válido.');
        for (const campo of ['cv', 'certificados', 'github', 'linkedin']) {
            if (datos[campo].trim() && !ProfileService.urlValida(datos[campo].trim())) {
                return fallo(`El enlace de ${campo} debe empezar por http:// o https://`);
            }
        }

        ProfileService.save(datos);
        this.closeProfileModal();
        this.renderCandidateBanner();
        this.applyFilters();
        this.showToast(`Perfil guardado · las cartas ahora salen a nombre de ${datos.nombre.trim()}`);
        return true;
    }

    resetProfile() {
        ProfileService.reset();
        this.closeProfileModal();
        this.renderCandidateBanner();
        this.applyFilters();
        this.showToast('Perfil borrado de este navegador');
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
                // Todos los dialogos deben ceder a Escape, incluido el de acceso:
                // dejar uno fuera atrapa al usuario de teclado.
                this.closeDetailModal();
                this.closeCompareModal();
                this.closeProfileModal();
            }
            if (e.key === 'Tab') this.trapFocus(e);
        });

        // Global Fail-Safe Interceptor for Mobile Email Actions:
        // Guarantees that on mobile devices / viewports, any email click opens the native email app via mailto:
        // and NEVER opens a new browser tab / window.
        document.addEventListener('click', (e) => {
            const emailTarget = e.target.closest('[data-email-action="true"], .mini-mail-app, .btn-mail-app, .mini-gmail, .btn-gmail, a[href^="mailto:"], a[href*="mail.google.com"]');
            if (!emailTarget) return;

            if (SecurityService.isMobile()) {
                const rawHref = emailTarget.getAttribute('href') || '';
                
                // If it points to Gmail web compose, block browser navigation and redirect to mailto:
                if (rawHref.includes('mail.google.com')) {
                    e.preventDefault();
                    e.stopPropagation();
                    try {
                        const parsed = new URL(rawHref, window.location.origin);
                        const to = parsed.searchParams.get('to') || emailTarget.getAttribute('data-email') || '';
                        const su = parsed.searchParams.get('su') || '';
                        const body = parsed.searchParams.get('body') || '';
                        const mailtoUri = SecurityService.getMailtoUrl(to, su, body);
                        window.location.href = mailtoUri;
                    } catch (err) {
                        const fallbackEmail = emailTarget.getAttribute('data-email') || '';
                        if (fallbackEmail) window.location.href = `mailto:${encodeURIComponent(fallbackEmail)}`;
                    }
                    return;
                }

                // If it's mailto:, ensure no target="_blank" so mobile browser doesn't open an empty tab
                if (rawHref.startsWith('mailto:')) {
                    if (emailTarget.getAttribute('target')) {
                        emailTarget.removeAttribute('target');
                    }
                    if (emailTarget.getAttribute('rel')) {
                        emailTarget.removeAttribute('rel');
                    }
                }
            }
        }, { capture: true });

        // Responsive Viewport Resize Listener: Update layout and buttons dynamically when crossing mobile breakpoint
        let resizeTimer = null;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                const isMobileNow = SecurityService.isMobile();
                if (this.store && this.store._lastIsMobile !== isMobileNow) {
                    this.store._lastIsMobile = isMobileNow;
                    if (this.store.viewMode === 'cards') {
                        this.renderCards();
                    } else {
                        this.renderTable();
                    }
                    if (this.store.activeDetailItem && this.store.modalTab === 'outreach') {
                        this.renderOutreachChannel(this.store.modalChannel || 'email');
                    }
                }
            }, 200);
        });
    }

    handleAction(action, el, event) {
        switch (action) {
            case 'switchNavTab':
                this.switchNavTab(el.getAttribute('data-tab'));
                break;
            case 'toggleTheme':
                this.toggleTheme();
                break;
            case 'exportData':
                this.exportData(el.getAttribute('data-format'));
                break;
            case 'openProfileModal':
                this.openProfileModal();
                break;
            case 'closeProfileModal':
            case 'backdropCloseProfile':
                if (action === 'backdropCloseProfile' && event.target.id !== 'profileModal') return;
                this.closeProfileModal();
                break;
            case 'saveProfile':
                this.saveProfile();
                break;
            case 'resetProfile':
                this.resetProfile();
                break;
            case 'setMode':
                this.setMode(el.getAttribute('data-mode'));
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

    /**
     * Gestion de foco de dialogos (WAI-ARIA APG): al abrir, el foco entra en el
     * panel; al cerrar, vuelve al control que lo invoco.
     */
    static FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

    focusablesIn(panel) {
        return [...panel.querySelectorAll(AppController.FOCUSABLE)]
            .filter(el => el.offsetParent !== null || el === document.activeElement);
    }

    openModalFocus(modal) {
        if (!modal) return;
        this._lastFocused = document.activeElement;
        this._openModal = modal;
        const panel = modal.querySelector('.modal-panel, .modal-content') || modal;
        const first = this.focusablesIn(panel)[0];
        if (first) setTimeout(() => first.focus(), 30);
    }

    releaseModalFocus(modal) {
        if (this._openModal !== modal) return;
        this._openModal = null;
        if (this._lastFocused && document.contains(this._lastFocused)) {
            this._lastFocused.focus();
        }
        this._lastFocused = null;
    }

    trapFocus(e) {
        const modal = this._openModal;
        if (!modal || modal.style.display === 'none') return;
        const panel = modal.querySelector('.modal-panel, .modal-content') || modal;
        const items = this.focusablesIn(panel);
        if (items.length === 0) return;
        const first = items[0];
        const last = items[items.length - 1];
        if (e.shiftKey && document.activeElement === first) {
            e.preventDefault();
            last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
            e.preventDefault();
            first.focus();
        }
    }

    /**
     * El dataset trae un hex por tier pensado solo para el tema oscuro.
     * Se traduce a una clase para que el color lo resuelvan los tokens.
     */
    /** Color del indicador de relevancia industrial por tramos. */
    static indScoreClass(score) {
        const n = Number(score) || 0;
        if (n >= 90) return 'is-tier-s';
        if (n >= 75) return 'is-tier-a';
        if (n >= 60) return 'is-tier-b';
        return 'is-tier-d';
    }

    setMode(modo) {
        if (modo === ModeService.get()) return;
        ModeService.set(modo);
        // Los grupos de un modo no existen en el otro: se limpia la seleccion.
        this.store.activeTier = '';
        this.store.activeStack = '';
        this.store.currentPage = 1;
        if (this.dom.mainSearch) this.dom.mainSearch.value = '';
        this.renderModeUI();
        this.renderCandidateBanner();
        this.applyFilters();
        this.showToast(`Modo ${ModeService.config().etiqueta} activo`);
    }

    /** Ajusta cabeceras, grupos y textos al modo activo. */
    renderModeUI() {
        const cfg = ModeService.config();
        const industrial = ModeService.esIndustrial();
        document.body.classList.toggle('modo-industrial', industrial);

        document.querySelectorAll('[data-action="setMode"]').forEach(b => {
            const activo = b.getAttribute('data-mode') === cfg.id;
            b.classList.toggle('active', activo);
            b.setAttribute('aria-pressed', String(activo));
        });

        const th = document.querySelectorAll('.data-table thead th');
        if (th.length >= 7) {
            th[4].textContent = cfg.columnaGrupo;
            th[5].textContent = cfg.columnaDetalle;
            th[6].textContent = cfg.columnaScore;
        }

        const stackRow = document.querySelector('.stack-row');
        if (stackRow) stackRow.hidden = industrial;

        if (this.dom.mainSearch) {
            this.dom.mainSearch.placeholder = industrial
                ? 'Buscar por empresa, NIT, ciudad, sector o actividad (CIIU)...'
                : 'Buscar por empresa, NIT, ciudad, stack (React, Node, SQL)...';
        }

        const brandIcon = document.querySelector('.brand-badge i');
        if (brandIcon) brandIcon.className = cfg.icono;

        const marca = document.querySelector('.brand-title h1');
        const marcaSub = document.querySelector('.brand-title span');
        if (marca) marca.textContent = cfg.marca;
        if (marcaSub) marcaSub.textContent = cfg.marcaSub;

        // Nota de procedencia: en modo industrial el usuario debe saber que el
        // contacto es real pero la vacante publicada es de contrato de
        // aprendizaje, no una oferta de ingenieria.
        const nota = document.getElementById('notaModo');
        if (nota) {
            nota.hidden = !industrial;
            if (industrial) {
                nota.innerHTML = '<i class="fa-solid fa-circle-info" aria-hidden="true"></i> ' +
                    '<span><strong>Cómo usar este directorio:</strong> los correos y teléfonos son los que ' +
                    'cada empresa publicó en el portal del SENA para recibir postulaciones, y su actividad ' +
                    'económica está verificada contra el registro mercantil. Las vacantes listadas son ' +
                    'contratos de aprendizaje, así que el uso aquí es enviar tu hoja de vida de forma ' +
                    'espontánea al área de Gestión Humana, no responder a esa vacante.</span>';
            }
        }

        document.querySelectorAll('[data-unidad]').forEach(el => {
            el.textContent = cfg.unidadPlural;
        });

        this.renderGrupos();
    }

    /** Botones de grupo: tiers en software, sectores reales en industrial. */
    renderGrupos() {
        const cont = document.querySelector('.tier-segments');
        if (!cont) return;
        const industrial = ModeService.esIndustrial();
        const campo = industrial ? 'ind_sector' : 'cat_id';

        const conteo = this.store.rawData.reduce((acc, d) => {
            const k = d[campo];
            if (k) acc[k] = (acc[k] || 0) + 1;
            return acc;
        }, {});

        let grupos;
        if (industrial) {
            grupos = ModeService.SECTORES
                .filter(sec => conteo[sec])
                .map(sec => ({ valor: sec, texto: sec, clase: '' }));
        } else {
            grupos = [
                { valor: 'TIER_1', texto: 'Tier 1 · Élite Tech', clase: 'seg-1' },
                { valor: 'TIER_2', texto: 'Tier 2 · Sistemas', clase: 'seg-2' },
                { valor: 'TIER_3', texto: 'Tier 3 · Soporte TI', clase: 'seg-3' },
                { valor: 'TIER_5', texto: 'Tier 5 · No TI', clase: '' }
            ].filter(g => conteo[g.valor]);
        }

        const total = this.store.rawData.length;
        const activo = this.store.activeTier;
        let html = `<button class="tier-seg-btn${activo ? '' : ' active'}" data-action="filterTier" data-tier="">` +
                   `Todos <span class="seg-pill">${total}</span></button>`;
        grupos.forEach(g => {
            html += `<button class="tier-seg-btn ${g.clase}${activo === g.valor ? ' active' : ''}" ` +
                    `data-action="filterTier" data-tier="${SecurityService.escapeHtml(g.valor)}">` +
                    `${SecurityService.escapeHtml(g.texto)} <span class="seg-pill">${conteo[g.valor]}</span></button>`;
        });
        cont.innerHTML = html;
    }

    static aiTierClass(tier) {
        const map = { S: 'is-tier-s', A: 'is-tier-a', B: 'is-tier-b', C: 'is-tier-b', D: 'is-tier-d' };
        return map[String(tier || '').toUpperCase()] || 'is-tier-a';
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
            const campoGrupo = ModeService.esIndustrial() ? 'ind_sector' : 'cat_id';
            if (this.store.activeTier && it[campoGrupo] !== this.store.activeTier) return false;
            if (this.store.activeStack && (!it.stack_tags || !it.stack_tags.includes(this.store.activeStack))) return false;
            if (ch === 'WHATSAPP' && !it.is_whatsapp) return false;
            if (ch === 'EMAIL' && (!it.email || !it.email.includes('@'))) return false;
            if (comp && it.facilidad_code !== comp) return false;

            if (query) {
                const combined = `${it.empresa} ${it.nit} ${it.ciudad} ${it.departamento} ${it.funciones} ${it.perfil_requerido} ${it.contacto} ${it.email} ${it.telefono} ${it.ind_sector || ''} ${it.ind_actividad || ''}`.toLowerCase();
                if (!combined.includes(query)) return false;
            }

            if (dpto && it.departamento !== dpto) return false;
            if (city && (it.ciudad || '').trim() !== city) return false;

            return true;
        });

        // Sorting
        // En modo industrial el orden por defecto es la afinidad del sector con
        // procesos, produccion y logistica, no el ranking pensado para software.
        const industrial = ModeService.esIndustrial();
        this.store.filteredData.sort((a, b) => {
            if (industrial && sort === 'ranking_asc') return (b.ind_score || 0) - (a.ind_score || 0);
            if (sort === 'score_desc' && industrial) return (b.ind_score || 0) - (a.ind_score || 0);
            if (sort === 'ranking_asc') return (a.ranking_posicion || 0) - (b.ranking_posicion || 0);
            if (sort === 'score_desc') return (b.puntaje_exito || 0) - (a.puntaje_exito || 0);
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
                            <i class="fa-solid fa-magnifying-glass" style="font-size: 1.9rem; color: var(--text-dim);" aria-hidden="true"></i>
                            <strong style="color: var(--text-main); font-size: 0.96rem;">No se encontraron vacantes con los criterios seleccionados</strong>
                            <p style="font-size: 0.82rem; max-width: 380px;">Prueba ajustando los términos de búsqueda o restableciendo los filtros para ver las ${this.store.rawData.length} oportunidades.</p>
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
            const waUrl = hasValidWA ? SecurityService.getWhatsAppUrl(it.telefono, ModeService.carta(it, 'wa')) : '';

            const posFormatted = (it.ranking_posicion || 1) < 10 ? '0' + it.ranking_posicion : it.ranking_posicion;

            const mailBody = ModeService.carta(it, 'email');
            const mailSub = ModeService.asunto(it);

            const isMobile = SecurityService.isMobile();
            const emailHref = isMobile 
                ? SecurityService.getMailtoUrl(it.email, mailSub, mailBody)
                : SecurityService.getGmailUrl(it.email, mailSub, mailBody);
            const emailTarget = isMobile ? '' : 'target="_blank" rel="noopener noreferrer"';
            const emailClass = isMobile ? 'mini-btn mini-mail-app' : 'mini-btn mini-gmail';
            const emailIcon = isMobile ? '<i class="fa-solid fa-envelope"></i>' : '<i class="fa-brands fa-google"></i>';
            const emailTitle = isMobile ? `Abrir en App de Correo (${SecurityService.escapeHtml(it.email)})` : `Redactar en Gmail (${SecurityService.escapeHtml(it.email)})`;

            tr.innerHTML = `
                <td style="text-align: center;">
                    <input type="checkbox" ${isComp ? 'checked' : ''} data-action="toggleCompare" data-id="${SecurityService.escapeHtml(it.solicitud_id)}" aria-label="Comparar empresa">
                </td>
                <td style="text-align: center;">
                    <i class="${favIcon}" style="cursor: pointer; ${favColor}" data-action="toggleFavorite" data-id="${SecurityService.escapeHtml(it.solicitud_id)}" aria-label="Marcar como favorita"></i>
                </td>
                <td style="font-family: var(--font-mono); font-weight: 700; color: var(--text-dim); text-align: center;">#${posFormatted}</td>
                <td>
                    <div class="cell-main">
                        <span class="cell-title" title="${SecurityService.escapeHtml(it.empresa)}">${SecurityService.escapeHtml(it.empresa)}</span>
                        <span class="cell-sub">${SecurityService.escapeHtml(it.ciudad || '')}, ${SecurityService.escapeHtml(it.departamento || '')} • NIT: ${SecurityService.escapeHtml(it.nit || 'N/A')}</span>
                    </div>
                </td>
                <td>${ModeService.esIndustrial()
                    ? `<span class="pill-badge sector-badge" title="Sector según el registro mercantil">${SecurityService.escapeHtml(it.ind_sector || 'Sin verificar')}</span>`
                    : `<span class="pill-badge ${tierClass}">${SecurityService.escapeHtml(it.cat_badge || 'Tier')}</span>`}</td>
                <td>
                    <div style="display: flex; gap: 0.22rem; flex-wrap: wrap; align-items: center;">
                        ${ModeService.esIndustrial()
                            ? `<span class="ciiu-cell" title="Actividad declarada en el registro mercantil">
                                   <span class="ciiu-code">${SecurityService.escapeHtml(it.rues_ciiu || '----')}</span>
                                   <span class="ciiu-text">${SecurityService.escapeHtml(it.ind_actividad || 'Sin verificar')}</span>
                               </span>`
                            : (it.stack_tags && it.stack_tags.length > 0)
                                ? it.stack_tags.slice(0, 3).map(t => `<span class="stack-chip">${SecurityService.escapeHtml(t)}</span>`).join('')
                                : `<span style="color:var(--text-dim);font-size:0.76rem;">ADSO General</span>`
                        }
                    </div>
                </td>
                <td style="text-align: center;">
                    <div style="display: inline-flex; align-items: center; gap: 0.3rem;">
                        ${ModeService.esIndustrial()
                            ? `<strong class="ai-score ${AppController.indScoreClass(it.ind_score)}" style="font-family: var(--font-mono); font-size: 0.94rem;">${it.ind_score || 0}</strong>
                               ${it.rues_verificado ? '<span class="verif-chip" title="Verificada en el registro mercantil (RUES)"><i class="fa-solid fa-circle-check" aria-hidden="true"></i></span>' : ''}`
                            : `<strong class="ai-score ${AppController.aiTierClass(it.ai_tier)}" style="font-family: var(--font-mono); font-size: 0.94rem;">${it.puntaje_exito || 0}</strong>
                               <span class="ai-tier-chip ${AppController.aiTierClass(it.ai_tier)}">T${it.ai_tier || '?'}</span>`}
                    </div>
                </td>
                <td>
                    <span style="display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.79rem; white-space: nowrap;">
                        <span class="ratio-dot ${dotClass}"></span>
                        <span>${it.vacantes || 1} vac · ${it.postulados || 0} post</span>
                    </span>
                </td>
                <td style="text-align: right;">
                    <div class="row-actions">
                        ${hasEmail ? `<a href="${SecurityService.escapeHtml(emailHref)}" ${emailTarget} class="${emailClass}" title="${emailTitle}" data-email-action="true" data-email="${SecurityService.escapeHtml(it.email)}">${emailIcon}</a>` : ''}
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

        const page = this.store.currentPage;
        const prev = Math.max(1, page - 1);
        const next = Math.min(totalPages, page + 1);
        const atStart = page === 1;
        const atEnd = page === totalPages;

        // Un unico atributo style por boton: el disabled anterior emitia un
        // segundo style que el parser descartaba junto con el estado apagado.
        const arrow = (target, disabled, dir, label) =>
            `<button class="btn page-btn" data-action="goToPage" data-page="${target}"` +
            `${disabled ? ' disabled' : ''} aria-label="${label}">` +
            `<i class="fa-solid fa-chevron-${dir}" aria-hidden="true"></i></button>`;

        if (window.innerWidth < 640) {
            this.dom.paginationPages.innerHTML =
                arrow(prev, atStart, 'left', 'Página anterior') +
                `<span class="page-indicator">${page} / ${totalPages}</span>` +
                arrow(next, atEnd, 'right', 'Página siguiente');
            return;
        }

        let html = arrow(prev, atStart, 'left', 'Página anterior');
        for (let i = 1; i <= totalPages; i++) {
            if (totalPages > 6 && Math.abs(i - page) > 2 && i !== 1 && i !== totalPages) {
                if (i === 2 || i === totalPages - 1) html += `<span class="page-gap" aria-hidden="true">…</span>`;
                continue;
            }
            const current = i === page;
            html += `<button class="btn page-btn${current ? ' is-current' : ''}" data-action="goToPage" data-page="${i}"` +
                    `${current ? ' aria-current="page"' : ''} aria-label="Página ${i} de ${totalPages}">${i}</button>`;
        }
        html += arrow(next, atEnd, 'right', 'Página siguiente');

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
                        <i class="fa-solid fa-magnifying-glass" style="font-size: 1.9rem; color: var(--text-dim);" aria-hidden="true"></i>
                        <strong style="color: var(--text-main); font-size: 0.96rem;">No se encontraron vacantes con los filtros actuales</strong>
                        <p style="font-size: 0.82rem; max-width: 380px;">Prueba ajustando los términos de búsqueda o restableciendo los filtros para ver las ${this.store.rawData.length} oportunidades.</p>
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
            const waUrl = hasValidWA ? SecurityService.getWhatsAppUrl(it.telefono, ModeService.carta(it, 'wa')) : '';

            const posFormatted = (it.ranking_posicion || 1) < 10 ? '0' + it.ranking_posicion : it.ranking_posicion;

            const cardMailSub = ModeService.asunto(it);
            const cardMailBody = ModeService.carta(it, 'email');
            const isMobile = SecurityService.isMobile();
            const emailHref = isMobile 
                ? SecurityService.getMailtoUrl(it.email, cardMailSub, cardMailBody)
                : SecurityService.getGmailUrl(it.email, cardMailSub, cardMailBody);
            const emailTarget = isMobile ? '' : 'target="_blank" rel="noopener noreferrer"';
            const emailClass = isMobile ? 'mini-btn mini-mail-app' : 'mini-btn mini-gmail';
            const emailIcon = isMobile ? '<i class="fa-solid fa-envelope"></i>' : '<i class="fa-brands fa-google"></i>';
            const emailLabel = isMobile ? 'Correo (App)' : 'Gmail';
            const emailTitle = isMobile ? `Abrir en App de Correo (${SecurityService.escapeHtml(it.email)})` : `Redactar en Gmail (${SecurityService.escapeHtml(it.email)})`;

            card.innerHTML = `
                <div style="display: flex; flex-direction: column; gap: 0.45rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 0.35rem;">
                            <span style="font-family: var(--font-mono); font-weight: 700; color: var(--text-dim); font-size: 0.82rem;">#${posFormatted}</span>
                            <span class="pill-badge ${tierClass}">${SecurityService.escapeHtml(it.cat_badge || 'Tier')}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.4rem;">
                            <i class="${favIcon}" style="cursor: pointer; font-size: 0.93rem; ${favColor}" data-action="toggleFavorite" data-id="${SecurityService.escapeHtml(it.solicitud_id)}"></i>
                        </div>
                    </div>
                    <div>
                        <h3 style="font-size: 0.96rem; font-weight: 700; color: var(--text-main); line-height: 1.25; margin-bottom: 0.15rem;">${SecurityService.escapeHtml(it.empresa)}</h3>
                        <div style="font-size: 0.77rem; color: var(--text-dim);">${SecurityService.escapeHtml(it.ciudad || '')}, ${SecurityService.escapeHtml(it.departamento || '')} • ${it.vacantes || 1} vac · ${it.postulados || 0} post</div>
                    </div>
                    <div style="display: flex; gap: 0.22rem; flex-wrap: wrap; margin-top: 0.1rem;">
                        ${(it.stack_tags && it.stack_tags.length > 0)
                            ? it.stack_tags.slice(0, 4).map(t => `<span class="stack-chip">${SecurityService.escapeHtml(t)}</span>`).join('')
                            : `<span style="color:var(--text-dim);font-size:0.76rem;">ADSO General</span>`
                        }
                    </div>
                </div>

                <div style="background: var(--bg-canvas); border: 1px solid var(--border-muted); border-radius: var(--radius-xs); padding: 0.45rem 0.6rem; display: flex; justify-content: space-between; align-items: center; margin-top: 0.25rem;">
                    <div>
                        <span style="font-size: 0.72rem; color: var(--text-dim); text-transform: uppercase; font-weight: 600;">Rol & Afinidad ADSO</span>
                        <div class="ai-score ${AppController.aiTierClass(it.ai_tier)}" style="font-size: 0.82rem; font-weight: 700;">${SecurityService.escapeHtml(it.ai_tier_label || 'Prioridad media')}</div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.35rem;">
                        <span class="ai-score ${AppController.aiTierClass(it.ai_tier)}" style="font-size: 1.24rem; font-weight: 900; font-family: var(--font-mono);">${it.puntaje_exito || 0}</span>
                        <span class="ai-tier-chip ${AppController.aiTierClass(it.ai_tier)}">T${it.ai_tier || '?'}</span>
                    </div>
                </div>

                <div style="display: flex; justify-content: flex-end; align-items: center; border-top: 1px solid var(--border-muted); padding-top: 0.45rem; margin-top: 0.25rem;">
                    <div class="row-actions">
                        ${hasEmail ? `<a href="${SecurityService.escapeHtml(emailHref)}" ${emailTarget} class="${emailClass}" title="${emailTitle}" data-email-action="true" data-email="${SecurityService.escapeHtml(it.email)}">${emailIcon} ${emailLabel}</a>` : ''}
                        ${hasValidWA ? `<a href="${SecurityService.escapeHtml(waUrl)}" target="_blank" rel="noopener noreferrer" class="mini-btn mini-wa" title="WhatsApp"><i class="fa-brands fa-whatsapp"></i> WA</a>` : ''}
                        <button class="mini-btn" style="font-weight: 700;" data-action="openDetailModal" data-id="${SecurityService.escapeHtml(it.solicitud_id)}">Ver Detalle ↗</button>
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
            document.body.classList.remove('dock-active');
            return;
        }
        dock.style.display = 'flex';
        document.body.classList.add('dock-active');

        let html = '';
        this.store.compareList.forEach(id => {
            const it = this.store.rawData.find(d => String(d.solicitud_id) === String(id));
            if (it) {
                const name = SecurityService.escapeHtml(it.empresa);
                const short = SecurityService.escapeHtml(it.empresa.substring(0, 14));
                html += `<span class="pill-badge pill-tier-1 dock-chip" title="${name}">${short}…` +
                        `<button type="button" class="dock-chip-remove" data-action="toggleCompare" ` +
                        `data-id="${SecurityService.escapeHtml(it.solicitud_id)}" ` +
                        `aria-label="Quitar ${name} de la comparación">` +
                        `<i class="fa-solid fa-xmark" aria-hidden="true"></i></button></span>`;
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
            html += `<th style="padding: 0.5rem; text-align: left;"><strong style="color: var(--brand-primary);">${SecurityService.escapeHtml(it.empresa)}</strong><div style="font-size: 0.77rem; color: var(--text-dim);">#${it.ranking_posicion} • ${SecurityService.escapeHtml(it.cat_badge || '')}</div></th>`;
        });
        html += '</tr></thead><tbody>';

        const fields = [
            { label: "Afinidad & Tier IA", fn: it => `<strong class="ai-score ${AppController.aiTierClass(it.ai_tier)}">${it.puntaje_exito} / 100 (Tier ${it.ai_tier || '?'})</strong>` },
            { label: "Categoría", fn: it => `<span class="pill-badge pill-tier-1">${SecurityService.escapeHtml(it.cat_badge || '')}</span>` },
            { label: "Stack Tecnológico", fn: it => (it.stack_tags && it.stack_tags.length > 0) ? it.stack_tags.slice(0, 4).map(t => `<span class="stack-chip">${SecurityService.escapeHtml(t)}</span>`).join(' ') : 'ADSO General' },
            { label: "Actividad Principal", fn: it => `<div style="font-size: 0.79rem; color: var(--text-muted); line-height: 1.4;">${SecurityService.escapeHtml((it.panorama_actividad || it.funciones || '').slice(0, 140))}...</div>` },
            { label: "Vacantes / Cupos", fn: it => `<strong style="color: var(--tier-2);">${it.vacantes || 1} vacantes</strong> (${it.postulados || 0} postulados)` },
            { label: "Contacto Directo", fn: it => `<div><strong>${SecurityService.escapeHtml(it.contacto || 'RRHH')}</strong><div style="font-family: var(--font-mono); font-size: 0.77rem; color: var(--brand-primary);">${SecurityService.escapeHtml(it.email || '')}</div></div>` }
        ];

        fields.forEach(f => {
            html += `<tr style="border-bottom: 1px solid var(--border-muted);"><td style="padding: 0.5rem; font-weight: 600; color: var(--text-dim);">${f.label}</td>`;
            items.forEach(it => { html += `<td style="padding: 0.5rem;">${f.fn(it)}</td>`; });
            html += '</tr>';
        });
        html += '</tbody>';
        tbl.innerHTML = html;
        if (this.dom.compareModal) {
            this.dom.compareModal.style.display = 'flex';
            document.body.classList.add('modal-open');
            this.openModalFocus(this.dom.compareModal);
        }
    }

    closeCompareModal() {
        if (this.dom.compareModal) {
            this.dom.compareModal.style.display = 'none';
            document.body.classList.remove('modal-open');
            this.releaseModalFocus(this.dom.compareModal);
        }
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
        // ── Multi-AI Score Panel in Modal ──────────────────────────────
        const mScoreEl = this.dom.mScore;
        if (mScoreEl) {
            const ai = it.ai_scores || {};
            const aiModels = [
                { key: 'M1_RecruiterAI',  label: 'RecruiterAI',  desc: 'Prob. respuesta reclutador' },
                { key: 'M2_FitAI',        label: 'FitAI',        desc: 'Match técnico candidato' },
                { key: 'M3_GrowthAI',     label: 'GrowthAI',     desc: 'Crecimiento profesional 5A' },
                { key: 'M4_UrgencyAI',    label: 'UrgencyAI',    desc: 'Ventana y urgencia' },
                { key: 'M5_CompetenceAI', label: 'CompetenceAI', desc: 'Ventaja vs competidores' }
            ];
            const tierColor = it.ai_tier_color || '#6b7280';
            let html = `<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;">
                <span style="font-size:1.48rem;font-weight:900;font-family:var(--font-mono);color:${tierColor};">${it.puntaje_exito||0}</span>
                <div>
                    <div style="font-size:0.74rem;font-weight:700;color:${tierColor};padding:0.08rem 0.4rem;border-radius:4px;background:${tierColor}22;border:1px solid ${tierColor}44;display:inline-block;">
                        Tier ${it.ai_tier||'?'} — ${SecurityService.escapeHtml(it.ai_tier_label||'')}
                    </div>
                    <div style="font-size:0.72rem;color:var(--text-dim);margin-top:0.15rem;">Confianza de consenso: <strong style="color:var(--text-muted);">${SecurityService.escapeHtml(it.ai_consensus_confidence||'N/A')}</strong></div>
                </div>
            </div>
            <div style="display:flex;flex-direction:column;gap:0.3rem;">`;
            aiModels.forEach(m => {
                const val = ai[m.key] || 0;
                const col = val>=80?'#10b981':val>=65?'#f59e0b':val>=50?'#3b82f6':'#6b7280';
                const pct = Math.min(100, val);
                html += `<div>
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2px;">
                        <span style="font-size:0.72rem;font-weight:700;color:var(--text-muted);font-family:var(--font-mono);">${m.label}</span>
                        <span style="font-size:0.72rem;color:var(--text-dim);">${m.desc}</span>
                        <span style="font-size:0.74rem;font-weight:700;color:${col};font-family:var(--font-mono);">${val}</span>
                    </div>
                    <div style="height:4px;border-radius:2px;background:rgba(255,255,255,0.06);overflow:hidden;">
                        <div style="height:100%;width:${pct}%;background:${col};border-radius:2px;transition:width 0.6s ease;"></div>
                    </div>
                </div>`;
            });
            html += '</div>';
            mScoreEl.innerHTML = html;
        }

        setTxt(this.dom.mTierText, it.cat_badge || 'Tier 1 · Software');
        setTxt(this.dom.mVacantesText, `${it.vacantes || 1} vacantes (${it.postulados || 0} post.)`);
        setTxt(this.dom.mModalidadText, it.modalidad || 'Presencial / Híbrido');

        setTxt(this.dom.mContactName, it.contacto || 'Equipo de Selección y Gestión Humana');
        if (this.dom.mContactEmail) {
            if (it.email && it.email.includes('@')) {
                const contactSub = ModeService.asunto(it);
                const contactBody = ModeService.carta(it, 'email');
                const contactMailto = SecurityService.getMailtoUrl(it.email, contactSub, contactBody);
                this.dom.mContactEmail.innerHTML = `<a href="${SecurityService.escapeHtml(contactMailto)}" style="color: var(--tier-2); text-decoration: underline;" title="Abrir en App de Correo (${SecurityService.escapeHtml(it.email)})" data-email-action="true" data-email="${SecurityService.escapeHtml(it.email)}">${SecurityService.escapeHtml(it.email)}</a>`;
            } else {
                this.dom.mContactEmail.textContent = 'No registrado';
            }
        }
        setTxt(this.dom.mContactPhone, it.telefono || 'No registrado');
        setTxt(this.dom.mContactModalidad, it.modalidad || 'Presencial / Híbrido');

        setTxt(this.dom.mPerfil, it.perfil_requerido || 'No registrado');
        setTxt(this.dom.mFunciones, it.funciones || 'No registrado');
        setTxt(this.dom.mClosingDate, it.fecha_cierre || 'No registrada');

        // ── ÉXITO & ARGUMENTACIÓN DE RANKING (ACLI v3.0) ────────────────────
        const mPanoramaContainer = document.getElementById('mPanoramaContainer');
        if (mPanoramaContainer) {
            const posFormatted = (it.ranking_posicion || 1) < 10 ? '0' + it.ranking_posicion : it.ranking_posicion;
            
            const prosList = Array.isArray(it.ranking_pros) 
                ? it.ranking_pros 
                : (it.panorama_pros || '').split('·').filter(Boolean).map(s => s.trim());
                
            const perosList = Array.isArray(it.ranking_peros) 
                ? it.ranking_peros 
                : (it.panorama_contras || '').split('·').filter(Boolean).map(s => s.trim());

            const stackList = (it.panorama_stack_real || (it.stack_tags ? it.stack_tags.join(', ') : 'ADSO General')).split(',').map(s => s.trim()).filter(Boolean);

            mPanoramaContainer.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 0.65rem; margin-top: 0.35rem;">
                
                <!-- 1. Hero Card: Justificación de Posición en Ranking -->
                <div class="ranking-arg-card">
                    <div class="ranking-arg-header">
                        <div style="display: flex; align-items: center; gap: 0.4rem;">
                            <span class="ranking-pos-badge"><i class="fa-solid fa-trophy"></i> Puesto #${posFormatted} de 195</span>
                            <span class="pill-badge ai-tier-pill ${AppController.aiTierClass(it.ai_tier)}">${SecurityService.escapeHtml(it.cat_badge || 'Tier')}</span>
                        </div>
                        <span class="learning-pill"><i class="fa-solid fa-graduation-cap"></i> ${SecurityService.escapeHtml(it.aprendizaje_potencial || 'Software & Sistemas')}</span>
                    </div>
                    <div>
                        <div style="font-size: 0.74rem; font-weight: 800; color: var(--brand-primary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.2rem;">
                            🎯 ¿Por qué esta empresa ocupa esta posición?
                        </div>
                        <p class="ranking-justificacion-text">
                            ${SecurityService.escapeHtml(it.ranking_justificacion || it.panorama_actividad || 'Evaluación técnica basada en entorno de desarrollo, tecnologías en producción y escalabilidad profesional a 5 años.')}
                        </p>
                    </div>
                </div>

                <!-- 3. Pros Técnicos vs Los Peros (Contra-argumentos honestos) -->
                <div class="arg-grid-2">
                    <!-- Lo Bueno -->
                    <div class="arg-pro-box">
                        <div class="arg-pro-title">
                            <i class="fa-solid fa-circle-check"></i> Lo Mejor (Ventajas Técnicas)
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 0.3rem;">
                            ${prosList.map(p => `
                                <div class="arg-item">
                                    <i class="fa-solid fa-check" style="color: var(--brand-primary);"></i>
                                    <span>${SecurityService.escapeHtml(p)}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <!-- Los Peros -->
                    <div class="arg-con-box">
                        <div class="arg-con-title">
                            <i class="fa-solid fa-triangle-exclamation"></i> Los "Peros" (A considerar)
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 0.3rem;">
                            ${perosList.map(c => `
                                <div class="arg-item">
                                    <i class="fa-solid fa-circle-info" style="color: #f59e0b;"></i>
                                    <span>${SecurityService.escapeHtml(c)}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>

                <!-- 4. Stack Tecnológico Real en Producción -->
                <div style="background: var(--bg-canvas); border: 1px solid var(--border-muted); border-radius: var(--radius-xs); padding: 0.6rem 0.75rem;">
                    <div style="font-size: 0.72rem; font-weight: 700; color: var(--brand-primary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.35rem; display: flex; align-items: center; gap: 0.3rem;">
                        <i class="fa-solid fa-layer-group"></i> Tecnologías y Entorno de Producción
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.25rem;">
                        ${stackList.map(t => `<span class="stack-chip" style="font-size: 0.74rem; padding: 0.15rem 0.45rem;">${SecurityService.escapeHtml(t)}</span>`).join('')}
                    </div>
                </div>

                <!-- 5. Veredicto Técnico IA -->
                <div style="padding: 0.55rem 0.75rem; border-radius: var(--radius-xs); background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.25);">
                    <div style="font-size: 0.72rem; font-weight: 800; color: #a5b4fc; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.15rem; display: flex; align-items: center; gap: 0.3rem;">
                        <i class="fa-solid fa-robot"></i> Veredicto de Orientación Profesional ADSO
                    </div>
                    <div style="font-size: 0.81rem; color: var(--text-main); line-height: 1.55;">
                        ${SecurityService.escapeHtml(it.panorama_veredicto || 'Oportunidad evaluada bajo el índice ACLI de aprendizaje y éxito profesional.')}
                    </div>
                </div>

            </div>`;
        }

        if (it.finanzas_5anios) {
            setTxt(this.dom.mFinAcumulado5A, it.finanzas_5anios.acumulado_5a);
            setTxt(this.dom.mFinDiferencial, it.finanzas_5anios.diferencial_vs_pyme);
        }

        // Timeline
        const tl = this.dom.mTimelineGrid;
        if (tl && it.hitos_carrera) {
            let html = '';
            it.hitos_carrera.forEach(h => {
                html += `<div style="background: var(--bg-canvas); border: 1px solid var(--border-muted); border-radius: var(--radius-xs); padding: 0.45rem; font-size: 0.79rem;">
                    <span style="color: var(--text-dim); text-transform: uppercase; font-weight: 700; font-size: 0.72rem;">${SecurityService.escapeHtml(h.periodo)}</span>
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
                    <div style="background: var(--bg-canvas); border: 1px solid var(--border-muted); border-radius: var(--radius-sm); padding: 0.65rem; font-size: 0.82rem;">
                        <strong style="color: var(--tier-2);">#${idx + 1} ${SecurityService.escapeHtml(q.pregunta)}</strong>
                        <div style="color: var(--text-muted); margin: 0.3rem 0; line-height: 1.4;">${SecurityService.escapeHtml(q.respuesta_modelo)}</div>
                        <div style="color: var(--brand-primary); font-size: 0.79rem;"><i class="fa-brands fa-github"></i> ${SecurityService.escapeHtml(q.tip_github)}</div>
                    </div>
                `;
            });
            qaList.innerHTML = html;
        }

        this.updateModalFavBtn();
        this.setModalTab('panorama');
        this.setChannel('email');
        if (this.dom.detailModal) {
            this.dom.detailModal.style.display = 'flex';
            document.body.classList.add('modal-open');
            this.openModalFocus(this.dom.detailModal);
        }
    }

    closeDetailModal() {
        if (this.dom.detailModal) {
            this.dom.detailModal.style.display = 'none';
            document.body.classList.remove('modal-open');
            this.releaseModalFocus(this.dom.detailModal);
        }
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
        [this.dom.mSecPanorama, this.dom.mSecOutreach, this.dom.mSecDetails, this.dom.mSecInterview].forEach(el => {
            if (el) el.style.display = 'none';
        });

        if (tab === 'panorama') {
            this.dom.mTabPanorama?.classList.add('active');
            if (this.dom.mSecPanorama) this.dom.mSecPanorama.style.display = 'flex';
        } else if (tab === 'outreach') {
            this.dom.mTabOutreach?.classList.add('active');
            if (this.dom.mSecOutreach) this.dom.mSecOutreach.style.display = 'flex';
        } else if (tab === 'details') {
            this.dom.mTabDetails?.classList.add('active');
            if (this.dom.mSecDetails) this.dom.mSecDetails.style.display = 'flex';
        } else if (tab === 'interview') {
            this.dom.mTabInterview?.classList.add('active');
            if (this.dom.mSecInterview) this.dom.mSecInterview.style.display = 'flex';
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
            let subject = ModeService.asunto(it);

            let bodyText = ModeService.carta(it, 'email');
            if (bodyText.startsWith('Asunto:')) {
                const lines = bodyText.split('\n');
                subject = lines[0].replace(/^Asunto:\s*/i, '').trim();
                bodyText = lines.slice(2).join('\n');
            }

            if (this.dom.mOutreachHeading) {
                this.dom.mOutreachHeading.textContent = 'Carta de postulación personalizada';
            }
            if (this.dom.mOutreachBody) this.dom.mOutreachBody.textContent = bodyText;

            const hasEmail = it.email && it.email.includes('@');
            const isMobile = SecurityService.isMobile();
            const gmailLink = hasEmail ? SecurityService.getGmailUrl(it.email, subject, bodyText) : '#';
            const mailtoLink = hasEmail ? SecurityService.getMailtoUrl(it.email, subject, bodyText) : '#';

            if (this.dom.mOutreachActions) {
                let emailButtonsHtml = '';
                if (!hasEmail) {
                    emailButtonsHtml = '<span style="font-size: 0.79rem; color: var(--text-dim);">Sin correo registrado</span>';
                } else if (isMobile) {
                    // Mobile version: Directly open native email app, NO browser navigation
                    emailButtonsHtml = `<a href="${SecurityService.escapeHtml(mailtoLink)}" class="btn btn-mail-app" style="padding: 0.22rem 0.52rem;" title="Abrir en tu App de Correo (Gmail / Apple Mail / Outlook)" data-email-action="true" data-email="${SecurityService.escapeHtml(it.email)}"><i class="fa-solid fa-envelope-open-text"></i> Abrir en App de Correo</a>`;
                } else {
                    // Desktop version: Provide web compose in Gmail as primary or local mail client
                    emailButtonsHtml = `
                        <a href="${SecurityService.escapeHtml(gmailLink)}" target="_blank" rel="noopener noreferrer" class="btn btn-gmail" style="padding: 0.22rem 0.52rem;" title="Redactar correo de postulación directamente en Gmail"><i class="fa-brands fa-google"></i> Redactar en Gmail</a>
                        <a href="${SecurityService.escapeHtml(mailtoLink)}" class="btn" style="padding: 0.22rem 0.52rem;" title="Abrir en cliente de correo local (Outlook / Apple Mail)" data-email-action="true" data-email="${SecurityService.escapeHtml(it.email)}"><i class="fa-solid fa-envelope"></i> Correo (App)</a>
                    `;
                }

                this.dom.mOutreachActions.innerHTML = `
                    <button class="btn" style="padding: 0.22rem 0.52rem;" data-action="copyOutreach"><i class="fa-regular fa-copy"></i> Copiar Correo</button>
                    ${emailButtonsHtml}
                    <a href="https://drive.google.com/file/d/1r89tS4JI4OKwSuzyyfPhGn4ylZTRlrln/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn-cv-drive" style="padding: 0.22rem 0.52rem; font-size: 0.79rem;" title="Abrir Hoja de Vida oficial (PDF)"><i class="fa-solid fa-file-pdf"></i> Hoja de Vida <span class="cv-mini-badge">PDF</span></a>
                    <a href="https://drive.google.com/drive/folders/1BZ-qBNdPeYsxW84zIq_ls97UkPlQcHyN?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn-certs-link" style="padding: 0.22rem 0.52rem; font-size: 0.79rem;" title="Abrir Certificados Académicos en Google Drive"><i class="fa-brands fa-google-drive"></i> Certificados <span class="cv-mini-badge">DRIVE</span></a>
                `;
            }
        } else if (ch === 'wa') {
            let waMsg = ModeService.carta(it, 'wa');
            if (this.dom.mOutreachHeading) {
                this.dom.mOutreachHeading.textContent = 'Mensaje directo de WhatsApp';
            }
            if (this.dom.mOutreachBody) this.dom.mOutreachBody.textContent = waMsg;

            const hasValidWA = SecurityService.isValidMobile(it.telefono);
            const waUrl = hasValidWA ? SecurityService.getWhatsAppUrl(it.telefono, waMsg) : '';

            if (this.dom.mOutreachActions) {
                this.dom.mOutreachActions.innerHTML = `
                    <button class="btn" style="padding: 0.2rem 0.5rem;" data-action="copyOutreach"><i class="fa-regular fa-copy"></i> Copiar Mensaje</button>
                    ${hasValidWA ? `<a href="${SecurityService.escapeHtml(waUrl)}" target="_blank" rel="noopener noreferrer" class="btn btn-whatsapp" style="padding: 0.2rem 0.5rem;"><i class="fa-brands fa-whatsapp"></i> Abrir Chat</a>` : '<span style="font-size: 0.79rem; color: var(--text-dim);"><i class="fa-solid fa-phone"></i> Teléfono PBX / Fijo</span>'}
                `;
            }
        } else if (ch === 'linkedin') {
            let liMsg = ModeService.carta(it, 'linkedin');
            if (this.dom.mOutreachHeading) {
                this.dom.mOutreachHeading.textContent = 'Nota de conexión en LinkedIn (menos de 300 caracteres)';
            }
            if (this.dom.mOutreachBody) this.dom.mOutreachBody.textContent = liMsg;

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

    // =========================================================================
    // 5. SGVA LIVE SYNCHRONIZATION & TELEMETRY ENGINE
    // =========================================================================
    /**
     * Panel de estado flotante: arranca plegado para no tapar la tabla y
     * recuerda la preferencia del usuario entre visitas.
     */
    refreshTierCounts() {
        const counts = this.store.rawData.reduce((acc, d) => {
            acc[d.cat_id] = (acc[d.cat_id] || 0) + 1;
            return acc;
        }, {});
        const total = this.store.rawData.length;

        document.querySelectorAll('.tier-seg-btn').forEach(btn => {
            const tier = btn.getAttribute('data-tier');
            const pill = btn.querySelector('.seg-pill');
            if (pill) pill.textContent = tier ? (counts[tier] || 0) : total;
        });

        if (this.dom.pillTotalCount) this.dom.pillTotalCount.textContent = total;
        if (this.dom.lblTotalCount) this.dom.lblTotalCount.textContent = total;
        const bannerTotal = document.getElementById('lblBannerTotal');
        if (bannerTotal) bannerTotal.textContent = total;
    }

    /**
     * El panel mostraba valores incrustados por scripts/update_sync_badge.py,
     * que hay que ejecutar a mano antes de cada commit: quedaba congelado en
     * el ultimo commit en que alguien se acordo de correrlo. Ahora el estado
     * se consulta a la API publica de GitHub, que es la fuente real de lo que
     * Workers Builds acaba de publicar.
     */
    async initRepoStatus() {
        const REPO = 'lakerstrake/sena-adso-caprendizaje';
        const DATA_PATH = 'output/assets/data/empresas.json';
        const TTL_MS = 30 * 60 * 1000;   // 60 peticiones/hora sin token: se cachea.
        const CACHE_KEY = 'repo_status_cache';

        const cached = this._readRepoCache(CACHE_KEY, TTL_MS);
        if (cached) {
            this.renderRepoStatus(cached);
            return;
        }

        try {
            const base = `https://api.github.com/repos/${REPO}/commits`;
            const [headRes, dataRes] = await Promise.all([
                fetch(`${base}?sha=main&per_page=1`, { headers: { Accept: 'application/vnd.github+json' } }),
                fetch(`${base}?sha=main&path=${encodeURIComponent(DATA_PATH)}&per_page=1`, { headers: { Accept: 'application/vnd.github+json' } })
            ]);
            if (!headRes.ok) throw new Error(`GitHub respondio ${headRes.status}`);

            const head = (await headRes.json())[0];
            const dataCommit = dataRes.ok ? (await dataRes.json())[0] : null;

            const status = {
                hash: head.sha.substring(0, 7),
                message: head.commit.message.split('\n')[0],
                committedAt: head.commit.committer.date,
                dataCommittedAt: dataCommit ? dataCommit.commit.committer.date : null,
                fetchedAt: Date.now()
            };
            try { localStorage.setItem(CACHE_KEY, JSON.stringify(status)); } catch (e) { /* cuota llena */ }
            this.renderRepoStatus(status);
        } catch (err) {
            // Sin red o limite de peticiones agotado: se marca como desconocido
            // en vez de dejar en pantalla una fecha antigua que parece vigente.
            this.renderRepoStatus(null);
        }
    }

    _readRepoCache(key, ttlMs) {
        try {
            const raw = localStorage.getItem(key);
            if (!raw) return null;
            const data = JSON.parse(raw);
            return (Date.now() - (data.fetchedAt || 0) < ttlMs) ? data : null;
        } catch (e) {
            return null;
        }
    }

    renderRepoStatus(status) {
        const set = (id, text, title) => {
            const el = document.getElementById(id);
            if (!el) return;
            el.textContent = text;
            if (title) el.title = title;
        };

        if (!status) {
            set('syncDate', 'Estado no disponible');
            set('syncHash', '—');
            set('syncMsg', 'No se pudo consultar GitHub en este momento.');
            set('cfDate', 'Estado no disponible');
            return;
        }

        const commitDate = new Date(status.committedAt);
        set('syncDate', this.formatEsDateTime(commitDate), commitDate.toLocaleString('es-CO'));
        set('syncHash', status.hash);
        const msg = status.message.length > 55 ? `${status.message.substring(0, 52)}...` : status.message;
        set('syncMsg', msg, status.message);

        // Workers Builds publica desde ese mismo commit, unos instantes despues.
        set('cfDate', this.formatEsDateTime(commitDate), 'Publicado desde el commit ' + status.hash);

        if (status.dataCommittedAt) {
            const dataDate = new Date(status.dataCommittedAt);
            set('sgvaDate', this.formatEsDateTime(dataDate), 'Ultimo cambio del dataset en el repositorio');
            set('sgvaMsg', `Dataset actualizado por ultima vez el ${this.formatEsDateTime(dataDate)}`);
        }
    }

    formatEsDateTime(dateObj) {
        const months = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
        const hrs = String(dateObj.getHours()).padStart(2, '0');
        const mins = String(dateObj.getMinutes()).padStart(2, '0');
        return `${dateObj.getDate()} ${months[dateObj.getMonth()]} ${dateObj.getFullYear()}, ${hrs}:${mins}`;
    }

    async exportData(fmt) {
        if (typeof XLSX === 'undefined') {
            this.showToast('Cargando motor de exportación...');
            try {
                await new Promise((resolve, reject) => {
                    const script = document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js';
                    script.onload = resolve;
                    script.onerror = reject;
                    document.head.appendChild(script);
                });
            } catch (err) {
                this.showToast('Error al cargar librería de exportación');
                return;
            }
        }
        if (typeof XLSX !== 'undefined') {
            const ws = XLSX.utils.json_to_sheet(this.store.filteredData);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "ADSO_SENA");
            if (fmt === 'xlsx') XLSX.writeFile(wb, "postulaciones_adso_sena.xlsx");
            else XLSX.writeFile(wb, "postulaciones_adso_sena.csv");
            this.showToast(`Archivo ${fmt.toUpperCase()} descargado con éxito`);
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
