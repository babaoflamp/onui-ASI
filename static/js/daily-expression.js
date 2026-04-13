// 오늘의 표현 - Daily Expression Card Slider JavaScript

(function() {
  'use strict';

  let expressions = [];
  let currentIndex = 0;
  let currentAudio = null;

  const card = document.getElementById("expressionCard");
  const sentenceKrEl = document.getElementById("sentenceKr");
  const sentenceEnEl = document.getElementById("sentenceEn");
  const romanizedEl = document.getElementById("romanizedText");
  const cultureNoteEl = document.getElementById("cultureNote");
  const levelChipEl = document.getElementById("levelChip");
  const situationLabelEl = document.getElementById("situationLabel");
  const tagLabelEl = document.getElementById("tagLabel");
  const sliderCaptionEl = document.getElementById("sliderCaption");
  const dotsContainer = document.getElementById("dots");
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");
  const ttsBtn = document.getElementById("ttsBtn");
  const ttsIcon = document.getElementById("ttsIcon");

  // Load expressions from API, pass current month so this month comes first
  async function loadExpressions() {
    try {
      const month = new Date().getMonth() + 1; // 1-12
      const response = await fetch(`/api/expressions?month=${month}`);
      const data = await response.json();
      expressions = data.expressions || [];

      if (expressions.length > 0) {
        createDots();
        renderCard();
      } else {
        card.innerHTML = '<p class="text-gray-500">No expression data found.</p>';
      }
    } catch (error) {
      console.error('Error loading expressions:', error);
      card.innerHTML = '<p class="text-red-500">Error loading data.</p>';
    }
  }

  // Create navigation dots
  function createDots() {
    dotsContainer.innerHTML = '';
    expressions.forEach((_, idx) => {
      const dot = document.createElement("div");
      dot.className = "dot";
      dot.dataset.index = idx;
      dot.addEventListener("click", () => {
        currentIndex = idx;
        renderCard();
      });
      dotsContainer.appendChild(dot);
    });
  }

  // Render current card
  function renderCard() {
    if (!expressions.length) return;
    stopTTS();

    const data = expressions[currentIndex];
    const lang = localStorage.getItem("app_lang") || "en";

    sentenceKrEl.textContent = data.sentenceKr;
    romanizedEl.textContent = data.romanized || '';
    sentenceEnEl.textContent = data.sentenceEn;

    if (lang === "ko") {
      cultureNoteEl.textContent = data.cultureNote;
      situationLabelEl.textContent = data.situation;
      tagLabelEl.textContent = data.tag;
    } else {
      cultureNoteEl.textContent = data.cultureNoteEn || data.cultureNote;
      situationLabelEl.textContent = data.situationEn || data.situation;
      tagLabelEl.textContent = data.tagEn || data.tag;
    }

    levelChipEl.textContent = "CEFR " + data.level;
    sliderCaptionEl.textContent = `${currentIndex + 1} / ${expressions.length}`;

    // Update dots
    document.querySelectorAll(".dot").forEach((d, idx) => {
      d.classList.toggle("active", idx === currentIndex);
    });

    // Animation effect
    card.style.opacity = "0";
    card.style.transform = "translateY(8px)";
    card.style.transition = "opacity 0.25s ease, transform 0.25s ease";
    requestAnimationFrame(() => {
      setTimeout(() => {
        card.style.opacity = "1";
        card.style.transform = "translateY(0)";
      }, 30);
    });
  }

  // TTS
  async function playTTS(text) {
    if (!text) return;

    if (currentAudio && !currentAudio.paused) {
      stopTTS();
      return; // toggle off on second click
    }

    ttsBtn.disabled = true;
    ttsBtn.classList.add('playing');
    ttsIcon.textContent = '⏸';

    try {
      const resp = await fetch('/api/tts/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language_code: 'ko' })
      });

      if (!resp.ok) throw new Error('TTS failed');

      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      currentAudio = audio;

      ttsBtn.disabled = false;

      audio.onended = () => {
        stopTTS();
        URL.revokeObjectURL(url);
      };
      audio.onerror = () => {
        stopTTS();
        URL.revokeObjectURL(url);
      };

      audio.play();
    } catch (err) {
      console.error('TTS error:', err);
      stopTTS();
    }
  }

  function stopTTS() {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      currentAudio = null;
    }
    if (ttsBtn) {
      ttsBtn.disabled = false;
      ttsBtn.classList.remove('playing');
    }
    if (ttsIcon) ttsIcon.textContent = '🔊';
  }

  // TTS button click
  if (ttsBtn) {
    ttsBtn.addEventListener('click', () => {
      const text = expressions[currentIndex]?.sentenceKr;
      if (text) playTTS(text);
    });
  }

  // Navigation buttons
  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      currentIndex = (currentIndex - 1 + expressions.length) % expressions.length;
      renderCard();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      currentIndex = (currentIndex + 1) % expressions.length;
      renderCard();
    });
  }

  // Keyboard navigation
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") prevBtn?.click();
    if (e.key === "ArrowRight") nextBtn?.click();
  });

  // Initialize
  loadExpressions();
})();
