/**
 * eShop Compliance Audit — UI Controller
 * 100% Client-Side, Zero Third-Party Requests, Strict CSP (No inline handlers)
 */

(function () {
  'use strict';

  let currentAuditResult = null;
  let currentFilter = 'all';
  let isSampleMode = false;

  const ICONS = {
    pass: '<svg class="icon text-pass" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"></circle><polyline points="9 12 11 14 15 10"></polyline></svg>',
    crit: '<svg class="icon text-crit" viewBox="0 0 24 24" aria-hidden="true"><polygon points="8 2 16 2 22 8 22 16 16 22 8 22 2 16 2 8 8 2"></polygon><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>',
    warn: '<svg class="icon text-warn" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 2 20h20L12 3z"></path><line x1="12" y1="9" x2="12" y2="14"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
  };

  const policyInput = document.getElementById('policyInput');
  const storeNameInput = document.getElementById('storeNameInput');
  const storeTypeSelect = document.getElementById('storeTypeSelect');
  const charCount = document.getElementById('charCount');
  const resultsSection = document.getElementById('resultsSection');
  const sampleDemoBanner = document.getElementById('sampleDemoBanner');
  const criticalWarningBanner = document.getElementById('criticalWarningBanner');
  const scoreValue = document.getElementById('scoreValue');
  const scoreLabel = document.getElementById('scoreLabel');
  const statGrade = document.getElementById('statGrade');
  const statGradeSubtitle = document.getElementById('statGradeSubtitle');
  const statPassed = document.getElementById('statPassed');
  const statCritical = document.getElementById('statCritical');
  const statCriticalLabel = document.getElementById('statCriticalLabel');
  const resultsContainer = document.getElementById('resultsContainer');
  const countAll = document.getElementById('count-all');
  const countFailed = document.getElementById('count-failed');
  const countCritical = document.getElementById('count-critical');
  const countPassed = document.getElementById('count-passed');

  if (policyInput && charCount) {
    policyInput.addEventListener('input', function () {
      isSampleMode = false;
      charCount.textContent = `${this.value.length.toLocaleString('el-GR')} χαρακτήρες`;
    });
  }

  function loadSamplePolicy(type) {
    if (!window.SAMPLE_ESHOP_POLICIES || !window.SAMPLE_ESHOP_POLICIES[type]) return;
    const sample = window.SAMPLE_ESHOP_POLICIES[type];
    if (policyInput) {
      policyInput.value = sample.text;
      policyInput.dispatchEvent(new Event('input'));
    }
    if (storeNameInput) {
      if (type === 'compliant') storeNameInput.value = 'HellasTech Solutions Μ.ΕΠΕ';
      else if (type === 'illegal_refund') storeNameInput.value = 'FashionTrendy Boutique';
      else storeNameInput.value = 'TrendyDropship Greece';
    }
    isSampleMode = true;
    executeAudit();
  }

  function clearInput() {
    if (policyInput) {
      policyInput.value = '';
      policyInput.dispatchEvent(new Event('input'));
    }
    if (storeNameInput) storeNameInput.value = '';
    isSampleMode = false;
    if (resultsSection) {
      resultsSection.hidden = true;
      resultsSection.classList.add('hidden');
    }
    currentAuditResult = null;
  }

  function executeAudit() {
    const text = policyInput ? policyInput.value.trim() : '';
    if (!text) {
      alert('Παρακαλούμε επικολλήστε πρώτα το κείμενο των Όρων Χρήσης ή της Πολιτικής Επιστροφών.');
      return;
    }
    if (!window.eshopComplianceEngine) return;

    const storeType = storeTypeSelect ? storeTypeSelect.value : 'physical';
    const res = window.eshopComplianceEngine.auditPolicy(text, { storeType });
    currentAuditResult = res;

    if (resultsSection) {
      resultsSection.hidden = false;
      resultsSection.classList.remove('hidden');
    }
    if (sampleDemoBanner) {
      sampleDemoBanner.hidden = !isSampleMode;
      sampleDemoBanner.classList.toggle('hidden', !isSampleMode);
    }

    renderMetrics(res);

    const failedTotal = res.results.filter(r => !r.passed).length;
    if (countAll) countAll.textContent = String(res.results.length);
    if (countFailed) countFailed.textContent = String(failedTotal);
    if (countCritical) countCritical.textContent = String(res.criticalViolations);
    if (countPassed) countPassed.textContent = String(res.passedCount);

    renderCards(res.results, currentFilter);
  }

  function renderMetrics(res) {
    if (scoreValue) {
      scoreValue.textContent = String(res.score);
      if (res.score >= 80) {
        scoreValue.className = 'summary-figure text-pass';
        scoreLabel.innerHTML = `${ICONS.pass} <span>Υψηλή Κάλυψη</span>`;
      } else if (res.score >= 60) {
        scoreValue.className = 'summary-figure text-warn';
        scoreLabel.innerHTML = `${ICONS.warn} <span>Μερική Κάλυψη</span>`;
      } else {
        scoreValue.className = 'summary-figure text-crit';
        scoreLabel.innerHTML = `${ICONS.crit} <span>Απαιτεί Διορθώσεις</span>`;
      }
    }

    if (statGrade) {
      const cleanGrade = res.grade.split(' ')[0];
      statGrade.textContent = cleanGrade;
      if (statGradeSubtitle) {
        if (cleanGrade === 'A') statGradeSubtitle.textContent = 'Τεχνικά Συμβατό';
        else if (cleanGrade === 'B') statGradeSubtitle.textContent = 'Μικρές Ελλείψεις';
        else if (cleanGrade === 'C') statGradeSubtitle.textContent = 'Χρήζει Προσαρμογής';
        else statGradeSubtitle.textContent = 'Κίνδυνος Παραβάσεων';
      }
    }

    if (statPassed) {
      statPassed.textContent = `${res.passedCount} / ${res.results.length}`;
    }

    if (statCritical) {
      statCritical.textContent = String(res.criticalViolations);
      if (res.criticalViolations > 0) {
        statCritical.className = 'summary-figure text-crit';
        if (statCriticalLabel) {
          statCriticalLabel.textContent = 'Άμεση Προσοχή';
          statCriticalLabel.className = 'summary-sub text-crit';
        }
        if (criticalWarningBanner) {
          criticalWarningBanner.hidden = false;
          criticalWarningBanner.classList.remove('hidden');
        }
      } else {
        statCritical.className = 'summary-figure text-pass';
        if (statCriticalLabel) {
          statCriticalLabel.textContent = 'Μηδενικές κρίσιμες ενδείξεις';
          statCriticalLabel.className = 'summary-sub text-pass';
        }
        if (criticalWarningBanner) {
          criticalWarningBanner.hidden = true;
          criticalWarningBanner.classList.add('hidden');
        }
      }
    }

    const achRefute = document.getElementById('achRefuteSummary');
    if (achRefute) {
      const warnFails = Math.max(0, res.failedCount - res.criticalViolations);
      achRefute.textContent = res.failedCount === 0
        ? `Επιβεβαιώθηκαν 0 διαψεύσεις (ACH) στα 14 κριτήρια του υποβληθέντος κειμένου (${res.score}/100). Ο δείκτης δεν υποκαθιστά τον έλεγχο ζωντανού checkout δεξιά.`
        : `Εντοπίστηκαν ${res.criticalViolations} κρίσιμες διαψεύσεις και ${warnFails} ελλείψεις στα 14 σημεία του επικολλημένου κειμένου (Δείκτης ${res.score}/100). Αποκαταστήστε τις κρίσιμες ρήτρες πριν ελέγξετε το ζωντανό checkout.`;
    }
  }

  function renderCards(results, filter) {
    if (!resultsContainer) return;
    resultsContainer.innerHTML = '';

    const filtered = results.filter(r => {
      if (filter === 'all') return true;
      if (filter === 'passed') return r.passed;
      if (filter === 'failed') return !r.passed;
      if (filter === 'critical') return !r.passed && r.severity === 'CRITICAL';
      return true;
    });

    if (filtered.length === 0) {
      resultsContainer.innerHTML = `<div class="panel"><p class="brand-sub">Δεν υπάρχουν ευρήματα για το επιλεγμένο φίλτρο.</p></div>`;
      return;
    }

    filtered.forEach(r => {
      const card = document.createElement('article');
      card.className = `audit-item-card ${r.passed ? 'passed' : (r.severity === 'CRITICAL' ? 'failed-critical' : 'failed-warning')}`;
      card.dataset.id = r.id;

      let statusIcon = ICONS.pass;
      let statusTag = '<span class="status-tag pass">ΣΥΜΒΑΤΟ</span>';
      if (!r.passed) {
        if (r.severity === 'CRITICAL') {
          statusIcon = ICONS.crit;
          statusTag = '<span class="status-tag crit">ΚΡΙΣΙΜΟ</span>';
        } else {
          statusIcon = ICONS.warn;
          statusTag = '<span class="status-tag warn">ΠΡΟΣΟΧΗ</span>';
        }
      }

      let html = `
        <div class="finding-top">
          <div class="finding-heading-wrap">
            ${statusIcon}
            <h3 class="finding-title">${escapeHtml(r.title)}</h3>
          </div>
          <div class="finding-meta">
            <span class="rule-code">${escapeHtml(r.ruleId || r.id)}</span>
            <span class="registry-status-tag">${escapeHtml(r.reviewStatus || 'Base Statute')}</span>
            ${statusTag}
          </div>
        </div>
        <div class="finding-law">
          <span><strong>Νομική Βάση:</strong> ${escapeHtml(r.lawRef)}</span>
          <span><strong>Ισχύς:</strong> ${escapeHtml(r.effectiveFrom || '')}</span>
          <span><strong>Τομέας:</strong> ${escapeHtml(r.category)}</span>
        </div>
      `;

      if (r.passed) {
        html += `
          <div class="finding-detail pass">
            ${ICONS.pass}
            <span>Καλύπτεται τυπικά από το υποβληθέν κείμενο.</span>
          </div>
        `;
      } else {
        html += `
          <div class="finding-detail issue"><strong>Εντοπισμένο Πρόβλημα:</strong> ${escapeHtml(r.issue)}</div>
          <div class="finding-detail risk"><strong>Κανονιστικός Κίνδυνος:</strong> ${escapeHtml(r.penaltyRisk)}</div>
          <p class="finding-rec"><strong>Σύσταση Προσαρμογής:</strong> ${escapeHtml(r.recommendation)}</p>
          <div>
            <div class="clause-header">
              <span>Ενδεικτική Ρήτρα προς Προσαρμογή (βάσει κειμένου Ν. 2251/1994 · 5317/2026):</span>
              <button type="button" class="btn btn-secondary btn-sm" data-copy-clause="${escapeHtml(r.id)}" id="copy-btn-${escapeHtml(r.id)}">Αντιγραφή</button>
            </div>
            <div class="clause-box">${escapeHtml(r.correctedClause)}</div>
          </div>
        `;
      }

      card.innerHTML = html;
      resultsContainer.appendChild(card);
    });
  }

  function filterResults(type) {
    currentFilter = type;
    ['all', 'failed', 'critical', 'passed'].forEach(t => {
      const el = document.getElementById(`filter-${t}`);
      if (el) el.classList.toggle('active', t === type);
    });
    if (currentAuditResult) renderCards(currentAuditResult.results, currentFilter);
  }

  function copyTextToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).catch(() => fallbackCopyText(text));
    }
    return fallbackCopyText(text);
  }

  function fallbackCopyText(text) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.left = '-999999px';
    document.body.appendChild(ta);
    ta.select();
    return new Promise((resolve, reject) => {
      try {
        const ok = document.execCommand('copy');
        document.body.removeChild(ta);
        ok ? resolve() : reject(new Error('copy failed'));
      } catch (e) {
        document.body.removeChild(ta);
        reject(e);
      }
    });
  }

  function copyClause(id) {
    if (!currentAuditResult) return;
    const item = currentAuditResult.results.find(r => r.id === id);
    if (!item || !item.correctedClause) return;
    copyTextToClipboard(item.correctedClause).catch(() => {}).finally(() => {
      const btn = document.getElementById(`copy-btn-${id}`);
      if (btn) {
        const prev = btn.textContent;
        btn.textContent = 'Αντιγράφηκε';
        setTimeout(() => { btn.textContent = prev; }, 2000);
      }
    });
  }

  function copyAllClauses() {
    if (!currentAuditResult) return;
    const failed = currentAuditResult.results.filter(r => !r.passed);
    if (failed.length === 0) {
      alert('Όλοι οι έλεγχοι είναι συμβατοί.');
      return;
    }
    const fullText = failed.map(r => `[${r.ruleId}] ${r.title} (${r.lawRef})\n${r.correctedClause}\n`).join('\n---\n\n');
    copyTextToClipboard(fullText).then(() => {
      alert(`Αντιγράφηκαν ${failed.length} ενδεικτικές ρήτρες στο πρόχειρο.`);
    }).catch(() => {});
  }

  function exportMarkdown() {
    if (!currentAuditResult || !window.eshopComplianceEngine) {
      alert('Εκτελέστε πρώτα τον έλεγχο συμμόρφωσης.');
      return;
    }
    const store = storeNameInput ? (storeNameInput.value.trim() || 'Ηλεκτρονικό Κατάστημα') : 'Ηλεκτρονικό Κατάστημα';
    const md = window.eshopComplianceEngine.generateMarkdownReport(currentAuditResult, store);
    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ekthesi-symmorfosis-${slugify(store)}-2026.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function escapeHtml(str) {
    return (str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function slugify(text) {
    return text.toString().toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^\w\-]+/g, '')
      .replace(/\-\-+/g, '-')
      .replace(/^-+/, '')
      .replace(/-+$/, '') || 'eshop';
  }

  // Event Listeners (Strict CSP: Zero Inline Handlers)
  document.querySelectorAll('[data-sample]').forEach(btn => {
    btn.addEventListener('click', () => loadSamplePolicy(btn.dataset.sample));
  });

  document.querySelectorAll('.filter-tab[data-filter]').forEach(tab => {
    tab.addEventListener('click', () => filterResults(tab.dataset.filter));
  });

  const runBtn = document.getElementById('runAuditBtn');
  if (runBtn) runBtn.addEventListener('click', executeAudit);

  if (storeTypeSelect) {
    storeTypeSelect.addEventListener('change', () => {
      if (policyInput && policyInput.value.trim()) executeAudit();
    });
  }

  const clearBtn = document.getElementById('clearInputBtn');
  if (clearBtn) clearBtn.addEventListener('click', clearInput);

  const jumpCritBtn = document.getElementById('jumpCriticalBtn');
  if (jumpCritBtn) jumpCritBtn.addEventListener('click', () => filterResults('critical'));

  const dlBtn = document.getElementById('downloadMdBtn');
  if (dlBtn) dlBtn.addEventListener('click', exportMarkdown);

  const prtBtn = document.getElementById('printReportBtn');
  if (prtBtn) prtBtn.addEventListener('click', () => {
    if (!currentAuditResult) {
      alert('Εκτελέστε πρώτα τον έλεγχο συμμόρφωσης.');
      return;
    }
    window.print();
  });

  const cpAllBtn = document.getElementById('copyAllBtn');
  if (cpAllBtn) cpAllBtn.addEventListener('click', copyAllClauses);

  if (resultsContainer) {
    resultsContainer.addEventListener('click', e => {
      const btn = e.target.closest('[data-copy-clause]');
      if (btn) copyClause(btn.dataset.copyClause);
    });
  }

  // Validation Mode Waitlist Form Handler
  const waitlistForm = document.getElementById('proWaitlistForm');
  if (waitlistForm) {
    waitlistForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const emailEl = document.getElementById('proWaitlistEmail');
      const consentEl = document.getElementById('proWaitlistConsent');
      const msgEl = document.getElementById('proWaitlistMsg');
      const emailVal = emailEl ? emailEl.value.trim() : '';

      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailVal)) {
        if (msgEl) {
          msgEl.className = 'waitlist-msg text-crit';
          msgEl.textContent = 'Παρακαλούμε εισάγετε μια έγκυρη διεύθυνση email.';
        }
        return;
      }
      if (!consentEl || !consentEl.checked) {
        if (msgEl) {
          msgEl.className = 'waitlist-msg text-crit';
          msgEl.textContent = 'Απαιτείται η ρητή συγκατάθεσή σας (επιλέξτε το πλαίσιο) πριν την εγγραφή.';
        }
        return;
      }
      const endpoint = (waitlistForm.dataset.endpoint || '').trim();
      const project = (waitlistForm.dataset.project || 'eshop-compliance-doctor').trim();
      if (!endpoint) return;
      if (msgEl) {
        msgEl.className = 'waitlist-msg';
        msgEl.textContent = 'Αποστολή...';
      }
      try {
        const adviceEl = document.getElementById('proWaitlistAdvice');
        const adviceVal = adviceEl ? adviceEl.value : '';
        const consentText = consentEl.parentElement ? consentEl.parentElement.innerText.trim().slice(0, 300) : '';
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
          body: JSON.stringify({
            email: emailVal,
            project,
            advice_focus: adviceVal,
            consent: true,
            consent_text: consentText,
            consent_ts: new Date().toISOString()
          })
        });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        if (msgEl) {
          msgEl.className = 'waitlist-msg text-pass';
          msgEl.textContent = 'Ευχαριστούμε. Καταχωρηθήκατε επιτυχώς στη λίστα αναμονής.';
        }
        emailEl.value = '';
        consentEl.checked = false;
      } catch (err) {
        if (msgEl) {
          msgEl.className = 'waitlist-msg text-crit';
          msgEl.textContent = 'Σφάλμα αποστολής. Δοκιμάστε ξανά αργότερα.';
        }
      }
    });
  }

  window.downloadMarkdown = exportMarkdown;
  window.copyAllCorrectedClauses = copyAllClauses;
})();
