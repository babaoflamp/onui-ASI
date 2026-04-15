/**
 * i18n.js - Onui Internationalization Helper
 */

let translations = {};

async function setAppLang(lang) {
    localStorage.setItem("app_lang", lang);
    await loadTranslations(lang);
    applyTranslations();
    
    // Update labels and flags
    const lbl = document.getElementById("current-lang-label");
    if (lbl) lbl.textContent = lang.toUpperCase();

    const flagEl = document.getElementById("current-lang-flag");
    const nameEl = document.getElementById("current-lang-name");
    if (flagEl && nameEl) {
        const flags = { ko: "🇰🇷", en: "🇺🇸", ja: "🇯🇵", zh: "🇨🇳" };
        flagEl.textContent = flags[lang] || "🌍";
        nameEl.textContent = lang.toUpperCase();
    }
}

async function loadTranslations(lang) {
    try {
        const resp = await fetch(`/data/locales/${lang}.json`);
        if (resp.ok) {
            translations = await resp.json();
        }
    } catch (err) {
        console.error("Failed to load translations:", err);
    }
}

function applyTranslations() {
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (translations[key]) {
            if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
                el.placeholder = translations[key];
            } else {
                el.innerHTML = translations[key];
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    const lang = localStorage.getItem("app_lang") || "en";
    await loadTranslations(lang);
    applyTranslations();

    // FOUC 방지 해제: 번역 적용 완료 후 표시
    document.documentElement.style.visibility = "";

    // Sync header selector if it exists
    const flagEl = document.getElementById("current-lang-flag");
    const nameEl = document.getElementById("current-lang-name");
    if (flagEl && nameEl) {
        const flags = { ko: "🇰🇷", en: "🇺🇸", ja: "🇯🇵", zh: "🇨🇳" };
        flagEl.textContent = flags[lang] || "🌍";
        nameEl.textContent = lang.toUpperCase();
    }
});
