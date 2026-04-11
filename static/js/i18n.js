/**
 * i18n.js - Onui Internationalization Helper
 */

let translations = {};

async function setAppLang(lang) {
    localStorage.setItem("app_lang", lang);
    await loadTranslations(lang);
    applyTranslations();
    
    // Update label if exists
    const lbl = document.getElementById("current-lang-label");
    if (lbl) lbl.textContent = lang.toUpperCase();
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
                el.textContent = translations[key];
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    const lang = localStorage.getItem("app_lang") || "en";
    await loadTranslations(lang);
    applyTranslations();
});
