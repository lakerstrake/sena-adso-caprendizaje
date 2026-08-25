import json
import os

data_path = r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.json"
with open(data_path, "r", encoding="utf-8") as f:
    data = json.load(f)

json_data_str = json.dumps(data, ensure_ascii=False)

html_template = f"""<!DOCTYPE html>
<html lang="es" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SENA · ADSO | Directorio Estratégico de Aprendices</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
    <style>
        :root {{
            --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            
            /* Clean Minimalist SaaS Dark Palette */
            --bg-canvas: #090d16;
            --bg-surface: #0f172a;
            --bg-surface-raised: #1e293b;
            --bg-surface-hover: #273549;
            --bg-subtle: rgba(255, 255, 255, 0.03);
            
            --border-muted: rgba(255, 255, 255, 0.07);
            --border-default: rgba(255, 255, 255, 0.12);
            --border-focused: #3b82f6;
            
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
            --text-inverse: #0f172a;
            
            --brand-primary: #10b981;
            --brand-primary-bg: rgba(16, 185, 129, 0.08);
            
            --tier-1: #a855f7;
            --tier-1-bg: rgba(168, 85, 247, 0.08);
            --tier-2: #38bdf8;
            --tier-2-bg: rgba(56, 189, 248, 0.08);
            --tier-3: #f59e0b;
            --tier-3-bg: rgba(245, 158, 11, 0.08);
            --tier-4: #94a3b8;
            --tier-4-bg: rgba(148, 163, 184, 0.08);
            --tier-5: #f43f5e;
            --tier-5-bg: rgba(244, 63, 94, 0.08);
            
            --whatsapp-color: #25D366;
            --linkedin-color: #0A66C2;
            --drive-color: #34A853;
            
            --radius-xs: 4px;
            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 14px;
            
            --shadow-subtle: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
            --shadow-overlay: 0 12px 32px -4px rgba(0, 0, 0, 0.7);
            
            --transition-fast: 0.12s ease;
        }}

        [data-theme="light"] {{
            --bg-canvas: #f8fafc;
            --bg-surface: #ffffff;
            --bg-surface-raised: #f1f5f9;
            --bg-surface-hover: #e2e8f0;
            --bg-subtle: rgba(0, 0, 0, 0.02);
            
            --border-muted: #e2e8f0;
            --border-default: #cbd5e1;
            --border-focused: #2563eb;
            
            --text-main: #0f172a;
            --text-muted: #475569;
            --text-dim: #94a3b8;
            --text-inverse: #ffffff;
            
            --brand-primary: #059669;
            --brand-primary-bg: rgba(5, 150, 105, 0.06);
            
            --tier-1: #7c3aed;
            --tier-1-bg: rgba(124, 58, 237, 0.06);
            --tier-2: #0284c7;
            --tier-2-bg: rgba(2, 132, 199, 0.06);
            --tier-3: #d97706;
            --tier-3-bg: rgba(217, 119, 6, 0.06);
            --tier-4: #64748b;
            --tier-4-bg: rgba(100, 116, 139, 0.06);
            --tier-5: #e11d48;
            --tier-5-bg: rgba(225, 29, 72, 0.06);
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        html, body {{
            height: 100%;
        }}
        body {{
            font-family: var(--font-sans);
            background-color: var(--bg-canvas);
            color: var(--text-main);
            line-height: 1.4;
            font-size: 13px;
            -webkit-font-smoothing: antialiased;
            display: flex;
            flex-direction: column;
        }}

        /* Clean Top Navigation Bar */
        .navbar {{
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border-muted);
            position: sticky;
            top: 0;
            z-index: 50;
            flex-shrink: 0;
        }}

        .navbar-container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 0.45rem 1.25rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            white-space: nowrap;
        }}

        .brand-section {{
            display: flex;
            align-items: center;
            gap: 0.55rem;
            flex-shrink: 0;
        }}

        .brand-badge {{
            width: 24px;
            height: 24px;
            background: var(--brand-primary);
            color: #fff;
            border-radius: var(--radius-xs);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.72rem;
            font-weight: 700;
            flex-shrink: 0;
        }}

        .brand-title {{
            display: flex;
            align-items: baseline;
            gap: 0.35rem;
        }}

        .brand-title h1 {{
            font-size: 0.84rem;
            font-weight: 700;
            letter-spacing: -0.2px;
            color: var(--text-main);
            white-space: nowrap;
        }}

        .brand-title span {{
            font-size: 0.68rem;
            color: var(--text-muted);
            white-space: nowrap;
        }}

        /* Center Nav Pills */
        .nav-pills {{
            display: flex;
            align-items: center;
            background: var(--bg-canvas);
            border: 1px solid var(--border-muted);
            padding: 2px;
            border-radius: var(--radius-sm);
            gap: 2px;
            flex-shrink: 0;
        }}

        .nav-pill-btn {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 0.28rem 0.65rem;
            font-size: 0.72rem;
            font-weight: 600;
            font-family: var(--font-sans);
            border-radius: calc(var(--radius-sm) - 2px);
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            transition: var(--transition-fast);
            white-space: nowrap;
        }}

        .nav-pill-btn:hover {{ color: var(--text-main); }}
        .nav-pill-btn.active {{
            background: var(--bg-surface-raised);
            color: var(--text-main);
            box-shadow: var(--shadow-subtle);
        }}

        /* Modern Elegant Counter Badges */
        .count-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.08rem 0.4rem;
            border-radius: 10px;
            font-size: 0.64rem;
            font-weight: 700;
            font-family: var(--font-mono);
            background: var(--bg-surface-raised);
            color: var(--text-muted);
            border: 1px solid var(--border-muted);
            line-height: 1;
        }}

        .nav-pill-btn.active .count-badge {{
            background: rgba(16, 185, 129, 0.12);
            color: var(--brand-primary);
            border-color: rgba(16, 185, 129, 0.25);
        }}

        /* Candidate Mini Pill with CV link */
        .candidate-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            background: var(--bg-subtle);
            border: 1px solid var(--border-muted);
            padding: 0.25rem 0.65rem;
            border-radius: 20px;
            font-size: 0.7rem;
            white-space: nowrap;
            flex-shrink: 0;
        }}

        .candidate-pill a {{
            color: var(--text-muted);
            text-decoration: none;
            transition: var(--transition-fast);
            display: inline-flex;
            align-items: center;
            gap: 0.2rem;
        }}
        .candidate-pill a:hover {{ color: var(--text-main); }}

        /* Action Buttons */
        .btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.3rem;
            padding: 0.28rem 0.55rem;
            font-size: 0.7rem;
            font-weight: 600;
            font-family: var(--font-sans);
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-muted);
            background: var(--bg-surface);
            color: var(--text-main);
            cursor: pointer;
            transition: var(--transition-fast);
            text-decoration: none;
            white-space: nowrap;
        }}

        .btn:hover {{
            background: var(--bg-surface-raised);
            border-color: var(--border-default);
        }}

        .btn-primary {{
            background: var(--brand-primary);
            border-color: var(--brand-primary);
            color: #fff;
        }}
        .btn-primary:hover {{ background: #059669; }}

        .btn-whatsapp {{
            background: rgba(37, 211, 102, 0.1);
            color: var(--whatsapp-color);
            border-color: rgba(37, 211, 102, 0.25);
        }}
        .btn-whatsapp:hover, .btn-whatsapp.active {{
            background: var(--whatsapp-color);
            color: #fff;
            border-color: var(--whatsapp-color);
        }}

        .btn-linkedin {{
            background: rgba(10, 102, 194, 0.1);
            color: #38bdf8;
            border-color: rgba(10, 102, 194, 0.25);
        }}
        .btn-linkedin:hover, .btn-linkedin.active {{
            background: var(--linkedin-color);
            color: #fff;
            border-color: var(--linkedin-color);
        }}

        .btn-icon {{ width: 26px; height: 26px; padding: 0; }}

        /* Main Workspace Container */
        .main-content {{
            max-width: 1600px;
            width: 100%;
            margin: 0 auto;
            padding: 0.65rem 1.25rem 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            flex: 1;
            min-height: 0;
        }}

        /* Subtle Anti-Blocking Notice (Dismissible & Minimalist) */
        .notice-banner {{
            background: rgba(245, 158, 11, 0.05);
            border: 1px solid rgba(245, 158, 11, 0.2);
            border-radius: var(--radius-sm);
            padding: 0.35rem 0.75rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.7rem;
            color: var(--text-muted);
            flex-shrink: 0;
        }}

        .notice-banner strong {{ color: var(--tier-3); }}

        /* Unified Streamlined Filter Deck */
        .filter-deck {{
            background: var(--bg-surface);
            border: 1px solid var(--border-muted);
            border-radius: var(--radius-md);
            padding: 0.55rem 0.75rem;
            display: flex;
            flex-direction: column;
            gap: 0.45rem;
            flex-shrink: 0;
        }}

        .filter-deck-primary {{
            display: flex;
            align-items: center;
            gap: 0.55rem;
            flex-wrap: wrap;
        }}

        .search-box {{
            flex: 1;
            min-width: 250px;
            position: relative;
            display: flex;
            align-items: center;
        }}

        .search-box i {{
            position: absolute;
            left: 0.65rem;
            color: var(--text-dim);
            font-size: 0.72rem;
        }}

        .search-box input {{
            width: 100%;
            padding: 0.38rem 1.5rem 0.38rem 1.9rem;
            background: var(--bg-canvas);
            border: 1px solid var(--border-muted);
            border-radius: var(--radius-sm);
            color: var(--text-main);
            font-size: 0.74rem;
            font-family: var(--font-sans);
            outline: none;
            transition: var(--transition-fast);
        }}

        .search-box input:focus {{
            border-color: var(--border-focused);
            background: var(--bg-surface);
        }}

        /* Segmented Tier Quick Filters */
        .tier-segments {{
            display: flex;
            align-items: center;
            background: var(--bg-canvas);
            border: 1px solid var(--border-muted);
            padding: 2px;
            border-radius: var(--radius-sm);
            gap: 2px;
            overflow-x: auto;
        }}

        .tier-seg-btn {{
            background: transparent;
            border: none;
            padding: 0.25rem 0.55rem;
            font-size: 0.68rem;
            font-weight: 600;
            color: var(--text-muted);
            border-radius: calc(var(--radius-sm) - 2px);
            cursor: pointer;
            white-space: nowrap;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            transition: var(--transition-fast);
        }}

        .tier-seg-btn:hover {{ color: var(--text-main); }}
        .tier-seg-btn.active {{
            background: var(--bg-surface-raised);
            color: var(--text-main);
            font-weight: 700;
        }}

        .tier-seg-btn.seg-1.active {{ color: var(--tier-1); }}
        .tier-seg-btn.seg-2.active {{ color: var(--tier-2); }}
        .tier-seg-btn.seg-3.active {{ color: var(--tier-3); }}

        .seg-pill {{
            font-size: 0.62rem;
            font-family: var(--font-mono);
            padding: 0.02rem 0.3rem;
            border-radius: 8px;
            background: var(--bg-surface);
            border: 1px solid var(--border-muted);
        }}

        /* Tech Stack Chips Bar (Clean Horizontal Scroll) */
        .stack-row {{
            display: flex;
            align-items: center;
            gap: 0.35rem;
            overflow-x: auto;
            padding-bottom: 1px;
        }}

        .stack-row span {{
            font-size: 0.62rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            color: var(--text-dim);
            margin-right: 0.15rem;
            white-space: nowrap;
        }}

        .chip-btn {{
            background: var(--bg-canvas);
            border: 1px solid var(--border-muted);
            color: var(--text-muted);
            padding: 0.12rem 0.45rem;
            border-radius: 12px;
            font-size: 0.66rem;
            font-weight: 500;
            cursor: pointer;
            white-space: nowrap;
            transition: var(--transition-fast);
        }}

        .chip-btn:hover {{ color: var(--text-main); border-color: var(--border-default); }}
        .chip-btn.active {{
            background: var(--tier-1-bg);
            color: var(--tier-1);
            border-color: var(--tier-1);
            font-weight: 600;
        }}

        /* Collapsible Secondary Filters Bar */
        .secondary-filters-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 0.4rem;
            padding-top: 0.4rem;
            border-top: 1px solid var(--border-muted);
        }}

        .filter-select-wrap {{
            display: flex;
            flex-direction: column;
            gap: 0.1rem;
        }}

        .filter-select-wrap label {{
            font-size: 0.58rem;
            text-transform: uppercase;
            color: var(--text-dim);
            font-weight: 600;
        }}

        .select-sm {{
            width: 100%;
            background: var(--bg-canvas);
            border: 1px solid var(--border-muted);
            border-radius: var(--radius-xs);
            color: var(--text-main);
            padding: 0.24rem 0.4rem;
            font-size: 0.7rem;
            font-family: var(--font-sans);
            outline: none;
            cursor: pointer;
        }}

        /* Table Area Header & Controls */
        .table-toolbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 0.1rem;
            font-size: 0.7rem;
            color: var(--text-muted);
            flex-shrink: 0;
        }}

        .table-toolbar strong {{ color: var(--text-main); font-family: var(--font-mono); }}

        /* Premium Minimalist Table */
        .table-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-muted);
            border-radius: var(--radius-md);
            overflow: hidden;
            box-shadow: var(--shadow-subtle);
            display: flex;
            flex-direction: column;
            flex: 1;
            min-height: 0;
        }}

        .table-container {{
            overflow: auto;
            flex: 1;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.72rem;
            text-align: left;
        }}

        .data-table thead {{
            position: sticky;
            top: 0;
            z-index: 10;
            background: var(--bg-surface-raised);
        }}

        .data-table th {{
            padding: 0.45rem 0.6rem;
            font-size: 0.62rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border-muted);
            cursor: pointer;
            user-select: none;
            white-space: nowrap;
        }}

        .data-table th:hover {{ color: var(--text-main); }}

        .data-table td {{
            padding: 0.42rem 0.6rem;
            border-bottom: 1px solid var(--border-muted);
            vertical-align: middle;
            color: var(--text-main);
            line-height: 1.25;
        }}

        .data-table tbody tr {{
            transition: var(--transition-fast);
            cursor: pointer;
        }}

        .data-table tbody tr:hover {{
            background: var(--bg-surface-hover);
        }}

        /* Refined Typography Rows */
        .cell-main {{
            display: flex;
            flex-direction: column;
            gap: 1px;
        }}

        .cell-title {{
            font-weight: 600;
            color: var(--text-main);
            font-size: 0.74rem;
            letter-spacing: -0.1px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 280px;
        }}

        .cell-sub {{
            font-size: 0.64rem;
            color: var(--text-dim);
            white-space: nowrap;
        }}

        /* Subtle Modern Badges */
        .pill-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.2rem;
            padding: 0.1rem 0.38rem;
            border-radius: var(--radius-xs);
            font-size: 0.64rem;
            font-weight: 600;
            white-space: nowrap;
        }}

        .pill-tier-1 {{ background: var(--tier-1-bg); color: var(--tier-1); }}
        .pill-tier-2 {{ background: var(--tier-2-bg); color: var(--tier-2); }}
        .pill-tier-3 {{ background: var(--tier-3-bg); color: var(--tier-3); }}
        .pill-tier-4 {{ background: var(--tier-4-bg); color: var(--tier-4); }}
        .pill-tier-5 {{ background: var(--tier-5-bg); color: var(--tier-5); }}

        .rating-chip {{
            display: inline-flex;
            align-items: center;
            gap: 0.2rem;
            font-family: var(--font-mono);
            font-size: 0.68rem;
            font-weight: 600;
            color: var(--tier-3);
            white-space: nowrap;
        }}

        .ratio-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            display: inline-block;
            flex-shrink: 0;
        }}
        .ratio-green {{ background: var(--brand-primary); }}
        .ratio-blue {{ background: var(--tier-2); }}
        .ratio-amber {{ background: var(--tier-3); }}
        .ratio-rose {{ background: var(--tier-5); }}

        /* Action Buttons Group in Row */
        .row-actions {{
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 0.25rem;
            white-space: nowrap;
        }}

        .mini-btn {{
            padding: 0.18rem 0.4rem;
            font-size: 0.65rem;
            font-weight: 600;
            border-radius: var(--radius-xs);
            border: 1px solid var(--border-muted);
            background: var(--bg-canvas);
            color: var(--text-muted);
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.2rem;
            transition: var(--transition-fast);
        }}

        .mini-btn:hover {{ background: var(--bg-surface-raised); color: var(--text-main); }}
        .mini-wa {{ color: var(--whatsapp-color); }}
        .mini-wa:hover {{ background: rgba(37, 211, 102, 0.15); color: var(--whatsapp-color); }}
        .mini-mail {{ color: var(--tier-2); }}
        .mini-mail:hover {{ background: rgba(56, 189, 248, 0.15); color: var(--tier-2); }}

        /* Pagination Footer */
        .table-footer {{
            padding: 0.38rem 0.75rem;
            border-top: 1px solid var(--border-muted);
            background: var(--bg-surface-raised);
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.7rem;
            color: var(--text-muted);
            flex-shrink: 0;
        }}

        /* Floating Comparison Dock */
        .dock-bar {{
            position: fixed;
            bottom: 1rem;
            left: 50%;
            transform: translateX(-50%);
            background: var(--bg-surface);
            border: 1px solid var(--border-default);
            border-radius: var(--radius-md);
            padding: 0.45rem 0.85rem;
            box-shadow: var(--shadow-overlay);
            display: none;
            align-items: center;
            gap: 0.75rem;
            z-index: 90;
        }}

        /* Cards Grid View */
        .cards-view-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 0.65rem;
            overflow-y: auto;
            flex: 1;
        }}

        .clean-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-muted);
            border-radius: var(--radius-md);
            padding: 0.75rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 0.55rem;
            cursor: pointer;
            transition: var(--transition-fast);
        }}

        .clean-card:hover {{
            border-color: var(--border-default);
            transform: translateY(-1px);
        }}

        /* Modal Overlay & Structure */
        .modal-backdrop {{
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(4px);
            z-index: 100;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 1rem;
        }}

        .modal-panel {{
            background: var(--bg-surface);
            border: 1px solid var(--border-default);
            border-radius: var(--radius-lg);
            width: 100%;
            max-width: 880px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: var(--shadow-overlay);
            display: flex;
            flex-direction: column;
        }}

        .modal-header {{
            padding: 0.85rem 1.15rem;
            border-bottom: 1px solid var(--border-muted);
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            background: var(--bg-surface);
            z-index: 5;
        }}

        .modal-body {{
            padding: 1rem 1.15rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }}

        /* Stat Quad Cards in Modal */
        .stat-quad {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.45rem;
        }}

        .stat-box {{
            background: var(--bg-canvas);
            border: 1px solid var(--border-muted);
            border-radius: var(--radius-sm);
            padding: 0.45rem 0.6rem;
            text-align: center;
        }}

        .stat-box span {{
            font-size: 0.6rem;
            text-transform: uppercase;
            color: var(--text-dim);
            font-weight: 600;
            display: block;
        }}

        .stat-box strong {{
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--text-main);
            font-family: var(--font-mono);
        }}

        /* Modal Sub Tabs */
        .modal-tabs {{
            display: flex;
            background: var(--bg-canvas);
            border: 1px solid var(--border-muted);
            padding: 2px;
            border-radius: var(--radius-sm);
            gap: 2px;
        }}

        .modal-tab-item {{
            flex: 1;
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 0.32rem 0.45rem;
            font-size: 0.7rem;
            font-weight: 600;
            font-family: var(--font-sans);
            border-radius: var(--radius-xs);
            cursor: pointer;
            transition: var(--transition-fast);
            text-align: center;
        }}

        .modal-tab-item.active {{
            background: var(--bg-surface-raised);
            color: var(--text-main);
        }}

        /* Toast Feedback */
        .toast-msg {{
            position: fixed;
            bottom: 1.25rem;
            right: 1.25rem;
            background: var(--text-main);
            color: var(--text-inverse);
            padding: 0.45rem 0.8rem;
            border-radius: var(--radius-xs);
            font-size: 0.74rem;
            font-weight: 600;
            box-shadow: var(--shadow-overlay);
            display: none;
            z-index: 200;
        }}

        /* Strategy Tab Clean Design */
        .strategy-view {{
            display: flex;
            flex-direction: column;
            gap: 0.85rem;
            overflow-y: auto;
            flex: 1;
        }}

        .strategy-header {{
            background: var(--bg-surface);
            border: 1px solid var(--border-muted);
            border-radius: var(--radius-md);
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
        }}

        .strategy-columns {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 0.75rem;
        }}

        .strategy-card-clean {{
            background: var(--bg-surface);
            border: 1px solid var(--border-muted);
            border-radius: var(--radius-md);
            padding: 0.85rem 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.45rem;
        }}

        @media (max-width: 900px) {{
            .navbar-container {{ flex-direction: column; align-items: flex-start; }}
            .stat-quad {{ grid-template-columns: 1fr 1fr; }}
            .secondary-filters-row {{ grid-template-columns: 1fr 1fr; }}
        }}
    </style>
</head>
<body>

    <!-- Clean Top Navigation Bar -->
    <nav class="navbar">
        <div class="navbar-container">
            <div class="brand-section">
                <div class="brand-badge"><i class="fa-solid fa-code"></i></div>
                <div class="brand-title">
                    <h1>SENA · ADSO</h1>
                    <span>Directorio Estratégico</span>
                </div>
            </div>

            <!-- Center Navigation Pills (Clean Badges) -->
            <div class="nav-pills">
                <button class="nav-pill-btn active" id="pillDirectory" onclick="switchNavTab('directory')">
                    <i class="fa-solid fa-list-ul"></i> Directorio <span class="count-badge" id="pillTotalCount">179</span>
                </button>
                <button class="nav-pill-btn" id="pillStrategy" onclick="switchNavTab('strategy')">
                    <i class="fa-solid fa-rocket"></i> Escalabilidad & Finanzas
                </button>
                <button class="nav-pill-btn" id="pillFavs" onclick="switchNavTab('favs')">
                    <i class="fa-regular fa-bookmark"></i> Preseleccionadas <span class="count-badge" id="pillFavCount">0</span>
                </button>
            </div>

            <!-- Candidate Profile & Exports with CV link -->
            <div style="display: flex; align-items: center; gap: 0.4rem; flex-shrink: 0;">
                <div class="candidate-pill">
                    <i class="fa-solid fa-user-check" style="color: var(--brand-primary);"></i>
                    <strong style="color: var(--text-main);">Juan Manuel Lagos</strong>
                    <span style="color: var(--text-dim);">•</span>
                    <a href="https://drive.google.com/drive/folders/1BZ-qBNdPeYsxW84zIq_ls97UkPlQcHyN" target="_blank" title="Ver Hoja de Vida (CV)" style="color: #38bdf8; font-weight: 600;"><i class="fa-solid fa-file-lines"></i> Hoja de Vida</a>
                    <span style="color: var(--text-dim);">•</span>
                    <a href="https://github.com/lakerstrake" target="_blank" title="Portafolio en GitHub"><i class="fa-brands fa-github"></i> GitHub</a>
                    <span style="color: var(--text-dim);">•</span>
                    <a href="https://linkedin.com/in/juan-manuel-lagos-monroy" target="_blank" title="LinkedIn"><i class="fa-brands fa-linkedin"></i> LinkedIn</a>
                    <span style="color: var(--text-dim);">•</span>
                    <a href="https://drive.google.com/drive/folders/1BZ-qBNdPeYsxW84zIq_ls97UkPlQcHyN" target="_blank" title="Certificados y Cursos en Google Drive" style="color: var(--drive-color);"><i class="fa-brands fa-google-drive"></i> Certificados</a>
                </div>
                <button class="btn" onclick="exportData('xlsx')" title="Descargar Excel"><i class="fa-solid fa-file-excel" style="color: #10b981;"></i></button>
                <button class="btn" onclick="exportData('csv')" title="Descargar CSV"><i class="fa-solid fa-file-csv" style="color: #38bdf8;"></i></button>
                <button class="btn btn-icon" onclick="toggleTheme()" id="themeBtn" title="Tema"><i class="fa-solid fa-sun" id="themeIcon"></i></button>
            </div>
        </div>
    </nav>

    <!-- Main Workspace -->
    <main class="main-content">

        <!-- Dismissible Minimalist Anti-Blocking Banner -->
        <div class="notice-banner" id="antiBlockNotice">
            <div style="display: flex; align-items: center; gap: 0.4rem;">
                <i class="fa-solid fa-shield-halved" style="color: var(--tier-3);"></i>
                <span><strong>Protocolo Anti-Bloqueo:</strong> Contacta directamente a las empresas por <strong>Correo</strong>, <strong>WhatsApp</strong> o <strong>LinkedIn</strong> con tu CV para no bloquear tu perfil 15 días en SGVA.</span>
            </div>
            <i class="fa-solid fa-xmark" style="cursor: pointer; opacity: 0.6;" onclick="document.getElementById('antiBlockNotice').style.display='none'"></i>
        </div>

        <!-- DIRECTORY VIEW -->
        <div id="sectionDirectory" style="display: flex; flex-direction: column; flex: 1; min-height: 0; gap: 0.45rem;">

            <!-- Unified Streamlined Filter Deck -->
            <div class="filter-deck">
                <!-- Search and Quick Tier Segments -->
                <div class="filter-deck-primary">
                    <div class="search-box">
                        <i class="fa-solid fa-magnifying-glass"></i>
                        <input type="text" id="mainSearch" placeholder="Buscar por empresa, NIT, ciudad, stack (React, Node, SQL) o funciones...">
                    </div>

                    <!-- Tier Quick Segment Filters -->
                    <div class="tier-segments">
                        <button class="tier-seg-btn active" onclick="setTierFilter('')">Todos <span class="seg-pill">179</span></button>
                        <button class="tier-seg-btn seg-1" onclick="setTierFilter('TIER_1')">Tier 1 · Software <span class="seg-pill">11</span></button>
                        <button class="tier-seg-btn seg-2" onclick="setTierFilter('TIER_2')">Tier 2 · Sistemas <span class="seg-pill">31</span></button>
                        <button class="tier-seg-btn seg-3" onclick="setTierFilter('TIER_3')">Tier 3 · Soporte TI <span class="seg-pill">58</span></button>
                        <button class="tier-seg-btn" onclick="setTierFilter('TIER_4')">Tier 4 · Operación <span class="seg-pill">45</span></button>
                        <button class="tier-seg-btn" onclick="setTierFilter('TIER_5')">Tier 5 <span class="seg-pill">34</span></button>
                    </div>

                    <button class="btn" onclick="toggleSecondaryFilters()" id="toggleFiltersBtn">
                        <i class="fa-solid fa-sliders"></i> Filtros <span class="count-badge" id="activeFilterBadge" style="margin-left: 2px;">0</span>
                    </button>
                </div>

                <!-- Tech Stack Quick Filter Chips -->
                <div class="stack-row">
                    <span>Stack ADSO:</span>
                    <button class="chip-btn active" onclick="setStackChipFilter('')">Todos</button>
                    <button class="chip-btn" onclick="setStackChipFilter('SQL')">SQL / Bases de Datos</button>
                    <button class="chip-btn" onclick="setStackChipFilter('Frontend / Web')">Frontend & React</button>
                    <button class="chip-btn" onclick="setStackChipFilter('Java')">Java / Spring</button>
                    <button class="chip-btn" onclick="setStackChipFilter('Python')">Python</button>
                    <button class="chip-btn" onclick="setStackChipFilter('.NET / C#')">.NET / C#</button>
                    <button class="chip-btn" onclick="setStackChipFilter('Git')">Git / GitHub</button>
                    <button class="chip-btn" onclick="setStackChipFilter('APIs REST')">APIs REST</button>
                    <button class="chip-btn" onclick="setStackChipFilter('QA / Testing')">QA / Testing</button>
                    <button class="chip-btn" onclick="setStackChipFilter('Cloud')">Cloud AWS/Azure</button>
                    <button class="chip-btn" onclick="setStackChipFilter('ERP / Sistemas')">ERP / Sistemas</button>
                </div>

                <!-- Collapsible Advanced Filters -->
                <div class="secondary-filters-row" id="secondaryFiltersRow" style="display: none;">
                    <div class="filter-select-wrap">
                        <label>Canal Directo</label>
                        <select class="select-sm" id="filterChannel">
                            <option value="">Todos los canales</option>
                            <option value="WHATSAPP">Con WhatsApp Directo (129)</option>
                            <option value="EMAIL">Con Correo Electrónico (175)</option>
                        </select>
                    </div>
                    <div class="filter-select-wrap">
                        <label>Nivel de Competencia</label>
                        <select class="select-sm" id="filterCompetition">
                            <option value="">Cualquier competencia</option>
                            <option value="ZERO">Sin postulados (0 candidatos)</option>
                            <option value="LOW">Baja (≤ 1.0 postulados/cupo)</option>
                            <option value="MOD">Moderada (1.1 - 2.0 ratio)</option>
                            <option value="MED">Media (2.1 - 5.0 ratio)</option>
                        </select>
                    </div>
                    <div class="filter-select-wrap">
                        <label>Departamento</label>
                        <select class="select-sm" id="filterDpto"><option value="">Todos</option></select>
                    </div>
                    <div class="filter-select-wrap">
                        <label>Ciudad</label>
                        <select class="select-sm" id="filterCity"><option value="">Todas</option></select>
                    </div>
                    <div class="filter-select-wrap">
                        <label>Criterio de Orden</label>
                        <select class="select-sm" id="filterSort">
                            <option value="ranking_asc">Afinidad y Éxito (#01 a #179)</option>
                            <option value="escalabilidad_desc">Mayor Escalabilidad Profesional</option>
                            <option value="reputation_desc">Mayor Calidad Web (★)</option>
                            <option value="comp_asc">Menor Competencia</option>
                            <option value="vacancies_desc">Mayor Cantidad de Vacantes</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Table Header Toolbar -->
            <div class="table-toolbar">
                <div>Mostrando <strong id="lblVisibleCount">179</strong> de <strong id="lblTotalCount">179</strong> vacantes</div>
                <div style="display: flex; align-items: center; gap: 0.45rem;">
                    <button class="btn" style="padding: 0.18rem 0.45rem; font-size: 0.66rem;" onclick="resetFilters()">Restablecer</button>
                    <div class="nav-pills" style="padding: 1px;">
                        <button class="nav-pill-btn active" id="btnLayoutTable" onclick="setLayout('table')" style="padding: 0.18rem 0.45rem;"><i class="fa-solid fa-table-list"></i></button>
                        <button class="nav-pill-btn" id="btnLayoutCards" onclick="setLayout('cards')" style="padding: 0.18rem 0.45rem;"><i class="fa-solid fa-border-all"></i></button>
                    </div>
                </div>
            </div>

            <!-- Main Data Table Container -->
            <div class="table-card" id="tableCardWrap">
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th style="width: 24px; text-align: center;"><i class="fa-solid fa-code-compare" title="Comparar"></i></th>
                                <th style="width: 24px;"></th>
                                <th style="width: 38px;" onclick="sortTable('ranking_posicion')">Pos</th>
                                <th onclick="sortTable('empresa')">Empresa & Ubicación</th>
                                <th style="width: 130px;" onclick="sortTable('cat_nivel')">Clasificación</th>
                                <th style="width: 70px;" onclick="sortTable('puntaje_exito')">Puntos</th>
                                <th style="width: 80px;" onclick="sortTable('reputacion_rating')">Calidad Web</th>
                                <th style="width: 95px;" onclick="sortTable('escalabilidad_score')">Escala</th>
                                <th style="width: 110px;" onclick="sortTable('competencia_ratio')">Competencia</th>
                                <th style="width: 115px;">Apoyo / 5A</th>
                                <th style="width: 160px; text-align: right;">Contacto Directo</th>
                            </tr>
                        </thead>
                        <tbody id="tableBody"></tbody>
                    </table>
                </div>
                <!-- Pagination -->
                <div class="table-footer">
                    <span id="lblPagination">Página 1 de 4</span>
                    <div style="display: flex; gap: 3px;" id="paginationPages"></div>
                </div>
            </div>

            <!-- Cards Container -->
            <div class="cards-view-grid" id="cardsGridWrap" style="display: none;"></div>
        </div>

        <!-- STRATEGY & FINANCIALS VIEW -->
        <div id="sectionStrategy" class="strategy-view" style="display: none;">
            <div class="strategy-header">
                <div>
                    <h2 style="font-size: 1.05rem; font-weight: 700; color: var(--text-main);">Proyección Financiera & Escalabilidad a 5 Años</h2>
                    <p style="color: var(--text-muted); font-size: 0.74rem; margin-top: 0.15rem;">
                        Impacto profesional para <strong>Juan Manuel Lagos Monroy</strong> según el tipo de empresa seleccionada.
                    </p>
                </div>
                <div style="background: var(--bg-canvas); border: 1px solid var(--border-muted); padding: 0.5rem 1rem; border-radius: var(--radius-sm); text-align: center;">
                    <div style="font-size: 1.2rem; font-weight: 700; color: var(--tier-1); font-family: var(--font-mono);">+$320M COP</div>
                    <div style="font-size: 0.62rem; color: var(--text-dim); text-transform: uppercase;">Diferencial Acumulado Tier 1 vs Pyme</div>
                </div>
            </div>

            <div class="strategy-columns">
                <!-- Financial Table -->
                <div class="strategy-card-clean" style="grid-column: 1/-1;">
                    <div style="font-weight: 700; font-size: 0.8rem; color: var(--tier-1); display: flex; align-items: center; gap: 0.35rem;">
                        <i class="fa-solid fa-coins"></i> Ingresos Acumulados Proyectados (1 a 5 Años)
                    </div>
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.72rem; margin-top: 0.35rem;">
                        <thead>
                            <tr style="background: var(--bg-canvas); border-bottom: 1px solid var(--border-muted);">
                                <th style="padding: 0.45rem; text-align: left;">Categoría</th>
                                <th style="padding: 0.45rem;">Práctica (6m)</th>
                                <th style="padding: 0.45rem;">Año 1 (Junior)</th>
                                <th style="padding: 0.45rem;">Acumulado 3A</th>
                                <th style="padding: 0.45rem;">Acumulado 5A</th>
                                <th style="padding: 0.45rem; text-align: left;">Calidad de Vida</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom: 1px solid var(--border-muted);">
                                <td style="padding: 0.45rem;"><strong style="color: var(--tier-1);">Tier 1 · Software & Tech</strong></td>
                                <td style="padding: 0.45rem; text-align: center;">$8.541.000 COP</td>
                                <td style="padding: 0.45rem; text-align: center;">$45.000.000 COP</td>
                                <td style="padding: 0.45rem; text-align: center;"><strong style="color: var(--brand-primary);">$185.000.000</strong></td>
                                <td style="padding: 0.45rem; text-align: center;"><strong style="color: var(--tier-1);">$450M a $720M+ COP</strong></td>
                                <td style="padding: 0.45rem; color: var(--text-muted);">Remoto / Híbrido, autonomía y valorización global.</td>
                            </tr>
                            <tr style="border-bottom: 1px solid var(--border-muted);">
                                <td style="padding: 0.45rem;"><strong style="color: var(--tier-2);">Tier 2 · Sistemas & Datos</strong></td>
                                <td style="padding: 0.45rem; text-align: center;">$8.541.000 COP</td>
                                <td style="padding: 0.45rem; text-align: center;">$36.000.000 COP</td>
                                <td style="padding: 0.45rem; text-align: center;">$150.000.000</td>
                                <td style="padding: 0.45rem; text-align: center;"><strong>$320M a $480M COP</strong></td>
                                <td style="padding: 0.55rem; color: var(--text-muted);">Gran estabilidad bancaria e industrial.</td>
                            </tr>
                            <tr style="border-bottom: 1px solid var(--border-muted);">
                                <td style="padding: 0.45rem;"><strong style="color: var(--tier-3);">Tier 3 · Soporte TI</strong></td>
                                <td style="padding: 0.45rem; text-align: center;">$8.541.000 COP</td>
                                <td style="padding: 0.45rem; text-align: center;">$28.000.000 COP</td>
                                <td style="padding: 0.45rem; text-align: center;">$115.000.000</td>
                                <td style="padding: 0.45rem; text-align: center;">$210M a $310M COP</td>
                                <td style="padding: 0.45rem; color: var(--text-muted);">Mayormente presencial y turnos técnicos.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- 4 Hitos -->
                <div class="strategy-card-clean">
                    <div style="font-weight: 700; font-size: 0.78rem; color: var(--tier-2);"><i class="fa-solid fa-timeline"></i> Trayectoria de 4 Hitos ADSO</div>
                    <ul style="list-style: none; display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.7rem; color: var(--text-muted);">
                        <li><strong>Año 0 (Práctica):</strong> Apoyo legal ($1.423.500 COP + EPS/ARL). Foco en código y Scrum.</li>
                        <li><strong>Año 1 (Junior Dev):</strong> $3.0M a $4.8M COP al graduarte del tecnólogo.</li>
                        <li><strong>Año 3 (Mid-Level):</strong> $5.5M a $8.5M COP diseñando microservicios y cloud.</li>
                        <li><strong>Año 5+ (Senior / Remoto):</strong> $10M a $22M+ COP ($3.000 - $5.500 USD/mes).</li>
                    </ul>
                </div>

                <!-- Protocolo Anti Bloqueo -->
                <div class="strategy-card-clean">
                    <div style="font-weight: 700; font-size: 0.78rem; color: var(--tier-3);"><i class="fa-solid fa-shield-halved"></i> Estrategia Anti-Bloqueo</div>
                    <ul style="list-style: none; display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.7rem; color: var(--text-muted);">
                        <li><span style="color: var(--tier-5);">✗</span> <strong>NO</strong> te postules en SGVA (te bloquea 15 días hábiles a 1 sola empresa).</li>
                        <li><span style="color: var(--brand-primary);">✓</span> <strong>SÍ</strong> contacta simultáneamente a 20 o 30 empresas por Correo, WhatsApp y LinkedIn con tu CV.</li>
                    </ul>
                </div>
            </div>
        </div>

    </main>

    <!-- FLOATING COMPARISON DOCK -->
    <div class="dock-bar" id="comparisonDock">
        <span style="font-size: 0.72rem; font-weight: 700;"><i class="fa-solid fa-code-compare" style="color: var(--tier-1);"></i> Comparando <span class="count-badge" id="dockCount" style="margin-left: 2px;">0</span> de 3:</span>
        <div id="dockList" style="display: flex; gap: 0.35rem;"></div>
        <div style="display: flex; gap: 0.3rem;">
            <button class="btn btn-primary" style="padding: 0.2rem 0.5rem; font-size: 0.68rem;" onclick="openCompareModal()">Ver Comparativa</button>
            <button class="btn" style="padding: 0.2rem 0.4rem; font-size: 0.68rem;" onclick="clearComparison()">Limpiar</button>
        </div>
    </div>

    <!-- COMPARISON MODAL -->
    <div class="modal-backdrop" id="compareModal" onclick="if(event.target.id==='compareModal') closeCompareModal()">
        <div class="modal-panel" style="max-width: 1040px;">
            <div class="modal-header">
                <div>
                    <h2 style="font-size: 0.95rem; font-weight: 700;"><i class="fa-solid fa-code-compare" style="color: var(--tier-1);"></i> Comparación Directa Frente a Frente</h2>
                    <span style="font-size: 0.7rem; color: var(--text-muted);">Evaluación comparativa de vacantes seleccionadas</span>
                </div>
                <button class="btn btn-icon" onclick="closeCompareModal()"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="modal-body">
                <table style="width: 100%; border-collapse: collapse; font-size: 0.72rem;" id="compareTable"></table>
            </div>
        </div>
    </div>

    <!-- DETAIL MODAL -->
    <div class="modal-backdrop" id="detailModal" onclick="if(event.target.id==='detailModal') closeModal()">
        <div class="modal-panel" id="modalPanel">
            <div class="modal-header">
                <div>
                    <h2 id="mTitle" style="font-size: 1rem; font-weight: 700;">Empresa</h2>
                    <span id="mSubtitle" style="font-size: 0.72rem; color: var(--text-muted);">Ubicación • NIT</span>
                </div>
                <div style="display: flex; gap: 0.35rem;">
                    <button class="btn btn-icon" id="mFavBtn" onclick="toggleModalFav()"><i class="fa-regular fa-bookmark"></i></button>
                    <button class="btn btn-icon" onclick="closeModal()"><i class="fa-solid fa-xmark"></i></button>
                </div>
            </div>

            <div class="modal-body">
                <!-- 4 Top Stat Boxes -->
                <div class="stat-quad">
                    <div class="stat-box">
                        <span>Afinidad ADSO</span>
                        <strong id="mScore" style="color: var(--tier-1);">95 / 100</strong>
                    </div>
                    <div class="stat-box">
                        <span>Escalabilidad</span>
                        <strong id="mEsc" style="color: var(--tier-2);">96 / 100</strong>
                    </div>
                    <div class="stat-box">
                        <span>Calidad Web</span>
                        <strong id="mRating" style="color: var(--tier-3);">★ 4.3</strong>
                    </div>
                    <div class="stat-box">
                        <span>Apoyo Mensual</span>
                        <strong id="mSupport" style="color: var(--brand-primary);">$1.423.500</strong>
                    </div>
                </div>

                <!-- Modal Sub-Tabs -->
                <div class="modal-tabs">
                    <button class="modal-tab-item active" id="mTabOutreach" onclick="setModalTab('outreach')">
                        <i class="fa-solid fa-paper-plane"></i> Contacto Directo
                    </button>
                    <button class="modal-tab-item" id="mTabInterview" onclick="setModalTab('interview')">
                        <i class="fa-solid fa-brain"></i> Simulador de Entrevista
                    </button>
                    <button class="modal-tab-item" id="mTabCareer" onclick="setModalTab('career')">
                        <i class="fa-solid fa-chart-line"></i> Proyección & Finanzas
                    </button>
                    <button class="modal-tab-item" id="mTabDetails" onclick="setModalTab('details')">
                        <i class="fa-solid fa-file-lines"></i> Perfil & Funciones
                    </button>
                </div>

                <!-- SECTION 1: OUTREACH -->
                <div id="mSecOutreach" style="display: flex; flex-direction: column; gap: 0.65rem;">
                    <div style="display: flex; gap: 0.35rem;">
                        <button class="btn btn-primary" id="mChEmail" onclick="setChannel('email')" style="flex: 1;"><i class="fa-solid fa-envelope"></i> Correo Formal</button>
                        <button class="btn" id="mChWA" onclick="setChannel('wa')" style="flex: 1;"><i class="fa-brands fa-whatsapp"></i> WhatsApp Directo</button>
                        <button class="btn" id="mChLinkedIn" onclick="setChannel('linkedin')" style="flex: 1;"><i class="fa-brands fa-linkedin"></i> Nota LinkedIn</button>
                    </div>

                    <div style="background: var(--bg-canvas); border: 1px solid var(--border-muted); border-radius: var(--radius-sm); padding: 0.75rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                            <strong style="font-size: 0.74rem;" id="mOutreachHeading">Carta Formal de Postulación Institucional</strong>
                            <div id="mOutreachActions" style="display: flex; gap: 0.3rem;"></div>
                        </div>
                        <div id="mOutreachBody" style="font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-main); white-space: pre-wrap; max-height: 180px; overflow-y: auto; user-select: text;"></div>
                    </div>

                    <!-- Direct Contacts Summary -->
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.5rem; font-size: 0.72rem; background: var(--bg-subtle); padding: 0.65rem; border-radius: var(--radius-xs); border: 1px solid var(--border-muted);">
                        <div><span style="color: var(--text-dim);">Contacto / RRHH:</span> <strong id="mContactName"></strong></div>
                        <div><span style="color: var(--text-dim);">Correo:</span> <strong id="mContactEmail" style="font-family: var(--font-mono);"></strong></div>
                        <div><span style="color: var(--text-dim);">Teléfono / WhatsApp:</span> <strong id="mContactPhone" style="font-family: var(--font-mono);"></strong></div>
                        <div><span style="color: var(--text-dim);">Modalidad:</span> <strong id="mContactModalidad" style="color: var(--tier-2);"></strong></div>
                    </div>
                </div>

                <!-- SECTION 2: INTERVIEW SIMULATOR -->
                <div id="mSecInterview" style="display: none; flex-direction: column; gap: 0.5rem;">
                    <div id="mInterviewList" style="display: flex; flex-direction: column; gap: 0.45rem;"></div>
                </div>

                <!-- SECTION 3: CAREER & FINANCES -->
                <div id="mSecCareer" style="display: none; flex-direction: column; gap: 0.65rem;">
                    <div style="background: var(--bg-canvas); border: 1px solid var(--border-muted); border-radius: var(--radius-sm); padding: 0.75rem;">
                        <strong style="color: var(--tier-1); font-size: 0.76rem;" id="mCurvaTitulo"></strong>
                        <p style="font-size: 0.72rem; color: var(--text-muted); margin-top: 0.2rem;" id="mCurvaDetalle"></p>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.4rem;" id="mTimelineGrid"></div>
                    <div style="background: var(--tier-1-bg); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: var(--radius-xs); padding: 0.55rem 0.75rem; font-size: 0.72rem;">
                        <strong style="color: var(--tier-1);">Acumulado 5 Años:</strong> <span id="mFinAcumulado5A"></span> • <span id="mFinDiferencial" style="color: var(--brand-primary); font-weight: 600;"></span>
                    </div>
                </div>

                <!-- SECTION 4: DETAILS -->
                <div id="mSecDetails" style="display: none; flex-direction: column; gap: 0.55rem;">
                    <div style="background: var(--bg-canvas); border: 1px solid var(--border-muted); border-radius: var(--radius-sm); padding: 0.7rem;">
                        <span style="font-size: 0.62rem; text-transform: uppercase; color: var(--text-dim); font-weight: 600;">Perfil Requerido</span>
                        <p style="font-size: 0.74rem; color: var(--text-main); margin-top: 0.2rem; white-space: pre-wrap;" id="mPerfil"></p>
                    </div>
                    <div style="background: var(--bg-canvas); border: 1px solid var(--border-muted); border-radius: var(--radius-sm); padding: 0.7rem;">
                        <span style="font-size: 0.62rem; text-transform: uppercase; color: var(--text-dim); font-weight: 600;">Funciones Asignadas</span>
                        <p style="font-size: 0.74rem; color: var(--text-main); margin-top: 0.2rem; white-space: pre-wrap;" id="mFunciones"></p>
                    </div>
                </div>
            </div>

            <div style="padding: 0.65rem 1.25rem; border-top: 1px solid var(--border-muted); display: flex; justify-content: space-between; align-items: center; background: var(--bg-surface-raised);">
                <span style="font-size: 0.7rem; color: var(--text-dim);">Cierre: <strong id="mClosingDate" style="color: var(--tier-3); font-family: var(--font-mono);"></strong></span>
                <button class="btn btn-primary" onclick="closeModal()">Listo</button>
            </div>
        </div>
    </div>

    <!-- Notification Toast -->
    <div class="toast-msg" id="toastMsg">Mensaje</div>

    <script>
        const RAW_DATA = {json_data_str};
        let currentData = [...RAW_DATA];
        let activeTier = '';
        let activeStack = '';
        let filterFavs = false;
        let viewMode = 'table';
        let favorites = JSON.parse(localStorage.getItem('cap_favs') || '[]');
        let compareList = JSON.parse(localStorage.getItem('cap_comp') || '[]');
        let activeItem = null;
        let activeChannel = 'email';
        let currentPage = 1;
        let pageSize = 50;
        let sortCol = 'ranking_posicion';
        let sortAsc = true;

        const CANDIDATE = {{
            name: "Juan Manuel Lagos Monroy",
            phone: "(+57) 300 727 9875",
            email: "jmlagos2003@gmail.com",
            github: "https://github.com/lakerstrake",
            linkedin: "https://linkedin.com/in/juan-manuel-lagos-monroy",
            cv_drive: "https://drive.google.com/drive/folders/1BZ-qBNdPeYsxW84zIq_ls97UkPlQcHyN",
            program: "Tecnólogo en Análisis y Desarrollo de Software (ADSO) - SENA"
        }};

        document.addEventListener('DOMContentLoaded', () => {{
            initTheme();
            initFilters();
            updateFavPill();
            updateDock();
            applyFilters();
            setupEvents();
        }});

        function initTheme() {{
            const saved = localStorage.getItem('cap_theme') || 'dark';
            document.documentElement.setAttribute('data-theme', saved);
            document.getElementById('themeIcon').className = saved === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        }}

        function toggleTheme() {{
            const cur = document.documentElement.getAttribute('data-theme');
            const next = cur === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('cap_theme', next);
            document.getElementById('themeIcon').className = next === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        }}

        function switchNavTab(tab) {{
            document.querySelectorAll('.nav-pill-btn').forEach(b => b.classList.remove('active'));
            const secDir = document.getElementById('sectionDirectory');
            const secStrat = document.getElementById('sectionStrategy');

            if (tab === 'directory') {{
                document.getElementById('pillDirectory').classList.add('active');
                secDir.style.display = 'flex';
                secStrat.style.display = 'none';
                filterFavs = false;
                applyFilters();
            }} else if (tab === 'strategy') {{
                document.getElementById('pillStrategy').classList.add('active');
                secDir.style.display = 'none';
                secStrat.style.display = 'flex';
            }} else if (tab === 'favs') {{
                document.getElementById('pillFavs').classList.add('active');
                secDir.style.display = 'flex';
                secStrat.style.display = 'none';
                filterFavs = true;
                applyFilters();
            }}
        }}

        function setTierFilter(tier) {{
            activeTier = tier;
            document.querySelectorAll('.tier-seg-btn').forEach(b => b.classList.remove('active'));
            event.target.closest('.tier-seg-btn').classList.add('active');
            currentPage = 1;
            applyFilters();
        }}

        function setStackChipFilter(tag) {{
            activeStack = tag;
            document.querySelectorAll('.chip-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            currentPage = 1;
            applyFilters();
        }}

        function toggleSecondaryFilters() {{
            const row = document.getElementById('secondaryFiltersRow');
            const btn = document.getElementById('toggleFiltersBtn');
            if (row.style.display === 'none') {{
                row.style.display = 'grid';
                btn.classList.add('btn-primary');
            }} else {{
                row.style.display = 'none';
                btn.classList.remove('btn-primary');
            }}
        }}

        function updateFilterBadge() {{
            let count = 0;
            if (document.getElementById('filterChannel').value) count++;
            if (document.getElementById('filterCompetition').value) count++;
            if (document.getElementById('filterDpto').value) count++;
            if (document.getElementById('filterCity').value) count++;
            if (document.getElementById('filterSort').value !== 'ranking_asc') count++;
            document.getElementById('activeFilterBadge').textContent = count;
        }}

        function setupEvents() {{
            const search = document.getElementById('mainSearch');
            search.addEventListener('input', () => {{
                currentPage = 1;
                applyFilters();
            }});

            ['filterChannel', 'filterCompetition', 'filterDpto', 'filterCity', 'filterSort'].forEach(id => {{
                document.getElementById(id).addEventListener('change', () => {{
                    updateFilterBadge();
                    currentPage = 1;
                    applyFilters();
                }});
            }});

            document.addEventListener('keydown', (e) => {{
                if (e.key === 'Escape') {{ closeModal(); closeCompareModal(); }}
            }});
        }}

        function initFilters() {{
            const dptos = [...new Set(RAW_DATA.map(d => d.departamento).filter(Boolean))].sort();
            const dptoEl = document.getElementById('filterDpto');
            dptos.forEach(d => {{
                const opt = document.createElement('option');
                opt.value = d;
                opt.textContent = d;
                dptoEl.appendChild(opt);
            }});

            dptoEl.addEventListener('change', () => {{
                const cityEl = document.getElementById('filterCity');
                cityEl.innerHTML = '<option value="">Todas</option>';
                const selDpto = dptoEl.value;
                const relevant = selDpto ? RAW_DATA.filter(d => d.departamento === selDpto) : RAW_DATA;
                const cities = [...new Set(relevant.map(d => d.ciudad.trim()).filter(Boolean))].sort();
                cities.forEach(c => {{
                    const opt = document.createElement('option');
                    opt.value = c;
                    opt.textContent = c;
                    cityEl.appendChild(opt);
                }});
            }});
        }}

        function resetFilters() {{
            document.getElementById('mainSearch').value = '';
            document.getElementById('filterChannel').value = '';
            document.getElementById('filterCompetition').value = '';
            document.getElementById('filterDpto').value = '';
            document.getElementById('filterCity').value = '';
            document.getElementById('filterSort').value = 'ranking_asc';
            activeTier = '';
            activeStack = '';
            filterFavs = false;
            document.querySelectorAll('.tier-seg-btn').forEach(b => b.classList.remove('active'));
            document.querySelector('.tier-seg-btn')?.classList.add('active');
            document.querySelectorAll('.chip-btn').forEach(b => b.classList.remove('active'));
            document.querySelector('.chip-btn')?.classList.add('active');
            updateFilterBadge();
            currentPage = 1;
            applyFilters();
            showToast('Filtros restablecidos');
        }}

        function updateFavPill() {{
            document.getElementById('pillFavCount').textContent = favorites.length;
        }}

        function isFav(id) {{ return favorites.includes(id); }}

        function toggleFav(id, event) {{
            if (event) event.stopPropagation();
            if (isFav(id)) favorites = favorites.filter(x => x !== id);
            else favorites.push(id);
            localStorage.setItem('cap_favs', JSON.stringify(favorites));
            updateFavPill();
            if (filterFavs) applyFilters();
            else {{
                if (viewMode === 'table') renderTable();
                else renderCards();
            }}
            if (activeItem && activeItem.solicitud_id === id) updateModalFavBtn();
        }}

        function toggleModalFav() {{
            if (activeItem) toggleFav(activeItem.solicitud_id);
        }}

        function updateModalFavBtn() {{
            const btn = document.getElementById('mFavBtn');
            if (btn && activeItem) {{
                btn.innerHTML = isFav(activeItem.solicitud_id) ? '<i class="fa-solid fa-bookmark" style="color: var(--tier-3);"></i>' : '<i class="fa-regular fa-bookmark"></i>';
            }}
        }}

        // Comparison Dock
        function isComp(id) {{ return compareList.includes(id); }}

        function toggleComp(id, event) {{
            if (event) event.stopPropagation();
            if (isComp(id)) compareList = compareList.filter(x => x !== id);
            else {{
                if (compareList.length >= 3) {{
                    showToast('Máximo 3 empresas para comparar');
                    return;
                }}
                compareList.push(id);
            }}
            localStorage.setItem('cap_comp', JSON.stringify(compareList));
            updateDock();
            if (viewMode === 'table') renderTable();
            else renderCards();
        }}

        function clearComparison() {{
            compareList = [];
            localStorage.setItem('cap_comp', JSON.stringify(compareList));
            updateDock();
            if (viewMode === 'table') renderTable();
            else renderCards();
        }}

        function updateDock() {{
            const dock = document.getElementById('comparisonDock');
            const countEl = document.getElementById('dockCount');
            const listEl = document.getElementById('dockList');
            if (!dock) return;

            countEl.textContent = compareList.length;
            if (compareList.length === 0) {{
                dock.style.display = 'none';
                return;
            }}
            dock.style.display = 'flex';
            let html = '';
            compareList.forEach(id => {{
                const it = RAW_DATA.find(d => String(d.solicitud_id) === String(id));
                if (it) {{
                    html += `<span class="pill-badge pill-tier-1">${{it.empresa.substring(0, 14)}}... <i class="fa-solid fa-xmark" style="cursor: pointer; margin-left: 2px;" onclick="toggleComp('${{it.solicitud_id}}', event)"></i></span>`;
                }}
            }});
            listEl.innerHTML = html;
        }}

        function openCompareModal() {{
            if (compareList.length < 2) {{
                showToast('Selecciona al menos 2 empresas');
                return;
            }}
            const items = compareList.map(id => RAW_DATA.find(d => String(d.solicitud_id) === String(id))).filter(Boolean);
            const tbl = document.getElementById('compareTable');
            let html = '<thead><tr><th style="padding: 0.5rem; text-align: left;">Criterio</th>';
            items.forEach(it => {{
                html += `<th style="padding: 0.5rem; text-align: left;"><strong style="color: var(--brand-primary);">${{it.empresa}}</strong><div style="font-size: 0.65rem; color: var(--text-dim);">#${{it.ranking_posicion}} • ${{it.cat_badge}}</div></th>`;
            }});
            html += '</tr></thead><tbody>';

            const fields = [
                {{ label: "Afinidad & Puntos", fn: it => `<strong style="color: var(--tier-1);">${{it.puntaje_exito}} / 100</strong>` }},
                {{ label: "Reputación Web", fn: it => `★ ${{it.reputacion_rating ? it.reputacion_rating.toFixed(1) : '3.8'}} (${{it.reputacion_fuente}})` }},
                {{ label: "Escalabilidad", fn: it => `<strong style="color: var(--tier-2);">${{it.escalabilidad_score}}/100</strong> (${{it.escalabilidad_nivel}})` }},
                {{ label: "Apoyo Práctica", fn: it => `<strong style="color: var(--brand-primary);">${{it.apoyo_sostenimiento}}</strong>` }},
                {{ label: "5A Salario & Acumulado", fn: it => `<strong>${{it.techo_salarial_5anios}}</strong><div style="font-size: 0.65rem; color: var(--brand-primary);">${{it.finanzas_5anios ? it.finanzas_5anios.acumulado_5a : ''}}</div>` }},
                {{ label: "Competencia", fn: it => `${{it.vacantes}} vac. vs ${{it.postulados}} post. (Ratio: ${{it.competencia_ratio}})` }},
                {{ label: "Contacto Directo", fn: it => `${{it.contacto || 'RRHH'}} • ${{it.email || ''}} • ${{it.telefono || ''}}` }}
            ];

            fields.forEach(f => {{
                html += `<tr style="border-bottom: 1px solid var(--border-muted);"><td style="padding: 0.5rem; font-weight: 600; color: var(--text-dim);">${{f.label}}</td>`;
                items.forEach(it => {{ html += `<td style="padding: 0.5rem;">${{f.fn(it)}}</td>`; }});
                html += '</tr>';
            }});
            html += '</tbody>';
            tbl.innerHTML = html;
            document.getElementById('compareModal').style.display = 'flex';
        }}

        function closeCompareModal() {{
            document.getElementById('compareModal').style.display = 'none';
        }}

        function applyFilters() {{
            const query = document.getElementById('mainSearch').value.toLowerCase().trim();
            const ch = document.getElementById('filterChannel').value;
            const comp = document.getElementById('filterCompetition').value;
            const dpto = document.getElementById('filterDpto').value;
            const city = document.getElementById('filterCity').value;
            const sort = document.getElementById('filterSort').value;

            currentData = RAW_DATA.filter(it => {{
                if (filterFavs && !isFav(it.solicitud_id)) return false;
                if (activeTier && it.cat_id !== activeTier) return false;
                if (activeStack && (!it.stack_tags || !it.stack_tags.includes(activeStack))) return false;
                if (ch === 'WHATSAPP' && !it.is_whatsapp) return false;
                if (ch === 'EMAIL' && (!it.email || !it.email.includes('@'))) return false;
                if (comp && it.facilidad_code !== comp) return false;

                if (query) {{
                    const text = `${{it.empresa}} ${{it.nit}} ${{it.ciudad}} ${{it.departamento}} ${{it.funciones}} ${{it.perfil_requerido}} ${{it.contacto}} ${{it.email}} ${{it.telefono}}`.toLowerCase();
                    if (!text.includes(query)) return false;
                }}

                if (dpto && it.departamento !== dpto) return false;
                if (city && it.ciudad.trim() !== city) return false;

                return true;
            }});

            // Sort
            currentData.sort((a, b) => {{
                if (sort === 'ranking_asc') return (a.ranking_posicion || 0) - (b.ranking_posicion || 0);
                if (sort === 'escalabilidad_desc') return (b.escalabilidad_score || 0) - (a.escalabilidad_score || 0);
                if (sort === 'reputation_desc') return (b.reputacion_rating || 0) - (a.reputacion_rating || 0);
                if (sort === 'comp_asc') return (a.competencia_ratio || 0) - (b.competencia_ratio || 0);
                if (sort === 'vacancies_desc') return (b.vacantes || 0) - (a.vacantes || 0);
                return 0;
            }});

            document.getElementById('lblVisibleCount').textContent = currentData.length;

            if (viewMode === 'table') renderTable();
            else renderCards();
        }}

        function sortTable(col) {{
            if (sortCol === col) sortAsc = !sortAsc;
            else {{ sortCol = col; sortAsc = true; }}
            currentData.sort((a, b) => {{
                let valA = a[col];
                let valB = b[col];
                if (typeof valA === 'string') return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
                return sortAsc ? (valA - valB) : (valB - valA);
            }});
            renderTable();
        }}

        function renderTable() {{
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';
            const total = currentData.length;
            const totalPages = Math.ceil(total / pageSize) || 1;
            if (currentPage > totalPages) currentPage = totalPages;

            const start = (currentPage - 1) * pageSize;
            const pageSlice = currentData.slice(start, start + pageSize);

            if (total === 0) {{
                tbody.innerHTML = `<tr><td colspan="11" style="text-align: center; padding: 2rem; color: var(--text-dim);">No se encontraron vacantes con estos criterios.</td></tr>`;
                document.getElementById('lblPagination').textContent = '0 resultados';
                document.getElementById('paginationPages').innerHTML = '';
                return;
            }}

            pageSlice.forEach(it => {{
                const tr = document.createElement('tr');
                tr.onclick = () => openModal(it);

                const favIcon = isFav(it.solicitud_id) ? 'fa-solid fa-bookmark' : 'fa-regular fa-bookmark';
                const favColor = isFav(it.solicitud_id) ? 'color: var(--tier-3);' : '';
                const compCheck = isComp(it.solicitud_id) ? 'checked' : '';

                let tierPill = `<span class="pill-badge pill-tier-1">${{it.cat_badge}}</span>`;
                if (it.cat_id === 'TIER_2') tierPill = `<span class="pill-badge pill-tier-2">${{it.cat_badge}}</span>`;
                else if (it.cat_id === 'TIER_3') tierPill = `<span class="pill-badge pill-tier-3">${{it.cat_badge}}</span>`;
                else if (it.cat_id === 'TIER_4') tierPill = `<span class="pill-badge pill-tier-4">${{it.cat_badge}}</span>`;
                else if (it.cat_id === 'TIER_5') tierPill = `<span class="pill-badge pill-tier-5">${{it.cat_badge}}</span>`;

                let dotClass = 'ratio-green';
                if (it.competencia_ratio > 5.0) dotClass = 'ratio-rose';
                else if (it.competencia_ratio > 2.0) dotClass = 'ratio-amber';
                else if (it.competencia_ratio > 1.0) dotClass = 'ratio-blue';

                const hasEmail = it.email && it.email.includes('@');
                const quickMail = hasEmail ? `mailto:${{it.email}}?subject=${{encodeURIComponent(`Postulación Contrato de Aprendizaje ADSO SENA - ${{CANDIDATE.name}}`)}}&body=${{encodeURIComponent(it.correo_formal_completo || '')}}` : '#';

                let actions = '';
                if (hasEmail) actions += `<a href="${{quickMail}}" class="mini-btn mini-mail" title="Enviar correo formal"><i class="fa-solid fa-envelope"></i></a>`;
                if (it.is_whatsapp && it.whatsapp_url) actions += `<a href="${{it.whatsapp_url}}" target="_blank" class="mini-btn mini-wa" title="WhatsApp"><i class="fa-brands fa-whatsapp"></i></a>`;
                if (it.linkedin_contact_search_url) actions += `<a href="${{it.linkedin_contact_search_url}}" target="_blank" class="mini-btn" title="LinkedIn"><i class="fa-brands fa-linkedin" style="color: var(--linkedin-color);"></i></a>`;
                actions += `<button class="mini-btn" style="font-weight: 700;" onclick="openModalById('${{it.solicitud_id}}')">Detalle</button>`;

                // Clean 1-line or sleek 2-line formatting for Apoyo and Competencia
                const cleanApoyo = "$1.423.500 COP";
                const cleanTecho5A = it.techo_salarial_5anios ? it.techo_salarial_5anios.split('(')[0].replace('COP','').trim() : '$10M-$22M';

                tr.innerHTML = `
                    <td style="text-align: center;" onclick="event.stopPropagation();">
                        <input type="checkbox" ${{compCheck}} onchange="toggleComp('${{it.solicitud_id}}', event)">
                    </td>
                    <td onclick="event.stopPropagation();">
                        <i class="${{favIcon}}" style="cursor: pointer; ${{favColor}}" onclick="toggleFav('${{it.solicitud_id}}', event)"></i>
                    </td>
                    <td style="font-family: var(--font-mono); font-weight: 700; color: var(--text-dim);">#${{it.ranking_posicion < 10 ? '0' + it.ranking_posicion : it.ranking_posicion}}</td>
                    <td>
                        <div class="cell-main">
                            <span class="cell-title" title="${{it.empresa}}">${{it.empresa}}</span>
                            <span class="cell-sub">${{it.ciudad.trim()}}, ${{it.departamento}} • NIT: ${{it.nit || 'N/A'}}</span>
                        </div>
                    </td>
                    <td>${{tierPill}}</td>
                    <td><strong style="color: var(--tier-1); font-family: var(--font-mono);">${{it.puntaje_exito}}</strong><span style="color: var(--text-dim); font-size: 0.62rem;">/100</span></td>
                    <td><span class="rating-chip"><i class="fa-solid fa-star"></i> ${{it.reputacion_rating ? it.reputacion_rating.toFixed(1) : '3.8'}}</span></td>
                    <td><strong style="color: var(--tier-2); font-family: var(--font-mono);">${{it.escalabilidad_score || 70}}/100</strong></td>
                    <td>
                        <span style="display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.7rem; white-space: nowrap;">
                            <span class="ratio-dot ${{dotClass}}"></span>
                            <span>${{it.vacantes}} vac · ${{it.postulados}} post</span>
                        </span>
                    </td>
                    <td>
                        <div class="cell-main" style="white-space: nowrap;">
                            <span style="color: var(--brand-primary); font-weight: 600; font-family: var(--font-mono); font-size: 0.7rem;">${{cleanApoyo}}</span>
                            <span style="color: var(--tier-1); font-size: 0.62rem; font-weight: 600;">5A: ${{cleanTecho5A}}</span>
                        </div>
                    </td>
                    <td style="text-align: right;" onclick="event.stopPropagation();">
                        <div class="row-actions">${{actions}}</div>
                    </td>
                `;
                tbody.appendChild(tr);
            }});

            document.getElementById('lblPagination').textContent = `Mostrando ${{start + 1}}-${{Math.min(start + pageSize, total)}} de ${{total}} vacantes`;
            let pages = '';
            for (let i = 1; i <= totalPages; i++) {{
                if (totalPages > 6 && Math.abs(i - currentPage) > 2 && i !== 1 && i !== totalPages) continue;
                pages += `<button class="btn" style="padding: 0.15rem 0.45rem; font-size: 0.68rem; ${{i===currentPage?'background:var(--brand-primary);color:#fff;':''}}" onclick="goToPage(${{i}})">${{i}}</button>`;
            }}
            document.getElementById('paginationPages').innerHTML = pages;
        }}

        function goToPage(p) {{
            currentPage = p;
            renderTable();
        }}

        function renderCards() {{
            const grid = document.getElementById('cardsGridWrap');
            grid.innerHTML = '';
            currentData.forEach(it => {{
                const card = document.createElement('div');
                card.className = 'clean-card';
                card.onclick = () => openModal(it);
                card.innerHTML = `
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.35rem;">
                            <span class="pill-badge pill-tier-1">${{it.cat_badge}}</span>
                            <span class="rating-chip"><i class="fa-solid fa-star"></i> ${{it.reputacion_rating ? it.reputacion_rating.toFixed(1) : '3.8'}}</span>
                        </div>
                        <h3 style="font-size: 0.82rem; font-weight: 700; color: var(--text-main); line-height: 1.3;">${{it.empresa}}</h3>
                        <div style="font-size: 0.66rem; color: var(--text-dim); margin-top: 0.15rem;">${{it.ciudad.trim()}}, ${{it.departamento}}</div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.3rem; background: var(--bg-canvas); padding: 0.35rem; border-radius: var(--radius-xs); text-align: center;">
                        <div><span style="font-size: 0.58rem; color: var(--text-dim);">PUNTOS</span><div style="font-weight: 700; color: var(--tier-1);">${{it.puntaje_exito}}</div></div>
                        <div><span style="font-size: 0.58rem; color: var(--text-dim);">ESCALA</span><div style="font-weight: 700; color: var(--tier-2);">${{it.escalabilidad_score}}</div></div>
                        <div><span style="font-size: 0.58rem; color: var(--text-dim);">VACANTES</span><div style="font-weight: 700; color: var(--brand-primary);">${{it.vacantes}}</div></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.66rem; color: var(--text-muted); border-top: 1px solid var(--border-muted); padding-top: 0.35rem;">
                        <span><strong>Práctica:</strong> ${{it.apoyo_sostenimiento_corto}}</span>
                        <span style="color: var(--tier-1); font-weight: 600;">5A: ${{it.techo_salarial_5anios ? it.techo_salarial_5anios.split('(')[0].trim() : ''}}</span>
                    </div>
                `;
                grid.appendChild(card);
            }});
        }}

        function setLayout(mode) {{
            viewMode = mode;
            if (mode === 'cards') {{
                document.getElementById('tableCardWrap').style.display = 'none';
                document.getElementById('cardsGridWrap').style.display = 'grid';
                document.getElementById('btnLayoutCards').classList.add('active');
                document.getElementById('btnLayoutTable').classList.remove('active');
                renderCards();
            }} else {{
                document.getElementById('tableCardWrap').style.display = 'flex';
                document.getElementById('cardsGridWrap').style.display = 'none';
                document.getElementById('btnLayoutTable').classList.add('active');
                document.getElementById('btnLayoutCards').classList.remove('active');
                renderTable();
            }}
        }}

        function openModalById(solId) {{
            const it = RAW_DATA.find(d => String(d.solicitud_id) === String(solId));
            if (it) openModal(it);
        }}

        function openModal(it) {{
            activeItem = it;
            const setTxt = (id, val) => {{ const el = document.getElementById(id); if (el) el.textContent = val || ''; }};

            setTxt('mTitle', it.empresa);
            setTxt('mSubtitle', `${{it.ciudad.trim()}}, ${{it.departamento}} • NIT: ${{it.nit || 'No registrado'}}`);
            setTxt('mScore', `${{it.puntaje_exito}} / 100`);
            setTxt('mEsc', `${{it.escalabilidad_score || 75}} / 100`);
            setTxt('mRating', `★ ${{it.reputacion_rating ? it.reputacion_rating.toFixed(1) : '3.8'}}`);
            setTxt('mSupport', it.apoyo_sostenimiento_corto || '$1.423.500 COP');

            setTxt('mContactName', it.contacto || 'Equipo de Selección y Gestión Humana');
            setTxt('mContactEmail', it.email || 'No registrado');
            setTxt('mContactPhone', it.telefono || 'No registrado');
            setTxt('mContactModalidad', it.modalidad || 'Presencial / Híbrido');

            setTxt('mCurvaTitulo', it.curva_aprendizaje_titulo || 'Desarrollo de Software');
            setTxt('mCurvaDetalle', it.curva_aprendizaje_detalle || '');
            setTxt('mPerfil', it.perfil_requerido || 'No registrado');
            setTxt('mFunciones', it.funciones || 'No registrado');
            setTxt('mClosingDate', it.fecha_cierre || 'No registrada');

            if (it.finanzas_5anios) {{
                setTxt('mFinAcumulado5A', it.finanzas_5anios.acumulado_5a);
                setTxt('mFinDiferencial', it.finanzas_5anios.diferencial_vs_pyme);
            }}

            // Timeline
            const tl = document.getElementById('mTimelineGrid');
            if (tl && it.hitos_carrera) {{
                let html = '';
                it.hitos_carrera.forEach(h => {{
                    html += `<div style="background: var(--bg-canvas); border: 1px solid var(--border-muted); border-radius: var(--radius-xs); padding: 0.45rem; font-size: 0.68rem;">
                        <span style="color: var(--text-dim); text-transform: uppercase; font-weight: 700; font-size: 0.6rem;">${{h.periodo}}</span>
                        <div style="font-weight: 700; color: var(--text-main); margin: 2px 0;">${{h.rol}}</div>
                        <div style="color: var(--brand-primary); font-family: var(--font-mono); font-weight: 700;">${{h.salario}}</div>
                    </div>`;
                }});
                tl.innerHTML = html;
            }}

            // Interview QA
            const qaList = document.getElementById('mInterviewList');
            if (qaList && it.preguntas_entrevista) {{
                let html = '';
                it.preguntas_entrevista.forEach((q, idx) => {{
                    html += `
                        <div style="background: var(--bg-canvas); border: 1px solid var(--border-muted); border-radius: var(--radius-sm); padding: 0.65rem; font-size: 0.72rem;">
                            <strong style="color: var(--tier-2);">#${{idx + 1}} ${{q.pregunta}}</strong>
                            <div style="color: var(--text-muted); margin: 0.3rem 0; line-height: 1.4;">${{q.respuesta_modelo}}</div>
                            <div style="color: var(--brand-primary); font-size: 0.68rem;"><i class="fa-brands fa-github"></i> ${{q.tip_github}}</div>
                        </div>
                    `;
                }});
                qaList.innerHTML = html;
            }}

            updateModalFavBtn();
            setModalTab('outreach');
            setChannel('email');
            document.getElementById('detailModal').style.display = 'flex';
        }}

        function closeModal() {{
            document.getElementById('detailModal').style.display = 'none';
        }}

        function setModalTab(tab) {{
            document.querySelectorAll('.modal-tab-item').forEach(b => b.classList.remove('active'));
            ['mSecOutreach', 'mSecInterview', 'mSecCareer', 'mSecDetails'].forEach(id => document.getElementById(id).style.display = 'none');

            if (tab === 'outreach') {{
                document.getElementById('mTabOutreach').classList.add('active');
                document.getElementById('mSecOutreach').style.display = 'flex';
            }} else if (tab === 'interview') {{
                document.getElementById('mTabInterview').classList.add('active');
                document.getElementById('mSecInterview').style.display = 'flex';
            }} else if (tab === 'career') {{
                document.getElementById('mTabCareer').classList.add('active');
                document.getElementById('mSecCareer').style.display = 'flex';
            }} else if (tab === 'details') {{
                document.getElementById('mTabDetails').classList.add('active');
                document.getElementById('mSecDetails').style.display = 'flex';
            }}
        }}

        function setChannel(ch) {{
            activeChannel = ch;
            const heading = document.getElementById('mOutreachHeading');
            const body = document.getElementById('mOutreachBody');
            const actions = document.getElementById('mOutreachActions');
            if (!activeItem) return;

            // Update active state on channel buttons
            document.getElementById('mChEmail').className = ch === 'email' ? 'btn btn-primary' : 'btn';
            document.getElementById('mChWA').className = ch === 'wa' ? 'btn btn-whatsapp active' : 'btn';
            document.getElementById('mChLinkedIn').className = ch === 'linkedin' ? 'btn btn-linkedin active' : 'btn';

            if (ch === 'email') {{
                heading.textContent = 'Carta Formal de Postulación Institucional';
                body.textContent = activeItem.correo_formal_completo || '';
                const hasEmail = activeItem.email && activeItem.email.includes('@');
                const mailtoLink = hasEmail ? `mailto:${{activeItem.email}}?subject=${{encodeURIComponent(`Postulación Contrato de Aprendizaje ADSO SENA - ${{CANDIDATE.name}}`)}}&body=${{encodeURIComponent(activeItem.correo_formal_completo || '')}}` : '#';
                actions.innerHTML = `
                    <button class="btn" style="padding: 0.2rem 0.5rem;" onclick="copyText('mOutreachBody')"><i class="fa-regular fa-copy"></i> Copiar Correo</button>
                    ${{hasEmail ? `<a href="${{mailtoLink}}" class="btn btn-primary" style="padding: 0.2rem 0.5rem;"><i class="fa-solid fa-paper-plane"></i> Abrir en Mi Correo</a>` : '<span style="font-size: 0.68rem; color: var(--text-dim);">Sin correo registrado</span>'}}
                `;
            }} else if (ch === 'wa') {{
                heading.textContent = 'Mensaje de WhatsApp Directo';
                body.textContent = activeItem.whatsapp_message || '';
                actions.innerHTML = `
                    <button class="btn" style="padding: 0.2rem 0.5rem;" onclick="copyText('mOutreachBody')"><i class="fa-regular fa-copy"></i> Copiar Mensaje</button>
                    ${{activeItem.is_whatsapp && activeItem.whatsapp_url ? `<a href="${{activeItem.whatsapp_url}}" target="_blank" class="btn btn-whatsapp" style="padding: 0.2rem 0.5rem;"><i class="fa-brands fa-whatsapp"></i> Abrir Chat</a>` : '<span style="font-size: 0.68rem; color: var(--text-dim);">Teléfono fijo (usa correo)</span>'}}
                `;
            }} else if (ch === 'linkedin') {{
                heading.textContent = 'Nota de Conexión en LinkedIn (< 300 Caracteres)';
                body.textContent = activeItem.linkedin_connect_message || '';
                actions.innerHTML = `
                    <button class="btn" style="padding: 0.2rem 0.5rem;" onclick="copyText('mOutreachBody')"><i class="fa-regular fa-copy"></i> Copiar Nota</button>
                    <a href="${{activeItem.linkedin_contact_search_url}}" target="_blank" class="btn btn-linkedin" style="padding: 0.2rem 0.5rem;"><i class="fa-brands fa-linkedin"></i> Buscar Reclutador</a>
                `;
            }}
        }}

        function copyText(elemId) {{
            const el = document.getElementById(elemId);
            if (el) {{
                navigator.clipboard.writeText(el.textContent);
                showToast('Texto copiado al portapapeles');
            }}
        }}

        function showToast(msg) {{
            const t = document.getElementById('toastMsg');
            if (t) {{
                t.textContent = msg;
                t.style.display = 'block';
                setTimeout(() => {{ t.style.display = 'none'; }}, 2000);
            }}
        }}

        function exportData(fmt) {{
            if (fmt === 'xlsx' || fmt === 'csv') {{
                const ws = XLSX.utils.json_to_sheet(currentData);
                const wb = XLSX.utils.book_new();
                XLSX.utils.book_append_sheet(wb, ws, "ADSO_SENA");
                if (fmt === 'xlsx') XLSX.writeFile(wb, "postulaciones_adso_sena.xlsx");
                else XLSX.writeFile(wb, "postulaciones_adso_sena.csv");
            }}
            showToast(`Exportando datos en ${{fmt.toUpperCase()}}...`);
        }}
    </script>
</body>
</html>
"""

output_path = r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\index.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print("Generated polished table layout at: " + output_path)
