/* ==========================================================================
   Teacher Lewis's Practice Book - Studio Ghibli Edition
   Landing Page JavaScript Engine (index.js)
   ========================================================================== */

(function () {
  'use strict';

  // --- STICKERS DATABASE ---
  const STICKERS_DATA = [
    {
      id: 'sticker-1',
      chapter: 'Unit 1 100%',
      name: "Traveler's Backpack",
      icon: '🎒',
      image: 'images/ghibli/backpack_sticker.svg',
      description: "Teacher Lewis's handcrafted adventure backpack. Unlocked when Unit 1 is 100% complete!",
      lore: "Awarded for achieving a 100% perfect score (11/11) on Unit 1 (Introducing Yourself) with Teacher Lewis!",
      defaultUnlocked: false // Unlocked after Unit 1 is 100% complete!
    },
    {
      id: 'sticker-2',
      chapter: 'Unit 1',
      name: 'Spirit Name Tag',
      icon: '🏷️',
      description: 'A magical wooden tag engraved with your name by the forest spirits.',
      lore: 'Earned by introducing yourself and practicing contracted verb forms in Chapter 1 with Teacher Lewis.',
      defaultUnlocked: false
    },
    {
      id: 'sticker-3',
      chapter: 'Unit 2',
      name: 'Cozy Teapot',
      icon: '☕',
      description: 'A steaming teapot for relaxed conversations in the forest library.',
      lore: 'Awarded when mastering greetings and daily hobbies with Teacher Lewis.',
      defaultUnlocked: false
    },
    {
      id: 'sticker-4',
      chapter: 'Unit 3',
      name: 'Grammar Scroll',
      icon: '📜',
      description: 'An ancient scroll detailing the secrets of clear English sentence structures.',
      lore: 'Unlocked upon completing advanced grammar practice with Teacher Lewis.',
      defaultUnlocked: false
    },
    {
      id: 'sticker-5',
      chapter: 'Unit 4',
      name: 'Forest Express Ticket',
      icon: '🚂',
      description: 'A golden ticket to ride the forest train through new vocabulary towns.',
      lore: 'Earned by navigating vocabulary and listening exercises flawlessly.',
      defaultUnlocked: false
    },
    {
      id: 'sticker-6',
      chapter: 'Unit 5',
      name: 'Starry Sky Compass',
      icon: '🌟',
      description: 'A sparkling compass that guides you through tricky pronunciation.',
      lore: 'Granted for completing full listening comprehension sessions.',
      defaultUnlocked: false
    },
    {
      id: 'sticker-7',
      chapter: 'Unit 6',
      name: 'Cottage Key',
      icon: '🏡',
      description: 'The brass key to Teacher Lewis\'s cozy study cottage in the woods.',
      lore: 'Unlocked upon demonstrating fluent everyday conversation skills.',
      defaultUnlocked: false
    },
    {
      id: 'sticker-8',
      chapter: 'Mastery',
      name: 'Teacher Lewis Laurel',
      icon: '🏆',
      description: 'A shining golden laurel leaf crown of English mastery.',
      lore: 'The ultimate distinction awarded for completing Teacher Lewis\'s entire practice book!',
      defaultUnlocked: false
    }
  ];

  // --- AUDIO SYNTHESIZER ENGINE (Web Audio API) ---
  class SoundEngine {
    constructor() {
      this.ctx = null;
      this.isMuted = true;
      this.ambientTimer = null;
    }

    init() {
      if (!this.ctx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
          this.ctx = new AudioContext();
        }
      }
      if (this.ctx && this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
    }

    playChime(freqs = [523.25, 659.25, 783.99, 1046.50]) {
      if (window.GhibliAudio) {
        window.GhibliAudio.playChime(freqs);
      }
    }

    playClick() {
      if (window.GhibliAudio) {
        window.GhibliAudio.playClick();
      }
    }

    playStickerUnlockSound() {
      if (window.GhibliAudio) {
        window.GhibliAudio.playFanfare();
      }
    }

    toggleAmbient(btnElement) {
      if (window.GhibliAudio && window.GhibliAudio.toggleBGM) {
        window.GhibliAudio.toggleBGM(btnElement);
      }
    }

    startAmbientLoop() {
      if (this.ambientTimer) clearInterval(this.ambientTimer);
      // Gentle random Ghibli pentatonic background notes every 4s
      const pentatonic = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25];
      this.ambientTimer = setInterval(() => {
        if (this.isMuted || !this.ctx) return;
        const note = pentatonic[Math.floor(Math.random() * pentatonic.length)];
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(note, this.ctx.currentTime);

        gain.gain.setValueAtTime(0.001, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.08, this.ctx.currentTime + 0.5);
        gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + 3.2);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + 3.3);
      }, 3500);
    }
  }

  const soundFX = new SoundEngine();

  // --- STATE MANAGER (LocalStorage) ---
  const StorageManager = {
    STUDENT_KEY: 'teacher_lewis_student_name',
    INVENTORY_KEY: 'teacher_lewis_inventory',

    getStudentName() {
      return localStorage.getItem(this.STUDENT_KEY) || '';
    },

    setStudentName(name) {
      const cleanName = name.trim();
      if (cleanName) {
        localStorage.setItem(this.STUDENT_KEY, cleanName);
      }
      return cleanName;
    },

    getInventory() {
      const saved = localStorage.getItem(this.INVENTORY_KEY);
      if (saved) {
        try { return JSON.parse(saved); } catch (e) { }
      }
      // Initial default state: Sticker 1 (Backpack) is unlocked!
      const initial = {};
      STICKERS_DATA.forEach(s => {
        initial[s.id] = s.defaultUnlocked;
      });
      this.saveInventory(initial);
      return initial;
    },

    saveInventory(invObj) {
      localStorage.setItem(this.INVENTORY_KEY, JSON.stringify(invObj));
    },

    unlockSticker(stickerId) {
      const inv = this.getInventory();
      if (!inv[stickerId]) {
        inv[stickerId] = true;
        this.saveInventory(inv);
        return true; // Newly unlocked!
      }
      return false;
    }
  };

  // --- PARTICLES ENGINE ---
  function initParticles(theme = 'day') {
    const container = document.getElementById('particlesContainer');
    if (!container) return;
    container.innerHTML = '';

    if (theme === 'night') {
      for (let i = 0; i < 22; i++) {
        const firefly = document.createElement('div');
        firefly.className = 'firefly';
        firefly.style.left = Math.random() * 100 + 'vw';
        firefly.style.top = Math.random() * 100 + 'vh';
        firefly.style.animationDelay = (Math.random() * 5) + 's';
        firefly.style.animationDuration = (4 + Math.random() * 5) + 's';
        container.appendChild(firefly);
      }
    } else if (theme === 'day') {
      for (let i = 0; i < 10; i++) {
        const leaf = document.createElement('div');
        leaf.className = 'leaf-particle';
        leaf.style.left = Math.random() * 100 + 'vw';
        leaf.style.animationDelay = (Math.random() * 8) + 's';
        leaf.style.animationDuration = (8 + Math.random() * 6) + 's';
        container.appendChild(leaf);
      }
    }
  }

  // --- UI CONTROLLER & MASCOT INTERACTION ---
  document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const body = document.body;
    const mascotImg = document.getElementById('mascotAvatarImg');
    const mascotBubble = document.getElementById('mascotBubble');
    const mascotPrompt = document.getElementById('mascotNamePrompt');
    const studentNameInput = document.getElementById('studentNameInput');
    const saveNameBtn = document.getElementById('saveNameBtn');
    const studentBadgePill = document.getElementById('studentBadgePill');
    const studentNameDisplay = document.getElementById('studentNameDisplay');

    // Inventory Modal Elements
    const openInventoryBtn = document.getElementById('openInventoryBtn');
    const closeInventoryBtn = document.getElementById('closeInventoryBtn');
    const inventoryModal = document.getElementById('inventoryModal');
    const stickerGrid = document.getElementById('stickerGrid');
    const stickerProgressText = document.getElementById('stickerProgressText');
    const stickerProgressBar = document.getElementById('stickerProgressBar');
    const unlockToast = document.getElementById('unlockToast');
    const unlockToastIcon = document.getElementById('unlockToastIcon');
    const unlockToastTitle = document.getElementById('unlockToastTitle');
    const unlockToastDesc = document.getElementById('unlockToastDesc');

    // Time-of-Day theme selector
    const todButtons = document.querySelectorAll('.tod-btn');
    const toggleAmbientBtn = document.getElementById('toggleAmbientBtn');

    // Init Theme & Particles
    todButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        soundFX.playClick();
        todButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const theme = btn.dataset.theme;
        body.className = `theme-${theme}`;
        initParticles(theme);
      });
    });
    initParticles('day');

    if (toggleAmbientBtn) {
      toggleAmbientBtn.addEventListener('click', () => soundFX.toggleAmbient(toggleAmbientBtn));
    }

    // First Visit Overlay Elements
    const firstVisitOverlay = document.getElementById('firstVisitOverlay');
    const firstVisitMascotImg = document.getElementById('firstVisitMascotImg');
    const firstVisitBubble = document.getElementById('firstVisitBubble');
    const firstVisitNameInput = document.getElementById('firstVisitNameInput');
    const firstVisitSaveBtn = document.getElementById('firstVisitSaveBtn');

    // Initialize Student Name & Mascot Greeting
    let currentStudentName = StorageManager.getStudentName();

    function updateStudentBadgeUI() {
      if (currentStudentName) {
        studentNameDisplay.textContent = currentStudentName;
        studentBadgePill.style.display = 'flex';
      } else {
        studentNameDisplay.textContent = 'Guest Traveler';
        studentBadgePill.style.display = 'flex';
      }
    }

    function renderMascotState() {
      updateStudentBadgeUI();

      if (!currentStudentName) {
        // FIRST VISIT: Dedicated Full-Screen Mascot Greeting Overlay is ACTIVE!
        if (firstVisitOverlay) firstVisitOverlay.classList.remove('hidden');
        if (firstVisitNameInput) setTimeout(() => firstVisitNameInput.focus(), 400);

        // Sidebar card state (if elements exist)
        if (mascotImg) mascotImg.src = 'images/ghibli/mascot.jpg';
        if (mascotBubble) mascotBubble.innerHTML = `Konnichiwa! 🌿 Welcome to <strong>Teacher Lewis's Practice Book</strong>! May I ask what your name is?`;
        if (mascotPrompt) mascotPrompt.style.display = 'flex';
      } else {
        // RETURNING VISIT: Hide overlay, show hub!
        if (firstVisitOverlay) firstVisitOverlay.classList.add('hidden');

        // Sidebar card state (if elements exist)
        if (mascotImg) mascotImg.src = 'images/ghibli/mascot_talking.jpg';
        if (mascotBubble) mascotBubble.innerHTML = `Welcome back, <strong>${currentStudentName}</strong>! 🎒✨ Teacher Lewis has prepared your next English practice module. Ready to collect more stickers?`;
        if (mascotPrompt) mascotPrompt.style.display = 'none';
      }
    }

    renderMascotState();

    // First Visit Overlay Name Submission Handler
    function handleFirstVisitSubmission() {
      const inputVal = (firstVisitNameInput && firstVisitNameInput.value.trim()) || (studentNameInput && studentNameInput.value.trim());
      if (!inputVal) {
        if (firstVisitNameInput) firstVisitNameInput.focus();
        else if (studentNameInput) studentNameInput.focus();
        return;
      }

      soundFX.playClick();
      currentStudentName = StorageManager.setStudentName(inputVal);

      // Mascot Reaction on Overlay
      if (firstVisitMascotImg) firstVisitMascotImg.src = 'images/ghibli/mascot_talking.jpg';
      if (firstVisitBubble) {
        firstVisitBubble.innerHTML = `It's a wonderful pleasure to meet you, <strong>${currentStudentName}</strong>! Complete <strong>Unit 1</strong> with a 100% score to unlock your <img src="images/ghibli/backpack_sticker.svg" class="inline-backpack-img" alt="Backpack"> <strong>Traveler's Backpack</strong> sticker! Welcome to Teacher Lewis's Academy!`;
      }
      
      const formContainer = document.getElementById('firstVisitForm');
      if (formContainer) formContainer.style.display = 'none';

      // Also update sidebar mascot card if present
      if (mascotImg) mascotImg.src = 'images/ghibli/mascot_talking.jpg';
      if (mascotBubble) mascotBubble.innerHTML = `Welcome, <strong>${currentStudentName}</strong>! Score 100% on Unit 1 to earn your Traveler's Backpack sticker!`;
      if (mascotPrompt) mascotPrompt.style.display = 'none';

      updateStudentBadgeUI();

      renderInventory();
      soundFX.playChime([440, 554.37, 659.25]);

      // Transition: Fade out overlay after short pause to reveal full hub!
      setTimeout(() => {
        if (firstVisitOverlay) firstVisitOverlay.classList.add('hidden');
      }, 2000);
    }

    if (firstVisitSaveBtn) firstVisitSaveBtn.addEventListener('click', handleFirstVisitSubmission);
    if (firstVisitNameInput) {
      firstVisitNameInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleFirstVisitSubmission();
      });
    }

    if (saveNameBtn) saveNameBtn.addEventListener('click', handleFirstVisitSubmission);
    if (studentNameInput) {
      studentNameInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleFirstVisitSubmission();
      });
    }

    // Clicking student badge pill in header re-opens mascot overlay to edit name!
    if (studentBadgePill) {
      studentBadgePill.addEventListener('click', () => {
        soundFX.playClick();
        if (firstVisitOverlay) {
          if (firstVisitMascotImg) firstVisitMascotImg.src = 'images/ghibli/mascot_focused.jpg';
          if (firstVisitBubble) {
            firstVisitBubble.innerHTML = `Would you like to change your traveler name, <strong>${currentStudentName}</strong>? Enter your new name below:`;
          }
          const formContainer = document.getElementById('firstVisitForm');
          if (formContainer) formContainer.style.display = 'flex';
          if (firstVisitNameInput) {
            firstVisitNameInput.value = currentStudentName;
            setTimeout(() => firstVisitNameInput.focus(), 200);
          }
          firstVisitOverlay.classList.remove('hidden');
        }
      });
    }

    const globalHoverTooltip = document.getElementById('globalHoverTooltip');
    const inspectorIconPreview = document.getElementById('inspectorIconPreview');
    const inspectorTitle = document.getElementById('inspectorTitle');
    const inspectorDesc = document.getElementById('inspectorDesc');
    const inspectorLore = document.getElementById('inspectorLore');

    function updateInspectorCard(sticker, isUnlocked) {
      if (!inspectorTitle || !inspectorDesc) return;

      if (isUnlocked && sticker) {
        if (inspectorIconPreview) {
          inspectorIconPreview.innerHTML = sticker.image
            ? `<img src="${sticker.image}" alt="${sticker.name}" style="width: 36px; height: 36px; object-fit: contain;">`
            : sticker.icon;
        }
        inspectorTitle.textContent = `${sticker.name} (${sticker.chapter})`;
        inspectorDesc.textContent = sticker.description;
        if (inspectorLore) {
          inspectorLore.style.display = 'block';
          inspectorLore.textContent = `Teacher Lewis: "${sticker.lore}"`;
        }
      } else {
        if (inspectorIconPreview) {
          inspectorIconPreview.innerHTML = `<i class="fa-solid fa-feather-pointed" style="color: var(--ghibli-gold);"></i>`;
        }
        inspectorTitle.textContent = `Teacher Lewis Item Inspector`;
        inspectorDesc.textContent = `Hover over any unlocked sticker in your book to reveal Teacher Lewis's item details & lore!`;
        if (inspectorLore) inspectorLore.style.display = 'none';
      }
    }

    function showGlobalTooltip(e, sticker, isUnlocked) {
      if (!isUnlocked || !globalHoverTooltip) return;

      const tooltipIcon = sticker.image
        ? `<img src="${sticker.image}" style="width:20px;height:20px;object-fit:contain;">`
        : sticker.icon;

      globalHoverTooltip.innerHTML = `
        <div class="tooltip-item-title">${tooltipIcon} ${sticker.name}</div>
        <div class="tooltip-item-desc">${sticker.description}</div>
        <div class="tooltip-item-lore">Teacher Lewis: "${sticker.lore}"</div>
      `;

      const rect = e.currentTarget.getBoundingClientRect();
      let leftPos = rect.left + rect.width / 2 - 135;
      let topPos = rect.bottom + 12;

      // Flip upwards if near bottom of viewport
      if (topPos + 150 > window.innerHeight) {
        topPos = rect.top - 140;
      }
      leftPos = Math.max(12, Math.min(window.innerWidth - 282, leftPos));

      globalHoverTooltip.style.left = `${leftPos}px`;
      globalHoverTooltip.style.top = `${topPos}px`;
      globalHoverTooltip.classList.add('visible');
    }

    function hideGlobalTooltip() {
      if (globalHoverTooltip) globalHoverTooltip.classList.remove('visible');
    }

    // --- INVENTORY STICKER RENDERER ---
    function renderInventory() {
      const inventory = StorageManager.getInventory();
      if (!stickerGrid) return;
      stickerGrid.innerHTML = '';
      updateInspectorCard(null, false);

      let unlockedCount = 0;
      const totalStickers = STICKERS_DATA.length;

      STICKERS_DATA.forEach(sticker => {
        const isUnlocked = !!inventory[sticker.id];
        if (isUnlocked) unlockedCount++;

        const card = document.createElement('div');
        card.className = `sticker-card ${isUnlocked ? 'unlocked' : 'locked'}`;

        const iconContent = (isUnlocked && sticker.image) 
          ? `<img src="${sticker.image}" alt="${sticker.name}" style="width: 54px; height: 54px; object-fit: contain; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.15));">`
          : (isUnlocked ? sticker.icon : '🔒');

        card.innerHTML = `
          <div class="sticker-badge-tag">${sticker.chapter}</div>
          <div class="sticker-icon-wrap">${iconContent}</div>
          <div class="sticker-name">${sticker.name}</div>
          <div class="sticker-chapter-label">${isUnlocked ? 'Unlocked!' : 'Locked'}</div>
        `;

        if (isUnlocked) {
          card.addEventListener('mouseenter', (e) => {
            updateInspectorCard(sticker, true);
            showGlobalTooltip(e, sticker, true);
          });
          card.addEventListener('mouseleave', () => {
            hideGlobalTooltip();
          });
        }

        card.addEventListener('click', () => {
          soundFX.playClick();
          if (isUnlocked) {
            alert(`🎒 STICKER DETAILS:\n\nName: ${sticker.name} (${sticker.icon})\nChapter: ${sticker.chapter}\n\nDescription: ${sticker.description}\n\nTeacher Lewis Lore: ${sticker.lore}`);
          } else {
            alert(`🔒 LOCKED STICKER:\n\nName: ${sticker.name}\nHow to Unlock: Complete exercises in ${sticker.chapter} with Teacher Lewis to earn this sticker!`);
          }
        });

        stickerGrid.appendChild(card);
      });

      // Update progress bar
      const pct = Math.round((unlockedCount / totalStickers) * 100);
      stickerProgressText.textContent = `${unlockedCount} / ${totalStickers} Collected (${pct}%)`;
      stickerProgressBar.style.width = `${pct}%`;

      // Update navbar backpack badge button
      const navCountBadge = document.getElementById('backpackCountBadge');
      if (navCountBadge) {
        navCountBadge.textContent = `${unlockedCount}/${totalStickers}`;
      }
    }

    // Toast Popup for unlocking stickers
    function triggerStickerUnlockToast(stickerId) {
      const sticker = STICKERS_DATA.find(s => s.id === stickerId);
      if (!sticker) return;

      if (sticker.image) {
        unlockToastIcon.innerHTML = `<img src="${sticker.image}" alt="${sticker.name}" style="width: 52px; height: 52px; object-fit: contain;">`;
      } else {
        unlockToastIcon.textContent = sticker.icon;
      }
      unlockToastTitle.textContent = `New Sticker Unlocked!`;
      unlockToastDesc.textContent = `${sticker.name} - ${sticker.description}`;

      unlockToast.classList.add('show');
      soundFX.playStickerUnlockSound();

      setTimeout(() => {
        unlockToast.classList.remove('show');
      }, 5000);
    }

    // Modal Open & Close Functions
    function openBackpackModal() {
      soundFX.playClick();
      renderInventory();
      if (inventoryModal) {
        inventoryModal.classList.add('active');
        inventoryModal.style.display = 'flex';
        inventoryModal.style.opacity = '1';
        inventoryModal.style.pointerEvents = 'auto';
      }
    }

    function closeBackpackModal() {
      soundFX.playClick();
      if (inventoryModal) {
        inventoryModal.classList.remove('active');
        inventoryModal.style.opacity = '0';
        inventoryModal.style.pointerEvents = 'none';
        setTimeout(() => {
          if (!inventoryModal.classList.contains('active')) {
            inventoryModal.style.display = 'none';
          }
        }, 350);
      }
    }

    if (openInventoryBtn) openInventoryBtn.addEventListener('click', openBackpackModal);

    const bigStickerBookCard = document.getElementById('bigStickerBookCard');
    if (bigStickerBookCard) bigStickerBookCard.addEventListener('click', openBackpackModal);

    document.querySelectorAll('.sticker-book-open-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        openBackpackModal();
      });
    });

    if (closeInventoryBtn) closeInventoryBtn.addEventListener('click', closeBackpackModal);

    if (inventoryModal) {
      inventoryModal.addEventListener('click', (e) => {
        if (e.target === inventoryModal) {
          closeBackpackModal();
        }
      });
    }

    // Expose global helper to allow chapter modules to unlock stickers
    window.TeacherLewisAPI = {
      unlockSticker: (id) => {
        const isNew = StorageManager.unlockSticker(id);
        if (isNew) {
          triggerStickerUnlockToast(id);
          renderInventory();
        }
      },
      getStudentName: () => StorageManager.getStudentName()
    };

    // Render initial inventory badge state
    renderInventory();
  });
})();
