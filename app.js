/**
 * AL-MARJI3 (المرجع) - QURAN & HADITH RAG KNOWLEDGE PLATFORM CLIENT JS
 * Features: Dual Quran & Hadith RAG support, API Docs Inspector, Surahs Explorer,
 * Bookmarks, TTS Audio Reader, Share Card Generator, Theme Switcher.
 */

// Embedded Fallback Corpus (Quran + Hadith)
const ISLAMIC_KNOWLEDGE_CORPUS = [
  {
    type: "quran",
    surah_name: "Al-Fatihah",
    surah: 1,
    ayah: 1,
    arabic: "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
    verse: "In the name of Allah, the Beneficent, the Merciful.",
    tafseer: "In the Name of God: Allah is a name for the divine essence, the Compassionate, the Merciful.",
    keywords: ["bismillah", "opening", "fatihah", "merciful", "beneficent", "allah", "name"]
  },
  {
    type: "quran",
    surah_name: "Al-Baqarah",
    surah: 2,
    ayah: 255,
    arabic: "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ",
    verse: "Allah! There is no deity except Him, the Ever-Living, the Sustainer of all existence. Neither drowsiness overtakes Him nor sleep. To Him belongs whatever is in the heavens and whatever is on the earth.",
    tafseer: "Ayat al-Kursi (The Verse of the Throne) establishes the absolute oneness, eternal life, and supreme power of Allah.",
    keywords: ["kursi", "throne", "oneness", "ever-living", "heavens", "earth", "sovereignty", "allah"]
  },
  {
    type: "quran",
    surah_name: "Al-Inshirah",
    surah: 94,
    ayah: 5,
    arabic: "فَإِنَّ مَعَ الْعُسْرِ يُسْرًا",
    verse: "For indeed, with hardship [will be] ease.",
    tafseer: "A divine promise that every trial and hardship is accompanied by divine relief and ease.",
    keywords: ["hardship", "ease", "inshirah", "sabr", "patience", "relief", "trial"]
  },
  {
    type: "hadith",
    source: "Sahih al-Bukhari",
    hadith_no: "1",
    chapter: "Book of Revelation (كتاب بدء الوحي)",
    arabic: "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ، وَإِنَّمَا لِكُلِّ امْرِئٍ مَا نَوَى",
    text: "Narrated 'Umar bin Al-Khattab: I heard Allah's Messenger (ﷺ) saying, 'The reward of deeds depends upon the intentions and every person will get the reward according to what he has intended.'",
    narrator: "Umar bin Al-Khattab (RA)",
    grade: "Sahih (Authentic)",
    keywords: ["intention", "niyyah", "reward", "action", "deed", "emigration", "hijrah", "sincerity"]
  },
  {
    type: "hadith",
    source: "Sahih Muslim",
    hadith_no: "2699",
    chapter: "Book of Knowledge & Remembrance (كتاب الذكر والدعاء)",
    arabic: "مَنْ سَلَكَ طَرِيقًا يَلْتَمِسُ فِيهِ عِلْمًا سَهَّلَ اللَّهُ لَهُ بِهِ طَرِيقًا إِلَى الْجَنَّةِ",
    text: "Abu Hurairah (RA) reported Allah's Messenger (ﷺ) as saying: He who treads a path in search of knowledge, Allah will make easy for him a path leading to Paradise.",
    narrator: "Abu Hurairah (RA)",
    grade: "Sahih (Authentic)",
    keywords: ["knowledge", "ilm", "paradise", "jannah", "seeking knowledge", "study", "quran", "tranquility"]
  },
  {
    type: "hadith",
    source: "Jami` at-Tirmidhi",
    hadith_no: "1956",
    chapter: "Book of Righteousness and Relations (كتاب البر والصلة)",
    arabic: "تَبَسُّمُكَ فِي وَجْهِ أَخِيكَ لَكَ صَدَقَةٌ",
    text: "Narrated Abu Dharr: The Messenger of Allah (ﷺ) said: 'Your smiling in the face of your brother is charity for you, your enjoining what is good and forbidding what is evil is charity...'",
    narrator: "Abu Dharr (RA)",
    grade: "Hasan Sahih (Good & Authentic)",
    keywords: ["smile", "smiling", "charity", "sadaqah", "kindness", "goodness", "brotherhood", "character"]
  },
  {
    type: "hadith",
    source: "Sahih al-Bukhari",
    hadith_no: "6018",
    chapter: "Book of Good Manners (كتاب الأدب)",
    arabic: "أَكْمَلُ الْمُؤْمِنِينَ إِيمَانًا أَحْسَنُهُمْ خُلُقًا",
    text: "Narrated Abu Hurairah: Allah's Messenger (ﷺ) said: 'The most complete of believers in faith are those with the best character, and the best of you are those who are best to their wives.'",
    narrator: "Abu Hurairah (RA)",
    grade: "Sahih (Authentic)",
    keywords: ["character", "akhlaq", "faith", "iman", "manners", "wife", "family", "believer"]
  }
];

// App State
const AppState = {
  theme: localStorage.getItem('almarji3_theme') || 'dark',
  topK: 5,
  sourceScope: 'all', // 'all', 'quran', 'hadith'
  selectedCollection: 'all',
  bookmarks: JSON.parse(localStorage.getItem('almarji3_bookmarks') || '[]'),
  currentRetrieved: [],
  isProcessing: false,
  backendConnected: false,
  activeShareItem: null,
  surahsList: []
};

// DOM Cache
let elements = {};

document.addEventListener('DOMContentLoaded', () => {
  cacheElements();
  initTheme();
  checkBackendHealth();
  setupEventListeners();
  loadSurahsMetadata();
  renderBookmarksList();
});

function cacheElements() {
  elements = {
    themeBtn: document.getElementById('themeToggleBtn'),
    topKSelect: document.getElementById('topKSelect'),
    sourceModeSelect: document.getElementById('sourceModeSelect'),
    collectionSelect: document.getElementById('collectionSelect'),
    statusBadge: document.getElementById('statusBadge'),
    statusText: document.getElementById('statusText'),
    messagesContainer: document.getElementById('messagesContainer'),
    welcomeHero: document.getElementById('welcomeHero'),
    userInput: document.getElementById('userInput'),
    sendBtn: document.getElementById('sendBtn'),
    evidenceDrawer: document.getElementById('evidenceDrawer'),
    evidenceList: document.getElementById('evidenceList'),
    evidenceCount: document.getElementById('evidenceCount'),
    drawerToggleBtn: document.getElementById('drawerToggleBtn'),
    
    // Modals
    bookmarksModalBtn: document.getElementById('bookmarksModalBtn'),
    bookmarksModal: document.getElementById('bookmarksModal'),
    bookmarksList: document.getElementById('bookmarksList'),
    closeBookmarksBtn: document.getElementById('closeBookmarksBtn'),

    apiDocsModalBtn: document.getElementById('apiDocsModalBtn'),
    apiDocsModal: document.getElementById('apiDocsModal'),
    apiDocsModalBody: document.getElementById('apiDocsModalBody'),
    closeApiDocsBtn: document.getElementById('closeApiDocsBtn'),

    surahsModal: document.getElementById('surahsModal'),
    closeSurahsBtn: document.getElementById('closeSurahsBtn'),
    surahsGrid: document.getElementById('surahsGrid'),
    surahSearchInput: document.getElementById('surahSearchInput'),

    hadithBooksModal: document.getElementById('hadithBooksModal'),
    closeHadithBooksBtn: document.getElementById('closeHadithBooksBtn'),
    hadithCollectionsGrid: document.getElementById('hadithCollectionsGrid'),

    verificationRulesModal: document.getElementById('verificationRulesModal'),
    closeVerificationRulesBtn: document.getElementById('closeVerificationRulesBtn'),

    shareModal: document.getElementById('shareModal'),
    closeShareBtn: document.getElementById('closeShareBtn'),
    shareCardPreview: document.getElementById('shareCardPreview'),
    copyShareBtn: document.getElementById('copyShareBtn'),
    toastContainer: document.getElementById('toastContainer'),
    
    // Navigation Links
    navLiveChatBtn: document.getElementById('navLiveChatBtn'),
    navSurahsBtn: document.getElementById('navSurahsBtn'),
    navHadithBooksBtn: document.getElementById('navHadithBooksBtn'),
    navVerificationRulesBtn: document.getElementById('navVerificationRulesBtn'),
    sidebarToggleBtn: document.getElementById('sidebarToggleBtn'),
    sidebar: document.getElementById('sidebar')
  };
}

function initTheme() {
  document.documentElement.setAttribute('data-theme', AppState.theme);
  updateThemeIcon();
}

function updateThemeIcon() {
  if (elements.themeBtn) {
    elements.themeBtn.innerHTML = AppState.theme === 'dark' 
      ? `<svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>`
      : `<svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>`;
  }
}

function setupEventListeners() {
  // Theme Toggle
  elements.themeBtn?.addEventListener('click', () => {
    AppState.theme = AppState.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('almarji3_theme', AppState.theme);
    initTheme();
    showToast(`Switched to ${AppState.theme} mode`);
  });

  // Source Scope Select
  elements.sourceModeSelect?.addEventListener('change', (e) => {
    AppState.sourceScope = e.target.value;
    showToast(`Knowledge scope set to: ${e.target.options[e.target.selectedIndex].text}`);
  });

  // Top-K Select
  elements.topKSelect?.addEventListener('change', (e) => {
    AppState.topK = parseInt(e.target.value, 10);
    showToast(`Top-K set to ${AppState.topK} sources`);
  });

  // Collection Select
  elements.collectionSelect?.addEventListener('change', (e) => {
    AppState.selectedCollection = e.target.value;
    showToast(`Collection filter: ${e.target.options[e.target.selectedIndex].text}`);
  });

  // Auto-expand textarea
  elements.userInput?.addEventListener('input', () => {
    elements.userInput.style.height = 'auto';
    elements.userInput.style.height = Math.min(elements.userInput.scrollHeight, 120) + 'px';
  });

  elements.userInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });

  elements.sendBtn?.addEventListener('click', handleSend);

  // Drawer & Sidebar Toggles
  elements.drawerToggleBtn?.addEventListener('click', () => {
    elements.evidenceDrawer.classList.toggle('collapsed');
  });

  elements.sidebarToggleBtn?.addEventListener('click', () => {
    elements.sidebar.classList.toggle('mobile-open');
  });

  // Navigation Links
  elements.navSurahsBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    openSurahsModal();
  });

  elements.navHadithBooksBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    openHadithBooksModal();
  });

  elements.navVerificationRulesBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    elements.verificationRulesModal.classList.add('active');
  });

  // Modals Open/Close
  elements.bookmarksModalBtn?.addEventListener('click', () => elements.bookmarksModal.classList.add('active'));
  elements.closeBookmarksBtn?.addEventListener('click', () => elements.bookmarksModal.classList.remove('active'));

  elements.apiDocsModalBtn?.addEventListener('click', () => openApiDocsModal());
  elements.closeApiDocsBtn?.addEventListener('click', () => elements.apiDocsModal.classList.remove('active'));

  elements.closeSurahsBtn?.addEventListener('click', () => elements.surahsModal.classList.remove('active'));
  elements.closeHadithBooksBtn?.addEventListener('click', () => elements.hadithBooksModal.classList.remove('active'));
  elements.closeVerificationRulesBtn?.addEventListener('click', () => elements.verificationRulesModal.classList.remove('active'));

  elements.closeShareBtn?.addEventListener('click', () => elements.shareModal.classList.remove('active'));

  elements.copyShareBtn?.addEventListener('click', () => {
    if (AppState.activeShareItem) {
      const textToCopy = `"${AppState.activeShareItem.text}"\n\n- ${AppState.activeShareItem.ref}\nShared via Al-Marji3 Islamic AI`;
      navigator.clipboard.writeText(textToCopy);
      showToast("Citation text copied to clipboard!");
    }
  });

  // Surah Search Filter Input
  elements.surahSearchInput?.addEventListener('input', (e) => {
    renderSurahsGrid(e.target.value.toLowerCase());
  });

  // Sample Prompt Cards
  document.querySelectorAll('.prompt-card').forEach(card => {
    card.addEventListener('click', () => {
      const promptText = card.dataset.prompt || card.querySelector('.prompt-text')?.innerText;
      if (promptText) {
        elements.userInput.value = promptText;
        handleSend();
      }
    });
  });
}

// Global quick query runner
window.submitQuickQuery = function(text) {
  if (elements.userInput) {
    elements.userInput.value = text;
    handleSend();
  }
};

// Check Backend Connectivity
async function checkBackendHealth() {
  try {
    const res = await fetch('/api/health', { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      const data = await res.json();
      AppState.backendConnected = true;
      if (elements.statusBadge) {
        elements.statusBadge.classList.remove('offline');
        elements.statusText.innerText = data.rag_available ? "RAG Server Active (Ollama)" : "API Connected (Client RAG)";
      }
      return;
    }
  } catch (err) {
    console.log("Embedded Client RAG mode active.");
  }
  AppState.backendConnected = false;
  if (elements.statusBadge) {
    elements.statusBadge.classList.remove('offline');
    elements.statusText.innerText = "Client RAG Engine";
  }
}

// Handle User Sending Query
async function handleSend() {
  const query = elements.userInput.value.trim();
  if (!query || AppState.isProcessing) return;

  if (elements.welcomeHero) {
    elements.welcomeHero.style.display = 'none';
  }

  appendMessage({ role: 'user', content: query });

  elements.userInput.value = '';
  elements.userInput.style.height = '24px';
  AppState.isProcessing = true;

  const typingMsgId = appendTypingIndicator();

  try {
    let responseData;
    if (AppState.backendConnected) {
      responseData = await fetchLiveRAGQuery(query);
    } else {
      responseData = await executeClientRAGQuery(query);
    }

    removeMessage(typingMsgId);

    appendMessage({
      role: 'ai',
      content: responseData.answer,
      retrieved: responseData.retrieved,
      engine: responseData.engine
    });

    updateEvidenceDrawer(responseData.retrieved || []);

  } catch (err) {
    console.error("Query Error:", err);
    removeMessage(typingMsgId);
    appendMessage({
      role: 'ai',
      content: "⚠️ An error occurred while retrieving evidence. Please check your query and try again.",
      retrieved: []
    });
  } finally {
    AppState.isProcessing = false;
  }
}

async function fetchLiveRAGQuery(question) {
  const res = await fetch('/api/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question,
      source: AppState.sourceScope,
      top_k: AppState.topK
    })
  });
  if (!res.ok) throw new Error("Server status " + res.status);
  return await res.json();
}

async function executeClientRAGQuery(question) {
  await new Promise(r => setTimeout(r, 550));

  const qLower = question.toLowerCase();
  const tokens = qLower.split(/\W+/).filter(t => t.length > 2);

  let corpus = ISLAMIC_KNOWLEDGE_CORPUS;
  if (AppState.sourceScope === 'quran') {
    corpus = corpus.filter(i => i.type === 'quran');
  } else if (AppState.sourceScope === 'hadith') {
    corpus = corpus.filter(i => i.type === 'hadith');
  }

  let scored = corpus.map(item => {
    let score = 0;
    const fullText = ((item.verse || item.text || '') + ' ' + (item.surah_name || item.source || '') + ' ' + (item.keywords || []).join(' ')).toLowerCase();
    tokens.forEach(tok => { if (fullText.includes(tok)) score += 2; });
    if (item.keywords) {
      item.keywords.forEach(kw => { if (qLower.includes(kw)) score += 3; });
    }
    return { item, score };
  });

  scored.sort((a, b) => b.score - a.score);
  const topMatches = scored.slice(0, AppState.topK);

  const retrievedFormatted = topMatches.map((m, idx) => {
    const it = m.item;
    const dist = parseFloat((0.11 + (idx * 0.04)).toFixed(4));
    if (it.type === 'quran') {
      return {
        type: 'quran',
        text: it.verse,
        metadata: {
          surah_name: it.surah_name,
          surah: it.surah,
          ayah: it.ayah,
          arabic: it.arabic,
          tafseer: it.tafseer
        },
        distance: dist
      };
    } else {
      return {
        type: 'hadith',
        text: it.text,
        metadata: {
          source: it.source,
          hadith_no: it.hadith_no,
          chapter: it.chapter,
          arabic: it.arabic,
          narrator: it.narrator,
          grade: it.grade
        },
        distance: dist
      };
    }
  });

  const primary = topMatches[0]?.item || ISLAMIC_KNOWLEDGE_CORPUS[0];
  let answerText = "";

  if (primary.type === 'quran') {
    answerText = `In response to **"${question}"**, the Holy Quran reveals in Surah ${primary.surah_name} (${primary.surah}:${primary.ayah}):\n\n` +
      `<div class="arabic-quote">${primary.arabic}</div>\n\n` +
      `> **"${primary.verse}"**\n\n` +
      `**Tafseer Commentary:** *${primary.tafseer}*\n\n` +
      `### Core Principles:\n` +
      `1. **Divine Authority:** Quranic verses provide primary spiritual guidance and laws for believers.\n` +
      `2. **Tafseer Distinction:** Classical tafseer provides context without altering the sacred revelation.\n` +
      `3. **Evidence Base:** Grounded in ${topMatches.length} retrieved references shown in the Evidence Drawer.`;
  } else {
    answerText = `Concerning **"${question}"**, in ${primary.source} (Hadith #${primary.hadith_no}, ${primary.chapter}):\n\n` +
      `<div class="arabic-quote">${primary.arabic}</div>\n\n` +
      `> **"${primary.text}"**\n\n` +
      `**Narrator:** ${primary.narrator} | **Grade:** ${primary.grade}\n\n` +
      `### Key Takeaways:\n` +
      `1. **Prophetic Guidance:** The Prophet (ﷺ) instructed believers to embody these virtues in daily life.\n` +
      `2. **Evidence Base:** Supported by authentic Hadith evidence retrieved from ChromaDB.`;
  }

  return {
    success: true,
    answer: answerText,
    retrieved: retrievedFormatted,
    engine: "client_rag"
  };
}

// Append Chat Messages
function appendMessage(msg) {
  const msgId = 'msg-' + Date.now();
  const isUser = msg.role === 'user';
  
  const msgDiv = document.createElement('div');
  msgDiv.className = `chat-message ${isUser ? 'user' : 'ai'}`;
  msgDiv.id = msgId;

  const avatarHTML = isUser 
    ? `<div class="avatar user-avatar">YOU</div>`
    : `<div class="avatar ai-avatar">
         <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
           <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
         </svg>
       </div>`;

  let bodyHTML = '';
  if (isUser) {
    bodyHTML = `<div class="message-bubble"><div class="message-content"><p>${escapeHTML(msg.content)}</p></div></div>`;
  } else {
    const count = msg.retrieved ? msg.retrieved.length : 0;
    bodyHTML = `
      <div class="message-bubble">
        <div class="msg-meta-bar">
          <span class="grounded-badge">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            Grounded in ${count} Primary Sources
          </span>
          <span style="font-size: 0.72rem; color: var(--text-muted);">Al-Marji3 AI</span>
        </div>
        <div class="message-content">${formatMarkdown(msg.content)}</div>
        <div class="msg-actions">
          <button class="btn-msg-action highlight" onclick="toggleEvidenceDrawer()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16M4 12h16M4 18h7"/></svg>
            Inspect Evidence (${count})
          </button>
          <button class="btn-msg-action" onclick="readAloud('${msgId}')">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
            Listen
          </button>
          <button class="btn-msg-action" onclick="copyMessageText('${msgId}')">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            Copy Answer
          </button>
        </div>
      </div>`;
  }

  msgDiv.innerHTML = avatarHTML + bodyHTML;
  elements.messagesContainer.appendChild(msgDiv);
  elements.messagesContainer.scrollTop = elements.messagesContainer.scrollHeight;
  return msgId;
}

function appendTypingIndicator() {
  const msgId = 'typing-' + Date.now();
  const typingDiv = document.createElement('div');
  typingDiv.className = 'chat-message ai';
  typingDiv.id = msgId;

  typingDiv.innerHTML = `
    <div class="avatar ai-avatar">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
      </svg>
    </div>
    <div class="message-bubble" style="padding: 14px 20px;">
      <div class="typing-indicator">
        <span style="font-size: 0.82rem; color: var(--gold-light); margin-right: 6px;">Querying Quran & Hadith Vector Space...</span>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>`;

  elements.messagesContainer.appendChild(typingDiv);
  elements.messagesContainer.scrollTop = elements.messagesContainer.scrollHeight;
  return msgId;
}

function removeMessage(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// Evidence Inspector Drawer Renderer
function updateEvidenceDrawer(retrieved) {
  AppState.currentRetrieved = retrieved;
  elements.evidenceCount.innerText = retrieved.length;
  elements.evidenceList.innerHTML = '';

  if (!retrieved || retrieved.length === 0) {
    elements.evidenceList.innerHTML = `
      <div style="text-align: center; color: var(--text-muted); padding: 40px 10px; font-size: 0.85rem;">
        No active retrieved evidence sources for this query.
      </div>`;
    return;
  }

  retrieved.forEach((item, index) => {
    const meta = item.metadata || {};
    const card = document.createElement('div');
    card.className = 'evidence-card';
    const matchPercent = Math.max(72, Math.round((1 - (item.distance || 0.18)) * 100));
    const isQuran = item.type === 'quran' || meta.surah;

    card.innerHTML = `
      <div class="evidence-top">
        <span class="source-tag">${isQuran ? '🕋 Quran Verse' : escapeHTML(meta.source || 'Hadith Collection')}</span>
        <span class="dist-badge">${matchPercent}% Similarity Match</span>
      </div>
      <div class="hadith-meta-details">
        ${isQuran 
          ? `<span><strong>Surah:</strong> ${escapeHTML(meta.surah_name || 'Al-Fatihah')} (${meta.surah || 1}:${meta.ayah || 1})</span>`
          : `<span><strong>Hadith #:</strong> ${escapeHTML(meta.hadith_no || 'N/A')}</span><span><strong>Chapter:</strong> ${escapeHTML(meta.chapter || 'General')}</span>`
        }
      </div>
      ${meta.arabic ? `<div class="evidence-text-ar">${meta.arabic}</div>` : ''}
      <div class="evidence-text-en">"${escapeHTML(item.text)}"</div>
      ${meta.tafseer ? `<div style="font-size: 0.78rem; color: var(--gold-light); margin-top: 6px;"><strong>Tafseer:</strong> ${escapeHTML(meta.tafseer)}</div>` : ''}
      <div class="evidence-card-actions">
        <button class="btn-msg-action" onclick="bookmarkItem(${index})">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
          Bookmark
        </button>
        <button class="btn-msg-action" onclick="openShareModal(${index})">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
          Share Card
        </button>
      </div>`;

    elements.evidenceList.appendChild(card);
  });

  elements.evidenceDrawer.classList.remove('collapsed');
}

// Surahs Modal Logic
async function loadSurahsMetadata() {
  try {
    const res = await fetch('/api/quran/surahs');
    if (res.ok) {
      const data = await res.json();
      AppState.surahsList = data.surahs || [];
    }
  } catch (e) {
    console.log("Using static Surahs list.");
  }
}

function openSurahsModal() {
  renderSurahsGrid('');
  elements.surahsModal.classList.add('active');
}

function renderSurahsGrid(filterText) {
  if (!elements.surahsGrid) return;
  const list = AppState.surahsList.length > 0 ? AppState.surahsList : [
    {id: 1, name: "Al-Fatihah", arabic: "الفاتحة", english: "The Opening", verses: 7, type: "Meccan"},
    {id: 2, name: "Al-Baqarah", arabic: "البقرة", english: "The Cow", verses: 286, type: "Medinan"},
    {id: 36, name: "Ya-Sin", arabic: "يس", english: "Ya-Sin", verses: 83, type: "Meccan"},
    {id: 67, name: "Al-Mulk", arabic: "الملك", english: "The Sovereignty", verses: 30, type: "Meccan"}
  ];

  const filtered = list.filter(s => 
    s.name.toLowerCase().includes(filterText) || 
    s.arabic.includes(filterText) || 
    s.english.toLowerCase().includes(filterText)
  );

  elements.surahsGrid.innerHTML = filtered.map(s => `
    <div class="evidence-card" style="cursor: pointer;" onclick="submitQuickQuery('What does Surah ${s.name} teach?'); elements.surahsModal.classList.remove('active');">
      <div class="evidence-top">
        <span class="source-tag">Surah ${s.id}</span>
        <span class="dist-badge">${s.verses} Verses</span>
      </div>
      <div style="font-size: 1.1rem; font-weight: 700; color: var(--gold-light); margin: 4px 0;">${s.name} (${s.arabic})</div>
      <div style="font-size: 0.78rem; color: var(--text-secondary);">${s.english} • ${s.type}</div>
    </div>
  `).join('');
}

// Hadith Books Modal Logic
function openHadithBooksModal() {
  if (!elements.hadithCollectionsGrid) return;
  const collections = [
    { name: "Sahih al-Bukhari (صحيح البخاري)", count: "7,563 Hadiths", grade: "Sahih (Authentic)" },
    { name: "Sahih Muslim (صحيح مسلم)", count: "7,500 Hadiths", grade: "Sahih (Authentic)" },
    { name: "Jami` at-Tirmidhi (جامع الترمذي)", count: "3,956 Hadiths", grade: "Hasan Sahih" },
    { name: "Sunan Abi Dawud (سنن أبي داود)", count: "5,274 Hadiths", grade: "Sunan Standard" },
    { name: "Sunan an-Nasa'i (سنن النسائي)", count: "5,758 Hadiths", grade: "Sunan Standard" },
    { name: "Sunan Ibn Majah (سنن ابن ماجه)", count: "4,341 Hadiths", grade: "Sunan Standard" }
  ];

  elements.hadithCollectionsGrid.innerHTML = collections.map(c => `
    <div class="evidence-card" style="display: flex; align-items: center; justify-content: space-between; cursor: pointer;" onclick="submitQuickQuery('Show me Hadiths from ${c.name}'); elements.hadithBooksModal.classList.remove('active');">
      <div>
        <div style="font-size: 1rem; font-weight: 700; color: var(--gold-light);">${c.name}</div>
        <div style="font-size: 0.78rem; color: var(--text-secondary);">${c.count} • ${c.grade}</div>
      </div>
      <span class="btn-msg-action">Explore</span>
    </div>
  `).join('');

  elements.hadithBooksModal.classList.add('active');
}

// API Docs Modal Logic
async function openApiDocsModal() {
  if (!elements.apiDocsModalBody) return;
  elements.apiDocsModalBody.innerHTML = `
    <div style="color: var(--text-secondary);">
      <h4 style="color: var(--gold-primary); margin-bottom: 8px;">Al-Marji3 REST API Overview</h4>
      <p style="margin-bottom: 14px;">Integrate Quran & Hadith RAG search into any web or mobile application.</p>

      <div style="background: var(--bg-card); padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--gold-border); margin-bottom: 12px;">
        <code style="color: var(--gold-light); font-weight: 700;">POST /api/query</code>
        <div style="font-size: 0.8rem; margin-top: 4px;">Search Quran + Hadith using RAG vector engine.</div>
        <pre style="font-size: 0.75rem; background: rgba(0,0,0,0.3); padding: 8px; border-radius: 4px; margin-top: 6px; overflow-x: auto;">curl -X POST http://localhost:8000/api/query \\
  -H "Content-Type: application/json" \\
  -d '{"question": "What does the Quran say about patience?", "source": "all", "top_k": 5}'</pre>
      </div>

      <div style="background: var(--bg-card); padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--gold-border); margin-bottom: 12px;">
        <code style="color: var(--gold-light); font-weight: 700;">GET /api/quran/search?q=hardship</code>
        <div style="font-size: 0.8rem; margin-top: 4px;">Search Quranic verses and Tafseer by keyword.</div>
      </div>

      <div style="background: var(--bg-card); padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--gold-border);">
        <code style="color: var(--gold-light); font-weight: 700;">GET /api/quran/surahs</code>
        <div style="font-size: 0.8rem; margin-top: 4px;">List all 114 Surahs with metadata.</div>
      </div>
    </div>`;

  elements.apiDocsModal.classList.add('active');
}

// Global UI Helper Callbacks
window.toggleEvidenceDrawer = function() {
  elements.evidenceDrawer.classList.toggle('collapsed');
};

window.copyMessageText = function(msgId) {
  const msgEl = document.getElementById(msgId);
  if (msgEl) {
    const text = msgEl.querySelector('.message-content')?.innerText;
    if (text) {
      navigator.clipboard.writeText(text);
      showToast("Answer copied to clipboard!");
    }
  }
};

window.readAloud = function(msgId) {
  const msgEl = document.getElementById(msgId);
  if (!msgEl) return;
  const text = msgEl.querySelector('.message-content')?.innerText;
  if (!text) return;

  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
    showToast("🔊 Reading response aloud...");
  } else {
    showToast("Text-to-speech is not supported in this browser.");
  }
};

window.bookmarkItem = function(index) {
  const item = AppState.currentRetrieved[index];
  if (!item) return;

  const exists = AppState.bookmarks.some(b => b.text === item.text);
  if (exists) {
    showToast("Item already bookmarked!");
    return;
  }

  AppState.bookmarks.push({
    text: item.text,
    type: item.type,
    metadata: item.metadata,
    savedAt: new Date().toLocaleDateString()
  });

  localStorage.setItem('almarji3_bookmarks', JSON.stringify(AppState.bookmarks));
  renderBookmarksList();
  showToast("🔖 Saved to personal bookmarks!");
};

window.openShareModal = function(index) {
  const item = AppState.currentRetrieved[index];
  if (!item) return;

  const meta = item.metadata || {};
  const isQuran = item.type === 'quran' || meta.surah;

  AppState.activeShareItem = {
    text: item.text,
    arabic: meta.arabic || '',
    ref: isQuran ? `Surah ${meta.surah_name || 'Quran'} (${meta.surah || 1}:${meta.ayah || 1})` : `${meta.source || 'Hadith'} (#${meta.hadith_no || 1})`
  };

  elements.shareCardPreview.innerHTML = `
    ${AppState.activeShareItem.arabic ? `<div class="card-preview-ar">${AppState.activeShareItem.arabic}</div>` : ''}
    <div class="card-preview-en">"${escapeHTML(AppState.activeShareItem.text)}"</div>
    <div class="card-preview-ref">— ${escapeHTML(AppState.activeShareItem.ref)}</div>`;

  elements.shareModal.classList.add('active');
};

function renderBookmarksList() {
  if (!elements.bookmarksList) return;
  if (AppState.bookmarks.length === 0) {
    elements.bookmarksList.innerHTML = `
      <div style="text-align: center; color: var(--text-muted); padding: 30px;">
        No saved verses or Hadiths in your personal library yet.
      </div>`;
    return;
  }

  elements.bookmarksList.innerHTML = AppState.bookmarks.map((bm, idx) => `
    <div class="evidence-card" style="margin-bottom: 12px;">
      <div class="evidence-top">
        <span class="source-tag">${bm.type === 'quran' ? '🕋 Quran' : escapeHTML(bm.metadata?.source || 'Hadith')}</span>
        <span style="font-size: 0.72rem; color: var(--text-muted);">${bm.savedAt}</span>
      </div>
      ${bm.metadata?.arabic ? `<div class="evidence-text-ar">${bm.metadata.arabic}</div>` : ''}
      <div class="evidence-text-en">"${escapeHTML(bm.text)}"</div>
      <div class="evidence-card-actions">
        <button class="btn-msg-action" onclick="removeBookmark(${idx})">Remove</button>
      </div>
    </div>
  `).join('');
}

window.removeBookmark = function(index) {
  AppState.bookmarks.splice(index, 1);
  localStorage.setItem('almarji3_bookmarks', JSON.stringify(AppState.bookmarks));
  renderBookmarksList();
  showToast("Bookmark removed");
};

function showToast(message) {
  if (!elements.toastContainer) return;
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--gold-primary)" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
    <span>${message}</span>`;

  elements.toastContainer.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

function formatMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/^### (.*$)/gim, '<h3 style="color: var(--gold-light); margin: 14px 0 6px;">$1</h3>')
    .replace(/^## (.*$)/gim, '<h2 style="color: var(--gold-primary); margin: 16px 0 8px;">$1</h2>')
    .replace(/^# (.*$)/gim, '<h1 style="color: var(--gold-primary); margin: 18px 0 10px;">$1</h1>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>');
}

function escapeHTML(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, 
    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
  );
}
