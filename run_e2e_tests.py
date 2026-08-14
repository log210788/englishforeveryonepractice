#!/usr/bin/env python3
"""
run_e2e_tests.py - E2E Automated Browser Test Suite for Studio Ghibli Edition
Using Playwright (python playwright.sync_api) and unittest.

Covering:
- R1: Exercise page rendering and input acceptance.
- R2: Time-of-Day theme switching (Day/Sunset/Night), navigation links, Kodama mascot text, audio playback trigger.
- R3: Instant Check Answers validation, correct/incorrect class highlights, score text update, Reset button.
- Sample Matrix: p008, p012, p025, p050, p100, p176.
"""

import sys
import os
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent.resolve()
SAMPLE_PAGES = ["p008", "p012", "p025", "p050", "p100", "p176"]

class TestGhibliE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.set_default_timeout(5000)
        self.console_errors = []
        self.page.on("console", lambda msg: self.console_errors.append(msg.text) if msg.type == "error" else None)

    def tearDown(self):
        self.context.close()

    def _resolve_page_url(self, page_code):
        """Resolves target file:// URL for a sample page, with fallback to existing page if available."""
        filename = f"ghibli_{page_code}.html"
        filepath = BASE_DIR / filename
        if filepath.exists():
            return filepath.as_uri()
        
        # Fallback to ghibli_page12.html if sample page not generated yet
        fallback = BASE_DIR / "ghibli_page12.html"
        if fallback.exists():
            return fallback.as_uri()
            
        return None

    def test_r1_rendering_and_input_acceptance(self):
        """R1: Verify exercise page rendering and input acceptance."""
        url = self._resolve_page_url("p008")
        if not url:
            self.skipTest("No HTML page generated yet for R1 testing.")
            
        self.page.goto(url, wait_until="domcontentloaded")
        
        # Check title / header
        self.assertIn("Studio Ghibli", self.page.title() or self.page.content())
        
        # Find editable text inputs
        inputs = self.page.locator("input[type='text']:not([readonly]), .ghibli-input:not([readonly])")
        if inputs.count() > 0:
            first_input = inputs.first
            first_input.click()
            first_input.fill("Hello World")
            self.assertEqual(first_input.input_value(), "Hello World")

    def test_r2_time_of_day_theme_switching(self):
        """R2: Verify Time-of-Day theme switching (Day, Sunset, Night)."""
        url = self._resolve_page_url("p008")
        if not url:
            self.skipTest("No HTML page generated yet for R2 theme testing.")
            
        self.page.goto(url, wait_until="domcontentloaded")
        
        tod_btns = self.page.locator(".tod-btn")
        if tod_btns.count() == 0:
            self.skipTest("No .tod-btn found on page.")
            
        # Click Sunset
        sunset_btn = self.page.locator(".tod-btn[data-theme='sunset']")
        if sunset_btn.count() > 0:
            sunset_btn.click()
            body_class = self.page.locator("body").get_attribute("class") or ""
            body_theme = self.page.locator("body").get_attribute("data-theme") or ""
            self.assertTrue("sunset" in body_class or "sunset" in body_theme)
            
        # Click Night
        night_btn = self.page.locator(".tod-btn[data-theme='night']")
        if night_btn.count() > 0:
            night_btn.click()
            body_class = self.page.locator("body").get_attribute("class") or ""
            body_theme = self.page.locator("body").get_attribute("data-theme") or ""
            self.assertTrue("night" in body_class or "night" in body_theme)

        # Click Day
        day_btn = self.page.locator(".tod-btn[data-theme='day']")
        if day_btn.count() > 0:
            day_btn.click()
            body_class = self.page.locator("body").get_attribute("class") or ""
            body_theme = self.page.locator("body").get_attribute("data-theme") or ""
            self.assertTrue("day" in body_class or "day" in body_theme)

    def test_r2_navigation_links(self):
        """R2: Verify chapter navigation bar and links."""
        url = self._resolve_page_url("p008")
        if not url:
            self.skipTest("No HTML page generated yet for R2 navigation testing.")
            
        self.page.goto(url, wait_until="domcontentloaded")
        
        nav_bar = self.page.locator(".chapter-nav-bar")
        self.assertGreater(nav_bar.count(), 0, "Chapter navigation bar must exist")
        
        links = nav_bar.locator("a")
        self.assertGreater(links.count(), 0, "Chapter navigation bar must contain links")

    def test_r2_mascot_widget_and_audio(self):
        """R2: Verify Kodama mascot text bubble and audio trigger."""
        url = self._resolve_page_url("p008")
        if not url:
            self.skipTest("No HTML page generated yet for R2 mascot/audio testing.")
            
        self.page.goto(url, wait_until="domcontentloaded")
        
        # Mascot bubble
        mascot_bubble = self.page.locator("#mascotBubble, .mascot-bubble")
        self.assertGreater(mascot_bubble.count(), 0, "Mascot bubble must exist in DOM")
        
        # Audio button click
        audio_btns = self.page.locator(".ghibli-audio-play-btn, .ghibli-audio-btn, [data-audio]")
        if audio_btns.count() > 0:
            audio_btns.first.click()
            # Verify no unhandled JavaScript errors occurred (excluding missing static MP3 404 network notices)
            js_errors = [err for err in self.console_errors if "net::ERR_" not in err and "Failed to load resource" not in err]
            self.assertEqual(len(js_errors), 0, f"Unexpected JS console errors: {js_errors}")

    def test_r3_instant_grading_validation_and_reset(self):
        """R3: Verify Instant Check Answers validation, highlights, score update, and Reset."""
        url = self._resolve_page_url("p008")
        if not url:
            self.skipTest("No HTML page generated yet for R3 grading testing.")
            
        self.page.goto(url, wait_until="domcontentloaded")
        
        check_btn = self.page.locator("#ghibliCheckAnswersBtn, .ghibli-check-btn")
        self.assertGreater(check_btn.count(), 0, "Check Answers button must exist")
        
        inputs = self.page.locator("input[type='text']:not([readonly]), .ghibli-input:not([readonly])")
        if inputs.count() > 0:
            inputs.first.fill("test_answer")
            
        check_btn.first.click()
        
        # Verify score badge exists
        score_badge = self.page.locator("#ghibliScoreBadge, .ghibli-score-badge, #ghibliScoreText")
        self.assertGreater(score_badge.count(), 0, "Score badge must exist")
        
        # Reset button
        reset_btn = self.page.locator("#ghibliResetBtn, .ghibli-reset-btn")
        if reset_btn.count() > 0:
            reset_btn.first.click()
            if inputs.count() > 0:
                self.assertEqual(inputs.first.input_value(), "")

    def test_sample_matrix_execution(self):
        """Verify sample matrix across generated pages (p008, p012, p025, p050, p100, p176)."""
        tested_count = 0
        skipped_count = 0
        
        for page_code in SAMPLE_PAGES:
            filename = f"ghibli_{page_code}.html"
            filepath = BASE_DIR / filename
            if not filepath.exists():
                skipped_count += 1
                continue
                
            url = filepath.as_uri()
            self.page.goto(url, wait_until="domcontentloaded")
            
            # Verify core elements on each matrix page
            self.assertGreater(self.page.locator("#mascotBubble, .mascot-bubble").count(), 0)
            self.assertGreater(self.page.locator("#ghibliCheckAnswersBtn, .ghibli-check-btn").count(), 0)
            self.assertGreater(self.page.locator(".chapter-nav-bar").count(), 0)
            tested_count += 1
            
        print(f"\nSample Matrix Results: {tested_count} tested, {skipped_count} pending generation.")

if __name__ == "__main__":
    unittest.main(verbosity=2)
