/* ==========================================================================
   Studio Ghibli Interactive Edition — Page 21 Script
   Unit 5: Things you have
   Interactive Exercises 5.3, 5.4 & 5.5 (Substitution Chart Engine)
   ========================================================================== */

(function () {
  'use strict';

  /* 1. State Management */
  let currentTheme = localStorage.getItem('ghibli_theme') || 'day';
  let activeAudio = null;
  let activeRecorders = {};
  let recordedAudios = {};

  // Exercise 5.5 Substitution Chart State
  let selectedBlocks5_5 = {
    pointer: 'This',
    verb: 'is',
    possessive: 'her',
    noun: 'cat.'
  };

  const ALL_12_SENTENCES_5_5 = [
    "This is her cat.",
    "This is her parrot.",
    "This is their cat.",
    "This is their parrot.",
    "This is my cat.",
    "This is my parrot.",
    "That is her cat.",
    "That is her parrot.",
    "That is their cat.",
    "That is their parrot.",
    "That is my cat.",
    "That is my parrot."
  ];

  let discoveredSet5_5 = new Set(["This is her cat."]);

  // Pomodoro Timer State
  let pomodoroTime = 25 * 60;
  let isPomodoroRunning = false;
  let pomodoroInterval = null;
  let pomodoroMode = 'work';

  // Teacher Lewis Mascot Quotes for Unit 5
  const MASCOT_QUOTES = [
    "Konnichiwa! 🌿 Welcome to Page 21 of Teacher Lewis's Practice Book!",
    "Tip: Use 'this' for things close to you, and 'that' for things further away! 👈👉",
    "Possessive words like 'my', 'her', and 'their' show who an animal belongs to! 🐾",
    "Say each sentence out loud to train your English rhythm and confidence! 🗣️",
    "Try building all 12 sentences in Exercise 5.5 to discover every combination! ✨",
    "Great effort! Every practice step brings you closer to fluency. 🍃"
  ];

  /* 2. Document Initialization */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPage);
  } else {
    initPage();
  }

  function initPage() {
    setupTimeOfDay();
    setupAmbientMusic();
    setupMascotAndPomodoro();
    setupAudioButtons();
    setupVoiceRecorders();
    setupExercise5_3();
    setupExercise5_4();
    setupExercise5_5();
    setupGradingAndReset();
  }

  /* 3. Time of Day (Day / Sunset / Night) & Fireflies */
  function setupTimeOfDay() {
    const todBtns = document.querySelectorAll('.tod-btn');
    
    function applyTheme(theme) {
      currentTheme = theme;
      localStorage.setItem('ghibli_theme', theme);
      document.body.classList.remove('theme-day', 'theme-sunset', 'theme-night');
      document.body.classList.add('theme-' + theme);

      todBtns.forEach(btn => {
        if (btn.dataset.theme === theme) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });

      const container = document.getElementById('firefliesContainer');
      if (theme === 'night') {
        spawnFireflies(container, 18);
        speakMascot("Nighttime in the Ghibli forest... Listen to the fireflies! 🌙", 4000);
      } else {
        if (container) container.innerHTML = '';
        if (theme === 'sunset') {
          speakMascot("Golden hour! The sunset brings peace to our study space. 🌅", 4000);
        }
      }
    }

    todBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        applyTheme(btn.dataset.theme);
      });
    });

    applyTheme(currentTheme);
  }

  function spawnFireflies(container, count = 18) {
    if (!container) return;
    container.innerHTML = '';
    for (let i = 0; i < count; i++) {
      const fly = document.createElement('div');
      fly.className = 'ghibli-firefly';
      fly.style.left = Math.random() * 100 + '%';
      fly.style.top = Math.random() * 100 + '%';
      fly.style.animationDelay = Math.random() * 4 + 's';
      fly.style.animationDuration = 3 + Math.random() * 4 + 's';
      container.appendChild(fly);
    }
  }

  /* 4. Ambient Background Music Toggle */
  function setupAmbientMusic() {
    document.querySelectorAll('#toggleAmbientBtn, .bgm-toggle-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (window.GhibliAudio && window.GhibliAudio.toggleBGM) {
          window.GhibliAudio.toggleBGM(btn);
        }
      });
    });
    if (window.GhibliAudio && window.GhibliAudio.syncBGMButtonState) {
      window.GhibliAudio.syncBGMButtonState();
    }
  }

  /* 5. Mascot & Pomodoro Timer */
  function setupMascotAndPomodoro() {
    const avatar = document.getElementById('mascotAvatarWrap') || document.getElementById('mascotAvatarImg');
    const pomoToggle = document.getElementById('pomoToggleBtn');
    const pomoOpt = document.getElementById('pomoOptBtn');
    const quickPresets = document.getElementById('pomoQuickPresets');

    if (avatar) {
      avatar.addEventListener('click', () => {
        const quote = MASCOT_QUOTES[Math.floor(Math.random() * MASCOT_QUOTES.length)];
        speakMascot(quote, 5000);
        if (window.GhibliAudio && window.GhibliAudio.playWaterDrop) {
          window.GhibliAudio.playWaterDrop();
        }
      });
    }

    if (pomoToggle) {
      pomoToggle.addEventListener('click', togglePomodoro);
    }

    if (pomoOpt && quickPresets) {
      pomoOpt.addEventListener('click', () => {
        quickPresets.classList.toggle('hidden');
      });

      quickPresets.querySelectorAll('.pomo-quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          quickPresets.querySelectorAll('.pomo-quick-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          const mins = parseInt(btn.dataset.mins, 10) || 25;
          setPomodoroDuration(mins);
          quickPresets.classList.add('hidden');
        });
      });
    }
  }

  function speakMascot(text, duration = 4000) {
    const bubble = document.getElementById('mascotBubble');
    const content = document.getElementById('mascotTextContent');
    if (content) content.textContent = `"${text}"`;
    if (bubble) {
      bubble.style.display = 'block';
      bubble.classList.remove('focused-auto-collapsed');
      clearTimeout(bubble._timeout);
      bubble._timeout = setTimeout(() => {
        bubble.classList.add('focused-auto-collapsed');
      }, duration);
    }
  }
  window.speakMascot = speakMascot;

  function togglePomodoro() {
    const icon = document.getElementById('pomoIcon');
    if (isPomodoroRunning) {
      clearInterval(pomodoroInterval);
      isPomodoroRunning = false;
      if (icon) icon.className = 'fa-solid fa-play';
      speakMascot("Pomodoro paused. Take a deep breath! 🌿", 3000);
    } else {
      isPomodoroRunning = true;
      if (icon) icon.className = 'fa-solid fa-pause';
      speakMascot(pomodoroMode === 'work' ? "Focus session started! Let's practice English. 📖" : "Break time! Stretch and relax. 🍵", 3000);

      pomodoroInterval = setInterval(() => {
        pomodoroTime--;
        if (pomodoroTime < 0) {
          clearInterval(pomodoroInterval);
          isPomodoroRunning = false;
          if (icon) icon.className = 'fa-solid fa-play';

          if (pomodoroMode === 'work') {
            pomodoroMode = 'break';
            setPomodoroDuration(5);
            if (window.GhibliAudio && window.GhibliAudio.playFanfare) window.GhibliAudio.playFanfare();
            speakMascot("Well done! 5-minute Ghibli break time! 🍵", 6000);
          } else {
            pomodoroMode = 'work';
            setPomodoroDuration(25);
            if (window.GhibliAudio && window.GhibliAudio.playChime) window.GhibliAudio.playChime();
            speakMascot("Ready to practice again? Let's go! 🌿", 6000);
          }
        }
        updatePomodoroDisplay();
      }, 1000);
    }
  }

  function setPomodoroDuration(mins) {
    pomodoroTime = mins * 60;
    updatePomodoroDisplay();
  }

  function updatePomodoroDisplay() {
    const display = document.getElementById('pomoMinTime');
    if (!display) return;
    const m = Math.floor(pomodoroTime / 60).toString().padStart(2, '0');
    const s = (pomodoroTime % 60).toString().padStart(2, '0');
    display.textContent = `${m}:${s}`;
  }

  /* 6. Audio Playback Helper */
  function setupAudioButtons() {
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-audio]');
      if (!btn) return;
      // If button has specific handler like playSentenceBtn, let it handle
      if (btn.id === 'playSentenceBtn' || btn.id === 'playGreetingBtn') return;

      const audioSrc = btn.getAttribute('data-audio');
      if (audioSrc) {
        playAudioTrack(audioSrc, '', btn);
      }
    });
  }

  function playAudioTrack(src, text = '', btn = null) {
    if (activeAudio) {
      activeAudio.pause();
      activeAudio = null;
    }

    if (btn) btn.classList.add('playing');

    const resetBtn = () => {
      if (btn) btn.classList.remove('playing');
    };

    if (src) {
      const audio = new Audio(src);
      activeAudio = audio;
      audio.play().then(() => {
        audio.onended = resetBtn;
      }).catch(err => {
        console.warn('Audio playback fallback to TTS:', err);
        speakSentence(text, resetBtn);
      });
    } else if (text) {
      speakSentence(text, resetBtn);
    }
  }

  function speakSentence(text, onEnded = null) {
    if ('speechSynthesis' in window && text) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.92;
      utterance.pitch = 1.0;
      utterance.lang = 'en-US';
      if (onEnded) utterance.onend = onEnded;
      utterance.onerror = onEnded;
      window.speechSynthesis.speak(utterance);
    } else if (onEnded) {
      onEnded();
    }
  }

  /* 7. Voice Recorder ("Rec" and "My Voice") */
  function setupVoiceRecorders() {
    document.addEventListener('click', async (e) => {
      const recBtn = e.target.closest('.rec-btn, .voice-btn.rec-btn');
      if (recBtn) {
        handleRecordToggle(recBtn);
        return;
      }

      const playVoiceBtn = e.target.closest('.play-rec-btn, .voice-btn.play-rec-btn');
      if (playVoiceBtn) {
        handlePlayVoice(playVoiceBtn);
      }
    });
  }

  async function handleRecordToggle(recBtn) {
    const id = recBtn.getAttribute('data-id') || 'rec_default';
    const isRec = recBtn.classList.contains('recording');

    if (!isRec) {
      recBtn.classList.add('recording');
      recBtn.innerHTML = '<i class="fa-solid fa-square-stop" style="color:#ef4444;"></i> Stop';

      try {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia && typeof MediaRecorder !== 'undefined') {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          const mr = new MediaRecorder(stream);
          const chunks = [];
          mr.ondataavailable = (e) => chunks.push(e.data);
          mr.onstop = () => {
            const blob = new Blob(chunks, { type: 'audio/webm' });
            recordedAudios[id] = URL.createObjectURL(blob);
            revealPlayVoiceBtn(recBtn, id);
          };
          mr.start();
          activeRecorders[id] = { mr, stream };
        } else {
          recordedAudios[id] = 'practice_voice';
          revealPlayVoiceBtn(recBtn, id);
        }
      } catch (err) {
        console.warn('Microphone access denied or unavailable:', err);
        recordedAudios[id] = 'practice_voice';
        revealPlayVoiceBtn(recBtn, id);
      }

      speakMascot("Recording your voice... Speak clearly into your mic! 🎙️", 3000);
    } else {
      recBtn.classList.remove('recording');
      recBtn.innerHTML = '<i class="fa-solid fa-microphone"></i> Rec';

      if (activeRecorders[id]) {
        const { mr, stream } = activeRecorders[id];
        mr.stop();
        stream.getTracks().forEach(t => t.stop());
        delete activeRecorders[id];
      }

      speakMascot("Recording saved! Click 'Voice' to listen. 🎧", 3000);
    }
  }

  function revealPlayVoiceBtn(recBtn, id) {
    const parent = recBtn.parentNode;
    if (!parent) return;
    let playBtn = parent.querySelector(`.play-rec-btn[data-id="${id}"], .play-rec-btn`);
    if (playBtn) {
      playBtn.classList.remove('hidden');
      playBtn.style.display = 'inline-flex';
    }
  }

  function handlePlayVoice(playBtn) {
    const id = playBtn.getAttribute('data-id');
    const audioUrl = recordedAudios[id];
    if (audioUrl && audioUrl.startsWith('blob:')) {
      const a = new Audio(audioUrl);
      a.play().catch(e => console.warn(e));
      speakMascot("Playing your recorded voice! 🔊", 3000);
    } else {
      // Fallback voice playback
      speakMascot("Playing voice playback! 🔊", 3000);
      if (id && id.includes('5_5')) {
        const currentSentence = `${selectedBlocks5_5.pointer} ${selectedBlocks5_5.verb} ${selectedBlocks5_5.possessive} ${selectedBlocks5_5.noun}`;
        speakSentence(currentSentence);
      }
    }
  }

  /* 8. Exercise 5.3: Fill in the Gaps (This / That) */
  function setupExercise5_3() {
    document.querySelectorAll('.ex5-3-input, .ghibli-input').forEach(input => {
      input.addEventListener('input', () => {
        input.classList.remove('correct', 'incorrect');
      });
    });
  }

  /* 9. Exercise 5.4: Sentence Ordering (Word Bank) */
  function setupExercise5_4() {
    const containers = document.querySelectorAll('.ghibli-ordering-container');
    
    containers.forEach(container => {
      const wordPool = container.querySelector('.word-pool');
      const dropSlot = container.querySelector('.ghibli-drop-slot');
      const resetBtn = container.querySelector('.ghibli-order-reset-btn');
      const orderInput = container.querySelector('.order-input');

      // Click on chip to move between word pool and sentence slot
      container.addEventListener('click', (e) => {
        const chip = e.target.closest('.word-chip');
        if (!chip) return;

        if (chip.parentElement === wordPool && dropSlot) {
          dropSlot.appendChild(chip);
        } else if (chip.parentElement === dropSlot && wordPool) {
          wordPool.appendChild(chip);
        }

        updateOrderingInput(container);
        if (window.GhibliAudio && window.GhibliAudio.playWaterDrop) {
          window.GhibliAudio.playWaterDrop();
        }
      });

      if (resetBtn && wordPool && dropSlot) {
        resetBtn.addEventListener('click', () => {
          const chips = Array.from(dropSlot.querySelectorAll('.word-chip'));
          chips.forEach(c => wordPool.appendChild(c));
          updateOrderingInput(container);
          dropSlot.classList.remove('correct', 'incorrect');
          if (window.GhibliAudio && window.GhibliAudio.playClick) {
            window.GhibliAudio.playClick();
          }
        });
      }
    });
  }

  function updateOrderingInput(container) {
    const dropSlot = container.querySelector('.ghibli-drop-slot');
    const orderInput = container.querySelector('.order-input');
    if (!dropSlot || !orderInput) return;

    const words = Array.from(dropSlot.querySelectorAll('.word-chip')).map(c => c.dataset.word || c.textContent.trim());
    orderInput.value = words.join(' ');
  }

  /* 10. Exercise 5.5: Substitution Chart & Sentence Builder Engine */
  function setupExercise5_5() {
    const columns = ['pointer', 'verb', 'possessive', 'noun'];

    columns.forEach(colKey => {
      const colBtns = document.querySelectorAll(`.ghibli-block-btn[data-col="${colKey}"]`);
      colBtns.forEach(btn => {
        btn.addEventListener('click', () => {
          colBtns.forEach(b => b.classList.remove('selected'));
          btn.classList.add('selected');
          selectedBlocks5_5[colKey] = btn.dataset.value;
          updateAssembledSentence5_5();
          if (window.GhibliAudio && window.GhibliAudio.playClick) {
            window.GhibliAudio.playClick();
          }
        });
      });
    });

    const playSentenceBtn = document.getElementById('playSentenceBtn') || document.getElementById('playGreetingBtn');
    if (playSentenceBtn) {
      playSentenceBtn.addEventListener('click', () => {
        const sentence = `${selectedBlocks5_5.pointer} ${selectedBlocks5_5.verb} ${selectedBlocks5_5.possessive} ${selectedBlocks5_5.noun}`;
        playAudioTrack('audio/5/5_5_a.mp3', sentence, playSentenceBtn);
        speakMascot(`Playing Audio 5.5: "${sentence}"`, 3500);
      });
    }

    const trayHeader = document.getElementById('toggleSentencesTray');
    if (trayHeader) {
      trayHeader.addEventListener('click', () => {
        const grid = document.getElementById('ex5_5_tray_grid');
        const icon = trayHeader.querySelector('.tray-icon');
        if (grid) {
          const isHidden = grid.style.display === 'none';
          grid.style.display = isHidden ? 'grid' : 'none';
          if (icon) icon.className = isHidden ? 'fa-solid fa-chevron-down tray-icon' : 'fa-solid fa-chevron-right tray-icon';
        }
      });
    }

    updateAssembledSentence5_5();
  }

  function updateAssembledSentence5_5() {
    const pointer = selectedBlocks5_5.pointer || 'This';
    const verb = selectedBlocks5_5.verb || 'is';
    const possessive = selectedBlocks5_5.possessive || 'her';
    const noun = selectedBlocks5_5.noun || 'cat.';

    // Update chips in preview bar
    const chipP = document.getElementById('chip_pointer') || document.getElementById('chip_demonstrative');
    const chipV = document.getElementById('chip_verb');
    const chipPos = document.getElementById('chip_possessive');
    const chipN = document.getElementById('chip_noun');

    if (chipP) chipP.textContent = pointer;
    if (chipV) chipV.textContent = verb;
    if (chipPos) chipPos.textContent = possessive;
    if (chipN) chipN.textContent = noun;

    const currentSentence = `${pointer} ${verb} ${possessive} ${noun}`;

    // Grammar check: singular demonstratives "This" and "That" require singular verb "is", not "are"
    const isGrammarCorrect = (verb === 'is') && ALL_12_SENTENCES_5_5.includes(currentSentence);
    const valBadge = document.getElementById('ex5_5_val_badge');

    if (valBadge) {
      if (isGrammarCorrect) {
        valBadge.className = 'ex5-5-validation-badge valid';
        valBadge.innerHTML = '<i class="fa-solid fa-circle-check"></i> <span>Valid Sentence!</span>';

        if (!discoveredSet5_5.has(currentSentence)) {
          discoveredSet5_5.add(currentSentence);
          triggerSparkles();
          if (window.GhibliAudio && window.GhibliAudio.playChime) {
            window.GhibliAudio.playChime();
          }
          speakMascot(`🎉 Discovered sentence ${discoveredSet5_5.size}/12: "${currentSentence}"!`, 4000);
        }
      } else {
        valBadge.className = 'ex5-5-validation-badge invalid';
        const hint = verb === 'are'
          ? `Grammar Check: Pair singular "${pointer}" with "is", not "are"`
          : 'Grammar Check: Incomplete or invalid sentence combination';
        valBadge.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> <span>${hint}</span>`;
      }
    }

    updateDiscoveryTray5_5();
  }

  function updateDiscoveryTray5_5() {
    const countEl = document.getElementById('ex5_5_found_count');
    const trayCountEl = document.getElementById('tray_count_5_5');
    const trayGrid = document.getElementById('ex5_5_tray_grid');

    if (countEl) countEl.textContent = discoveredSet5_5.size;
    if (trayCountEl) trayCountEl.textContent = discoveredSet5_5.size;

    if (trayGrid) {
      trayGrid.innerHTML = ALL_12_SENTENCES_5_5.map((s, idx) => {
        const isFound = discoveredSet5_5.has(s);
        if (isFound) {
          return `<div class="ex5-5-tray-item unlocked"><i class="fa-solid fa-star" style="color:var(--ghibli-accent-gold);"></i> ${s}</div>`;
        } else {
          return `<div class="ex5-5-tray-item locked"><i class="fa-regular fa-circle"></i> Sentence ${idx + 1}</div>`;
        }
      }).join('');
    }
  }

  function triggerSparkles() {
    const aura = document.getElementById('mascotAura');
    if (aura) {
      aura.classList.add('sparkle-active');
      setTimeout(() => aura.classList.remove('sparkle-active'), 1200);
    }
  }

  /* 11. Check Answers & Reset Grading Engine */
  function setupGradingAndReset() {
    const checkBtns = document.querySelectorAll('#ghibliCheckAnswersBtn, #ghibliFloatingCheckBtn, .ghibli-check-btn-bottom');
    const resetBtns = document.querySelectorAll('#ghibliResetBtn, .ghibli-reset-btn-bottom');

    checkBtns.forEach(btn => {
      btn.addEventListener('click', checkAnswersPage21);
    });

    resetBtns.forEach(btn => {
      btn.addEventListener('click', resetAnswersPage21);
    });
  }

  function checkAnswersPage21() {
    let totalItems = 0;
    let totalCorrect = 0;

    const normalize = (str) => {
      if (!str) return '';
      return str.toString()
        .toLowerCase()
        .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?'"]/g, '')
        .replace(/\s+/g, ' ')
        .trim();
    };

    // 1. Check Fill in Blank (Exercise 5.3)
    const inputs = document.querySelectorAll('.ex5-3-input, input[data-correct]');
    inputs.forEach(input => {
      if (input.hasAttribute('readonly') || input.classList.contains('example-input')) return;
      totalItems++;

      const userVal = normalize(input.value);
      const correctVal = normalize(input.getAttribute('data-correct') || '');

      input.classList.remove('correct', 'incorrect');
      if (userVal && userVal === correctVal) {
        input.classList.add('correct');
        totalCorrect++;
      } else {
        input.classList.add('incorrect');
      }
    });

    // 2. Check Sentence Ordering (Exercise 5.4)
    const orderingCards = document.querySelectorAll('.ghibli-ordering-container');
    orderingCards.forEach(card => {
      totalItems++;
      const dropSlot = card.querySelector('.ghibli-drop-slot');
      const orderInput = card.querySelector('.order-input');
      const correctVal = normalize(card.getAttribute('data-correct') || (orderInput ? orderInput.getAttribute('data-correct') : ''));

      let userSentence = '';
      if (dropSlot && dropSlot.children.length > 0) {
        userSentence = Array.from(dropSlot.querySelectorAll('.word-chip')).map(c => c.textContent.trim()).join(' ');
      } else if (orderInput) {
        userSentence = orderInput.value;
      }

      const userNorm = normalize(userSentence);
      if (dropSlot) dropSlot.classList.remove('correct', 'incorrect');

      if (userNorm && userNorm === correctVal) {
        if (dropSlot) dropSlot.classList.add('correct');
        totalCorrect++;
      } else {
        if (dropSlot) dropSlot.classList.add('incorrect');
      }
    });

    // Update Score Display
    const scoreBadge = document.getElementById('ghibliScoreBadge');
    const scoreText = document.getElementById('ghibliScoreText');
    if (scoreText) scoreText.textContent = `Score: ${totalCorrect} / ${totalItems}`;

    if (totalCorrect === totalItems && totalItems > 0) {
      if (scoreBadge) scoreBadge.classList.add('perfect');
      if (window.GhibliAudio && window.GhibliAudio.playFanfare) {
        window.GhibliAudio.playFanfare();
      }
      speakMascot(`🌟 Perfect Score! You scored ${totalCorrect}/${totalItems}! Wonderful work! 🍃`, 6000);
    } else {
      if (window.GhibliAudio && window.GhibliAudio.playChime) {
        window.GhibliAudio.playChime();
      }
      speakMascot(`You scored ${totalCorrect} out of ${totalItems}. Keep practicing! 🌿`, 5000);
    }
  }

  function resetAnswersPage21() {
    // 1. Reset Fill in Blank
    document.querySelectorAll('.ex5-3-input, input[data-correct]').forEach(input => {
      if (!input.hasAttribute('readonly') && !input.classList.contains('example-input')) {
        input.value = '';
        input.classList.remove('correct', 'incorrect');
      }
    });

    // 2. Reset Ordering
    document.querySelectorAll('.ghibli-ordering-container').forEach(card => {
      const wordPool = card.querySelector('.word-pool');
      const dropSlot = card.querySelector('.ghibli-drop-slot');
      if (wordPool && dropSlot) {
        const chips = Array.from(dropSlot.querySelectorAll('.word-chip'));
        chips.forEach(c => wordPool.appendChild(c));
        dropSlot.classList.remove('correct', 'incorrect');
      }
    });

    // 3. Reset 5.5 Chart
    selectedBlocks5_5 = {
      pointer: 'This',
      verb: 'is',
      possessive: 'her',
      noun: 'cat.'
    };
    document.querySelectorAll('.ex5-5-col .ghibli-block-btn').forEach(btn => {
      btn.classList.remove('selected');
      if (['This', 'is', 'her', 'cat.'].includes(btn.dataset.value)) {
        btn.classList.add('selected');
      }
    });
    discoveredSet5_5 = new Set(["This is her cat."]);
    updateAssembledSentence5_5();

    const scoreText = document.getElementById('ghibliScoreText');
    if (scoreText) scoreText.textContent = `Score: 0 / 10`;

    speakMascot("Answers reset. Ready for another try! 🍃", 3000);
  }

})();
