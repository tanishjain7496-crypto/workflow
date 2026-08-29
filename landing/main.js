/* ═══════════════════════════════════════════════════════════════════
   Dev Mode Workflow — App Launcher JS
   Handles: Pre-rendered cards, dynamic config, icon extraction, PyWebView API
═══════════════════════════════════════════════════════════════════ */

'use strict';

let currentItems = [];
let activeFilter = 'all';

// Default Fallback Icons
const DEFAULT_ICONS = {
  gemini: 'fa-solid fa-sparkles',
  chatgpt: 'fa-solid fa-robot',
  claude: 'fa-solid fa-brain',
  perplexity: 'fa-solid fa-magnifying-glass',
  youtube: 'fa-brands fa-youtube',
  antigravity_ide: 'fa-solid fa-code',
  habit_tracker: 'fa-solid fa-chart-line'
};

// ──────────────────────────────────────────────────────────────────
// 1. LAUNCH ENGINE & LOG DISPLAY
// ──────────────────────────────────────────────────────────────────
const LauncherEngine = (function () {

  function log(message) {
    console.log("[Launcher]", message);
    const logText = document.getElementById('log-text');
    if (logText) logText.textContent = message;

    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `<i class="fa-solid fa-bolt" style="color: #64ffda; margin-right: 8px;"></i> ${message}`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  function launchAll() {
    log("🚀 Executing LAUNCH ALL sequence...");
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.launch_all()
        .then(() => log("✓ All workflow items launched successfully!"))
        .catch(err => log("⚠️ Launching via Python backend..."));
    } else {
      log("Opening Brave AI tabs in browser...");
      const urls = [
        "https://gemini.google.com/app?hl=en-IN",
        "https://chatgpt.com",
        "https://claude.com",
        "https://www.perplexity.ai/"
      ];
      urls.forEach(url => window.open(url, '_blank'));
      log("✓ Opened all 4 Brave AI tabs!");
    }
  }

  function launchUrl(url, name) {
    log(`Launching ${name || url}...`);
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.launch_url(url)
        .then(() => log(`✓ Opened ${name || 'URL'} in Brave!`))
        .catch(() => window.open(url, '_blank'));
    } else {
      window.open(url, '_blank');
      log(`✓ Opened ${name || 'URL'}!`);
    }
  }

  function launchApp(path, name) {
    log(`Launching ${name || 'App'}...`);
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.launch_app(path)
        .then(() => log(`✓ ${name} launched!`))
        .catch(() => log(`❌ Could not launch ${name}`));
    } else {
      log(`⚠️ Executable launcher requires native desktop app.`);
    }
  }

  return { log, launchAll, launchUrl, launchApp };
})();

// ──────────────────────────────────────────────────────────────────
// 2. CONFIG LOADER & GRID RENDERING
// ──────────────────────────────────────────────────────────────────
function loadWorkflowConfig() {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.get_config()
      .then(config => {
        if (config && config.items) {
          currentItems = config.items;
          renderGrid();
          LauncherEngine.log("✓ Loaded workflow configuration from /data/config.json");
        }
      })
      .catch(err => console.error("Config fetch error:", err));
  }
}

function renderGrid() {
  const grid = document.getElementById('workflow-grid');
  if (!grid || currentItems.length === 0) return;

  grid.innerHTML = '';

  const filtered = currentItems.filter(item => {
    if (activeFilter === 'all') return true;
    return item.type === activeFilter;
  });

  // Update counters
  const totalAll = currentItems.length;
  const totalUrls = currentItems.filter(i => i.type === 'urls').length;
  const totalApps = currentItems.filter(i => i.type === 'apps').length;

  document.querySelectorAll('#count-all, .count-all-m').forEach(el => el.textContent = totalAll);
  document.querySelectorAll('#count-urls, .count-urls-m').forEach(el => el.textContent = totalUrls);
  document.querySelectorAll('#count-apps, .count-apps-m').forEach(el => el.textContent = totalApps);

  filtered.forEach(item => {
    const card = document.createElement('div');
    card.className = 'workflow-card';
    card.dataset.id = item.id;
    card.dataset.type = item.type;
    if (item.url) card.dataset.url = item.url;
    if (item.path) card.dataset.path = item.path;

    // Render Icon
    let iconHtml = '';
    if (item.icon_src) {
      iconHtml = `<img src="${item.icon_src}" class="card-icon-img" alt="${item.name}" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';" /><i class="${DEFAULT_ICONS[item.id] || 'fa-solid fa-cube'}" style="display:none; color:#6c5ce7;"></i>`;
    } else {
      iconHtml = `<i class="${DEFAULT_ICONS[item.id] || (item.type === 'urls' ? 'fa-solid fa-globe' : 'fa-solid fa-cube')}" style="color:${item.type === 'urls' ? '#4285f4' : '#6c5ce7'};"></i>`;
    }

    const tagClass = item.type === 'apps' ? 'card-tag app' : 'card-tag';
    const tagText = item.tag || (item.type === 'urls' ? 'Brave Tab' : 'Desktop App');

    card.innerHTML = `
      <div class="card-icon">${iconHtml}</div>
      <div class="card-info">
        <div class="card-title">${item.name}</div>
        <div class="card-sub">${item.sub || item.url || item.path || ''}</div>
      </div>
      <div class="${tagClass}">${tagText}</div>
      <div class="card-actions">
        <button class="card-launch-btn" title="Launch ${item.name}">
          <i class="fa-solid ${item.type === 'urls' ? 'fa-arrow-up-right-from-square' : 'fa-play'}"></i>
        </button>
        <button class="card-delete-btn" title="Delete ${item.name}">
          <i class="fa-solid fa-trash"></i>
        </button>
      </div>
    `;

    // Bind Launch
    card.querySelector('.card-launch-btn').addEventListener('click', (e) => {
      e.stopPropagation();
      if (item.type === 'urls') LauncherEngine.launchUrl(item.url, item.name);
      else LauncherEngine.launchApp(item.path, item.name);
    });

    // Bind Delete
    card.querySelector('.card-delete-btn').addEventListener('click', (e) => {
      e.stopPropagation();
      deleteItem(item.id, item.name);
    });

    // Card click
    card.addEventListener('click', (e) => {
      if (e.target.closest('.card-actions')) return;
      if (item.type === 'urls') LauncherEngine.launchUrl(item.url, item.name);
      else LauncherEngine.launchApp(item.path, item.name);
    });

    grid.appendChild(card);
  });
}

function deleteItem(itemId, name) {
  if (confirm(`Delete "${name}" from workflow?`)) {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.delete_item(itemId)
        .then(() => {
          LauncherEngine.log(`✓ Deleted ${name}`);
          loadWorkflowConfig();
        });
    } else {
      currentItems = currentItems.filter(i => i.id !== itemId);
      renderGrid();
    }
  }
}

// ──────────────────────────────────────────────────────────────────
// 3. INITIALIZATION & EVENT LISTENERS
// ──────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

  // Bind Pre-rendered Card Click Listeners
  document.querySelectorAll('.workflow-card').forEach(card => {
    const launchBtn = card.querySelector('.card-launch-btn');
    const deleteBtn = card.querySelector('.card-delete-btn');
    const type = card.dataset.type;
    const url = card.dataset.url;
    const path = card.dataset.path;
    const name = card.querySelector('.card-title')?.textContent;

    if (launchBtn) {
      launchBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (type === 'urls') LauncherEngine.launchUrl(url, name);
        else LauncherEngine.launchApp(path, name);
      });
    }

    if (deleteBtn) {
      deleteBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        card.remove();
        LauncherEngine.log(`Removed ${name}`);
      });
    }

    card.addEventListener('click', (e) => {
      if (e.target.closest('.card-actions')) return;
      if (type === 'urls') LauncherEngine.launchUrl(url, name);
      else LauncherEngine.launchApp(path, name);
    });
  });

  // Bind Main Launch Buttons
  document.getElementById('main-launch-btn')?.addEventListener('click', () => LauncherEngine.launchAll());
  document.getElementById('launch-all-header-btn')?.addEventListener('click', () => LauncherEngine.launchAll());

  // Bind Filter Tabs
  document.querySelectorAll('[data-filter]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-filter]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFilter = btn.dataset.filter;

      const cards = document.querySelectorAll('.workflow-card');
      cards.forEach(c => {
        if (activeFilter === 'all' || c.dataset.type === activeFilter) {
          c.style.display = 'flex';
        } else {
          c.style.display = 'none';
        }
      });
    });
  });

  // Modal Handlers
  const webModal = document.getElementById('add-website-modal');
  const appModal = document.getElementById('add-app-modal');

  const openWeb = () => webModal.style.display = 'flex';
  const closeWeb = () => webModal.style.display = 'none';
  const openApp = () => appModal.style.display = 'flex';
  const closeApp = () => appModal.style.display = 'none';

  document.getElementById('open-add-website-btn')?.addEventListener('click', openWeb);
  document.getElementById('close-web-modal')?.addEventListener('click', closeWeb);
  document.getElementById('cancel-web-modal')?.addEventListener('click', closeWeb);

  document.getElementById('open-add-app-btn')?.addEventListener('click', openApp);
  document.getElementById('close-app-modal')?.addEventListener('click', closeApp);
  document.getElementById('cancel-app-modal')?.addEventListener('click', closeApp);

  // Submit Website
  document.getElementById('submit-add-website')?.addEventListener('click', () => {
    const name = document.getElementById('web-name-input').value.trim();
    let url = document.getElementById('web-url-input').value.trim();

    if (!url) {
      alert("Please enter a valid website URL.");
      return;
    }

    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      url = "https://" + url;
    }

    LauncherEngine.log(`Adding ${name || url} and fetching favicon...`);
    closeWeb();

    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.add_website(name, url)
        .then(() => {
          document.getElementById('web-name-input').value = '';
          document.getElementById('web-url-input').value = '';
          LauncherEngine.log(`✓ Added ${name || url} with extracted icon!`);
          loadWorkflowConfig();
        });
    } else {
      LauncherEngine.log(`✓ Added website!`);
    }
  });

  // Submit App
  document.getElementById('submit-add-app')?.addEventListener('click', () => {
    const name = document.getElementById('app-name-input').value.trim();
    const path = document.getElementById('app-path-input').value.trim();

    if (!path) {
      alert("Please enter or browse a valid executable path.");
      return;
    }

    LauncherEngine.log(`Adding ${name || 'App'} and extracting Windows icon...`);
    closeApp();

    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.add_app(name, path)
        .then(() => {
          document.getElementById('app-name-input').value = '';
          document.getElementById('app-path-input').value = '';
          LauncherEngine.log(`✓ Added ${name || 'App'} with native icon!`);
          loadWorkflowConfig();
        });
    } else {
      LauncherEngine.log(`✓ Added app!`);
    }
  });

  // Browse Native File Dialog
  document.getElementById('browse-app-path-btn')?.addEventListener('click', () => {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.pick_app_file()
        .then(filePath => {
          if (filePath) {
            document.getElementById('app-path-input').value = filePath;
            if (!document.getElementById('app-name-input').value) {
              const fileName = filePath.split('\\').pop().split('/').pop().replace(/\.(exe|lnk|bat|cmd)$/i, '');
              document.getElementById('app-name-input').value = fileName;
            }
          }
        });
    }
  });

  // PyWebView Ready Check
  window.addEventListener('pywebviewready', loadWorkflowConfig);
  setTimeout(loadWorkflowConfig, 600);
});
