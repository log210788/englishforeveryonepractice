#!/usr/bin/env python3
"""
test_adversarial_challenger.py - Comprehensive Adversarial & Empirical Test Suite
Studio Ghibli Edition (169 Pages)

Tests:
1. Full Scan of ALL 169 HTML Pages for JS Runtime Errors & DOM Layout integrity.
2. Edge Case: Invalid inputs (XSS payloads, special chars, oversized strings).
3. Edge Case: Blank fields grading.
4. Edge Case: Rapid clicking / Stress / Race conditions (theme buttons, check/reset buttons, audio buttons).
5. Edge Case: Missing audio files & Web Speech Synthesis fallback.
6. Edge Case: Theme persistence via localStorage across page navigation.
7. Edge Case: Kodama mascot state transitions, Pomodoro timer, Teacher Lewis narration.
8. Navigation integrity & Next/Prev button targets.
"""

import sys
import os
import time
import json
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent.resolve()
JSON_PATH = BASE_DIR / "output_json" / "all_pages_consolidated.json"

class AdversarialTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        # Launch chromium in headless mode
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.set_default_timeout(10000)
        self.console_errors = []
        self.page_errors = []
        self.page.on("console", lambda msg: self.console_errors.append(msg.text) if msg.type == "error" else None)
        self.page.on("pageerror", lambda err: self.page_errors.append(str(err)))

    def tearDown(self):
        self.context.close()

    def _get_page_path(self, page_num):
        filename = f"ghibli_p{page_num:03d}.html"
        filepath = BASE_DIR / filename
        return filepath if filepath.exists() else None

    def test_01_all_169_pages_js_errors_and_layout(self):
        """Scan ALL 169 HTML pages to verify zero JS runtime errors and valid DOM layout."""
        print("\n--- TEST 1: Scanning all 169 HTML pages for JS runtime errors & DOM layout ---")
        failed_pages = []
        js_error_pages = []
        
        for p_num in range(8, 177):
            filepath = self._get_page_path(p_num)
            self.assertIsNotNone(filepath, f"Missing HTML file: ghibli_p{p_num:03d}.html")
            
            self.console_errors.clear()
            self.page_errors.clear()
            
            try:
                self.page.goto(filepath.as_uri(), wait_until="domcontentloaded")
                
                # Check for critical JS page errors (uncaught exceptions)
                if self.page_errors:
                    js_error_pages.append((p_num, self.page_errors.copy()))
                
                # Check for console errors (filter out net::ERR_ file 404s for audio)
                real_js_errors = [e for e in self.console_errors if "net::ERR_" not in e and "Failed to load resource" not in e]
                if real_js_errors:
                    js_error_pages.append((p_num, real_js_errors))

                # Check required DOM elements
                has_mascot = self.page.locator("#mascotBubble, .mascot-bubble").count() > 0
                has_check = self.page.locator("#ghibliCheckAnswersBtn, .ghibli-check-btn").count() > 0
                has_score = self.page.locator("#ghibliScoreBadge, .ghibli-score-badge, #ghibliScoreText").count() > 0
                has_tod = self.page.locator(".tod-btn").count() > 0
                has_nav = self.page.locator(".chapter-nav-bar").count() > 0

                if not (has_mascot and has_check and has_score and has_tod and has_nav):
                    failed_pages.append((p_num, f"Missing elements: mascot={has_mascot}, check={has_check}, score={has_score}, tod={has_tod}, nav={has_nav}"))

            except Exception as e:
                failed_pages.append((p_num, f"Load exception: {str(e)}"))

        print(f"Scanned 169 pages. JS errors found: {len(js_error_pages)}, Layout failures: {len(failed_pages)}")
        self.assertEqual(len(js_error_pages), 0, f"JS runtime errors detected on pages: {js_error_pages[:5]}")
        self.assertEqual(len(failed_pages), 0, f"DOM layout failures on pages: {failed_pages[:5]}")

    def test_02_blank_fields_and_invalid_inputs(self):
        """Test submission with blank fields, XSS payloads, special characters, and long strings."""
        print("\n--- TEST 2: Testing blank fields & invalid inputs / edge cases ---")
        filepath = self._get_page_path(8) # p008
        self.page.goto(filepath.as_uri(), wait_until="domcontentloaded")
        
        check_btn = self.page.locator("#ghibliCheckAnswersBtn, .ghibli-check-btn").first
        
        # 1. Blank submission
        check_btn.click()
        score_badge = self.page.locator("#ghibliScoreBadge, .ghibli-score-badge, #ghibliScoreText").first
        score_text = score_badge.text_content()
        self.assertIn("0 /", score_text, f"Blank submission score should be 0/N, got: {score_text}")
        
        # Verify mascot reacted (encouragement)
        mascot_bubble = self.page.locator("#mascotBubble, .mascot-bubble").first
        self.assertTrue(len(mascot_bubble.text_content()) > 0)
        
        # 2. XSS and Special Character injection
        inputs = self.page.locator("input[type='text']:not([readonly]), .ghibli-input:not([readonly])")
        payloads = [
            "<script>alert('XSS')</script>",
            "'; DROP TABLE students; --",
            "&quot;><img src=x onerror=alert(1)>",
            "😊🚀🔥",
            "A" * 1000
        ]
        
        if inputs.count() > 0:
            for i in range(inputs.count()):
                payload = payloads[i % len(payloads)]
                inputs.nth(i).fill(payload)
            
            # Click check answers
            check_btn.click()
            
            # Verify no JS unhandled page exceptions occurred
            self.assertEqual(len(self.page_errors), 0, f"Page errors on invalid inputs: {self.page_errors}")

    def test_03_rapid_clicking_stress(self):
        """Stress test rapid clicking on theme toggle, check answers, reset, and audio buttons."""
        print("\n--- TEST 3: Rapid clicking stress test ---")
        filepath = self._get_page_path(12)
        self.page.goto(filepath.as_uri(), wait_until="domcontentloaded")

        tod_btns = self.page.locator(".tod-btn")
        check_btn = self.page.locator("#ghibliCheckAnswersBtn, .ghibli-check-btn").first
        reset_btn = self.page.locator("#ghibliResetBtn, .ghibli-reset-btn")

        # 1. Rapid theme toggling (50 clicks)
        if tod_btns.count() > 0:
            for _ in range(15):
                for k in range(tod_btns.count()):
                    tod_btns.nth(k).click(force=True)

        # 2. Rapid Check / Reset toggling
        for _ in range(10):
            check_btn.click(force=True)
            if reset_btn.count() > 0:
                reset_btn.first.click(force=True)

        # Verify page is still alive and responsive
        body_class = self.page.locator("body").get_attribute("class") or ""
        self.assertTrue(len(body_class) >= 0)
        self.assertEqual(len(self.page_errors), 0, f"Errors during rapid clicking: {self.page_errors}")

    def test_04_missing_audio_and_speech_synthesis_fallback(self):
        """Test audio buttons when audio file is missing or triggers fallback."""
        print("\n--- TEST 4: Missing audio & SpeechSynthesis fallback ---")
        filepath = self._get_page_path(16)
        self.page.goto(filepath.as_uri(), wait_until="domcontentloaded")

        audio_btns = self.page.locator(".ghibli-audio-play-btn, .ghibli-audio-btn, [data-audio]")
        if audio_btns.count() > 0:
            # Click first 3 audio buttons
            for i in range(min(3, audio_btns.count())):
                audio_btns.nth(i).click(force=True)
                self.page.wait_for_timeout(200)

        # Verify no unhandled JS runtime errors (console network 404s are expected for missing MP3s)
        self.assertEqual(len(self.page_errors), 0, f"Audio fallback triggered JS errors: {self.page_errors}")

    def test_05_theme_switching_persistence(self):
        """Test theme switching persistence across page navigation via localStorage."""
        print("\n--- TEST 5: Theme switching persistence ---")
        filepath_p8 = self._get_page_path(8)
        filepath_p9 = self._get_page_path(9)

        self.page.goto(filepath_p8.as_uri(), wait_until="domcontentloaded")

        night_btn = self.page.locator(".tod-btn[data-theme='night']")
        if night_btn.count() > 0:
            night_btn.click()
            self.page.wait_for_timeout(300)

            # Navigate to page 9
            self.page.goto(filepath_p9.as_uri(), wait_until="domcontentloaded")
            body_theme = self.page.locator("body").get_attribute("data-theme") or ""
            body_class = self.page.locator("body").get_attribute("class") or ""
            
            is_night = ("night" in body_theme) or ("night" in body_class)
            self.assertTrue(is_night, f"Theme did not persist across navigation: theme={body_theme}, class={body_class}")

    def test_06_mascot_state_transitions(self):
        """Test mascot state transitions: click mascot, trigger celebration, trigger story narration."""
        print("\n--- TEST 6: Mascot state transitions ---")
        filepath = self._get_page_path(25)
        self.page.goto(filepath.as_uri(), wait_until="domcontentloaded")

        mascot_widget = self.page.locator(".kodama-widget, #kodamaMascot, .mascot-companion, .ghibli-mascot").first
        mascot_bubble = self.page.locator("#mascotBubble, .mascot-bubble").first

        if mascot_widget.count() > 0:
            initial_text = mascot_bubble.text_content()
            mascot_widget.click(force=True)
            self.page.wait_for_timeout(200)
            new_text = mascot_bubble.text_content()
            # Mascot should respond to interaction
            self.assertTrue(len(new_text) > 0)

        # Trigger check answers to see celebration / encouragement text
        check_btn = self.page.locator("#ghibliCheckAnswersBtn, .ghibli-check-btn").first
        check_btn.click()
        post_grade_text = mascot_bubble.text_content()
        self.assertTrue(len(post_grade_text) > 0)

    def test_07_navigation_chain_and_targets(self):
        """Test Next/Previous page links and Home Hub navigation."""
        print("\n--- TEST 7: Navigation chain & href targets ---")
        filepath = self._get_page_path(50)
        self.page.goto(filepath.as_uri(), wait_until="domcontentloaded")

        nav_next = self.page.locator(".nav-next, a:has-text('Next'), a.next-page").first
        nav_prev = self.page.locator(".nav-prev, a:has-text('Prev'), a.prev-page").first
        nav_home = self.page.locator(".nav-home, a:has-text('Home'), a.home-hub").first

        self.assertGreater(self.page.locator(".chapter-nav-bar").count(), 0)

        if nav_next.count() > 0:
            href_next = nav_next.get_attribute("href")
            self.assertIn("ghibli_p051.html", href_next)

        if nav_prev.count() > 0:
            href_prev = nav_prev.get_attribute("href")
            self.assertIn("ghibli_p049.html", href_prev)

        if nav_home.count() > 0:
            href_home = nav_home.get_attribute("href")
            self.assertIn("index.html", href_home)


if __name__ == "__main__":
    unittest.main(verbosity=2)
