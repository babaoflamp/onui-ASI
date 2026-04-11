// 단어 꽃밭 - Vocabulary Flower Garden JavaScript

(function () {
  "use strict";

  let vocabList = [];
  const flowerGrid = document.getElementById("flowerGrid");
  const detailsBox = document.getElementById("details");
  const infoCaption = document.getElementById("infoCaption");

  // Load vocabulary from API
  async function loadVocabulary() {
    try {
      const response = await fetch("/api/vocabulary");
      const data = await response.json();
      vocabList = data.vocabulary || [];

      if (vocabList.length > 0) {
        renderFlowers();
      } else {
        const noData = (typeof translations !== 'undefined' && translations['vg.no_data']) || "No vocabulary data available.";
        flowerGrid.innerHTML = `<p class="text-gray-500">${noData}</p>`;
      }
    } catch (error) {
      console.error("Error loading vocabulary:", error);
      const errorMsg = (typeof translations !== 'undefined' && translations['dash.error_loading']) || "An error occurred while loading data.";
      flowerGrid.innerHTML = `<p class="text-red-500">${errorMsg}</p>`;
    }
  }

  // Render flower buttons
  function renderFlowers() {
    flowerGrid.innerHTML = "";

    vocabList.forEach((item, index) => {
      const card = document.createElement("div");
      card.className = "flower-card";
      card.dataset.id = item.id;
      card.dataset.level = item.level;

      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "flower-btn";
      btn.setAttribute("aria-label", item.word + " 선택");
      // Normalize emoji: if the data contains a two-letter country code
      // (e.g. "KR"), convert it to the corresponding flag emoji.
      let emojiLabel = item.emoji || "🌸";
      if (/^[A-Za-z]{2}$/.test(emojiLabel)) {
        const code = emojiLabel.toUpperCase();
        emojiLabel = String.fromCodePoint(
          ...[code.charCodeAt(0), code.charCodeAt(1)].map(
            (c) => 0x1f1e6 + (c - 65)
          )
        );
      }
      // If the label is a two-letter country code (e.g. 'KR'), render a
      // Twemoji SVG flag image to ensure consistent flag display across
      // platforms that may not render regional-indicator flags natively.
      if (/^[A-Za-z]{2}$/.test(emojiLabel)) {
        const code = emojiLabel.toUpperCase();
        const parts = [code.charCodeAt(0), code.charCodeAt(1)].map((c) =>
          (0x1f1e6 + (c - 65)).toString(16)
        );
        const svgUrl = `https://twemoji.maxcdn.com/v/latest/svg/${parts[0]}-${parts[1]}.svg`;
        btn.innerHTML = `<img src="${svgUrl}" alt="${code}" class="emoji-flag" />`;
      } else {
        // Default: place the emoji or fallback glyph as text content
        btn.textContent = emojiLabel;
      }

      const wordLabel = document.createElement("div");
      wordLabel.className = "flower-word";
      wordLabel.textContent = item.word;

      const cefr = document.createElement("div");
      cefr.className = "cefr-pill";
      cefr.innerHTML = `<span class="cefr-dot"></span> CEFR ${item.level}`;

      card.appendChild(btn);
      card.appendChild(wordLabel);
      card.appendChild(cefr);

      flowerGrid.appendChild(card);

      // Auto-select first word
      if (index === 0) {
        card.classList.add("active");
        showDetails(item);
      }

      card.addEventListener("click", () => {
        document
          .querySelectorAll(".flower-card")
          .forEach((c) => c.classList.remove("active"));
        card.classList.add("active");
        showDetails(item);
      });
    });
  }

  // Show word details in right panel
  let currentItem = null;

  function showDetails(item) {
    if (!detailsBox) return;

    currentItem = item; // Store for TTS functions

    const mainWord = detailsBox.querySelector(".main-word");
    const roman = detailsBox.querySelector(".roman");
    const meaning = detailsBox.querySelector(".meaning");
    const tagWrap = detailsBox.querySelector(".tag-wrap");
    const sentKr = detailsBox.querySelector(".sentence-kr");
    const sentEn = detailsBox.querySelector(".sentence-en");

    if (mainWord) mainWord.textContent = item.word;
    if (roman) {
      const romanLabel = (typeof translations !== 'undefined' && translations['vg.pronunciation']) || "Pronunciation";
      roman.textContent = item.roman
        ? `${romanLabel}: ${item.roman}`
        : "";
    }
    if (meaning) {
      const meanLabel = (typeof translations !== 'undefined' && translations['vg.meaning']) || "Meaning";
      meaning.textContent = `${meanLabel}: ${item.meaningKo} (${item.meaningEn})`;
    }

    // Tags
    if (tagWrap) {
      tagWrap.innerHTML = "";
      const levelTag = document.createElement("span");
      levelTag.className = "tag level";
      levelTag.textContent = `CEFR ${item.level}`;
      tagWrap.appendChild(levelTag);

      if (item.tags && item.tags.length > 0) {
        item.tags.forEach((t) => {
          const tag = document.createElement("span");
          tag.className = "tag";
          tag.textContent = t;
          tagWrap.appendChild(tag);
        });
      }
    }

    if (sentKr) sentKr.textContent = item.sentenceKr || "";
    if (sentEn) sentEn.textContent = item.sentenceEn || "";

    if (infoCaption) {
      const selectedMsg = (typeof translations !== 'undefined' && translations['vg.selected']) || "is selected.";
      infoCaption.textContent = `"${item.word}" ${selectedMsg}`;
    }
  }

  // Play word pronunciation using MzTTS
  window.playWord = async function() {
    if (!currentItem) {
      const selectWord = (typeof translations !== 'undefined' && translations['vg.select_first']) || "Please select a word first.";
      alert(selectWord);
      return;
    }

    const btn = document.getElementById('playWordBtn');
    btn.disabled = true;

    try {
      const payload = {
        text: currentItem.word,
        speaker: 0, // Hanna
        tempo: 0.9, // Slightly slower
        pitch: 1.0,
        gain: 1.2
      };

      const response = await fetch('/api/tts/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('TTS generation failed');
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
      };

      await audio.play();

    } catch (error) {
      console.error('Error playing word:', error);
      const playError = (typeof translations !== 'undefined' && translations['vg.play_error']) || "An error occurred during audio playback.";
      alert(playError);
    } finally {
      btn.disabled = false;
    }
  };

  // Play sentence pronunciation using MzTTS
  window.playSentence = async function() {
    if (!currentItem || !currentItem.sentenceKr) {
      const noExample = (typeof translations !== 'undefined' && translations['vg.no_example']) || "No example sentence available.";
      alert(noExample);
      return;
    }

    const btn = document.getElementById('playSentenceBtn');
    btn.disabled = true;

    try {
      const payload = {
        text: currentItem.sentenceKr,
        speaker: 0, // Hanna
        tempo: 0.85, // Slower for sentences
        pitch: 1.0,
        gain: 1.2
      };

      const response = await fetch('/api/tts/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('TTS generation failed');
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
      };

      await audio.play();

    } catch (error) {
      console.error('Error playing sentence:', error);
      const playError = (typeof translations !== 'undefined' && translations['vg.play_error']) || "An error occurred during audio playback.";
      alert(playError);
    } finally {
      btn.disabled = false;
    }
  };

  // Initialize
  loadVocabulary();
})();
