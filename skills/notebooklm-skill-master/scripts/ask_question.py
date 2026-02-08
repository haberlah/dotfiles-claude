#!/usr/bin/env python3
"""
Simple NotebookLM Question Interface
Based on MCP server implementation - simplified without sessions

Implements hybrid auth approach:
- Persistent browser profile (user_data_dir) for fingerprint consistency
- Manual cookie injection from state.json for session cookies (Playwright bug workaround)
See: https://github.com/microsoft/playwright/issues/36139
"""

import argparse
import sys
import time
import re
from pathlib import Path

from patchright.sync_api import sync_playwright

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from auth_manager import AuthManager
from notebook_manager import NotebookLibrary
from config import QUERY_INPUT_SELECTORS, RESPONSE_SELECTORS
from browser_utils import BrowserFactory, StealthUtils


# Follow-up reminder (adapted from MCP server for stateless operation)
# Since we don't have persistent sessions, we encourage comprehensive questions
FOLLOW_UP_REMINDER = (
    "\n\nEXTREMELY IMPORTANT: Is that ALL you need to know? "
    "You can always ask another question! Think about it carefully: "
    "before you reply to the user, review their original request and this answer. "
    "If anything is still unclear or missing, ask me another comprehensive question "
    "that includes all necessary context (since each question opens a new browser session)."
)


def ask_notebooklm(question: str, notebook_url: str, headless: bool = True) -> str:
    """
    Ask a question to NotebookLM

    Args:
        question: Question to ask
        notebook_url: NotebookLM notebook URL
        headless: Run browser in headless mode

    Returns:
        Answer text from NotebookLM
    """
    auth = AuthManager()

    if not auth.is_authenticated():
        print("⚠️ Not authenticated. Run: python auth_manager.py setup")
        return None

    print(f"💬 Asking: {question}")
    print(f"📚 Notebook: {notebook_url}")

    playwright = None
    context = None

    try:
        # Start playwright
        playwright = sync_playwright().start()

        # Launch persistent browser context using factory
        context = BrowserFactory.launch_persistent_context(
            playwright,
            headless=headless
        )

        # Navigate to notebook
        page = context.new_page()
        print("  🌐 Opening notebook...")
        page.goto(notebook_url, wait_until="domcontentloaded")

        # Wait for NotebookLM
        page.wait_for_url(re.compile(r"^https://notebooklm\.google\.com/"), timeout=10000)

        # Wait for page to stabilize
        StealthUtils.random_delay(2000, 3000)

        # Select all sources BEFORE querying
        print("  ⏳ Selecting all sources...")
        select_all_clicked = False
        try:
            # Click on "Sources" tab to open the sources panel
            sources_tab = page.locator('[role="tab"]:has-text("Sources")').first
            if sources_tab.is_visible(timeout=5000):
                sources_tab.click()
                print("  ✓ Clicked Sources tab")
                StealthUtils.random_delay(1500, 2500)

                # Check if "Select all sources" checkbox is already checked
                # Only click if it's NOT checked (to avoid toggling off)
                try:
                    # Look for the mat-checkbox and check its state
                    select_all_checkbox = page.locator('.select-checkbox-all-sources-container mat-checkbox').first
                    if select_all_checkbox.is_visible(timeout=3000):
                        # Check if it's already checked by looking for the checked class or attribute
                        is_checked = select_all_checkbox.evaluate('''el => {
                            return el.classList.contains("mat-mdc-checkbox-checked") ||
                                   el.querySelector("input")?.checked === true ||
                                   el.getAttribute("aria-checked") === "true";
                        }''')

                        if is_checked:
                            print("  ✓ 'Select all sources' already checked")
                            select_all_clicked = True
                        else:
                            select_all_checkbox.click()
                            select_all_clicked = True
                            print("  ✓ Clicked 'Select all sources' checkbox")
                            StealthUtils.random_delay(500, 1000)
                except Exception as e:
                    print(f"  ⚠️ mat-checkbox approach failed: {e}")

                # Alternative: check checkbox state via aria-checked or visual indicator
                if not select_all_clicked:
                    try:
                        select_all_row = page.locator('text=Select all sources').first
                        if select_all_row.is_visible(timeout=2000):
                            # Check if there's a checkmark visible (indicating already selected)
                            # Look for sibling checkbox state
                            parent = page.locator('*:has-text("Select all sources")').filter(has=page.locator('mat-checkbox')).first
                            if parent.is_visible(timeout=1000):
                                is_checked = parent.evaluate('''el => {
                                    const cb = el.querySelector("mat-checkbox");
                                    return cb?.classList.contains("mat-mdc-checkbox-checked") || false;
                                }''')
                                if is_checked:
                                    print("  ✓ 'Select all sources' already checked (alt check)")
                                    select_all_clicked = True
                                else:
                                    # Click the checkbox
                                    box = select_all_row.bounding_box()
                                    if box:
                                        page.mouse.click(box['x'] + box['width'] + 50, box['y'] + box['height'] / 2)
                                        select_all_clicked = True
                                        print("  ✓ Clicked checkbox area next to 'Select all sources'")
                                        StealthUtils.random_delay(500, 1000)
                    except:
                        pass

                # Switch back to Chat tab for querying
                chat_tab = page.locator('[role="tab"]:has-text("Chat")').first
                if chat_tab.is_visible(timeout=3000):
                    chat_tab.click()
                    print("  ✓ Switched back to Chat tab")
                    StealthUtils.random_delay(1000, 1500)

        except Exception as e:
            print(f"  ⚠️ Error selecting sources: {e}")

        if not select_all_clicked:
            print("  ⚠️ Could not click 'Select all sources' - continuing with default selection")

        # Wait for query input (MCP approach)
        print("  ⏳ Waiting for query input...")
        query_element = None

        for selector in QUERY_INPUT_SELECTORS:
            try:
                query_element = page.wait_for_selector(
                    selector,
                    timeout=10000,
                    state="visible"  # Only check visibility, not disabled!
                )
                if query_element:
                    print(f"  ✓ Found input: {selector}")
                    break
            except:
                continue

        if not query_element:
            print("  ❌ Could not find query input")
            return None

        # Type question (human-like, fast)
        print("  ⏳ Typing question...")

        # Use primary selector for typing
        input_selector = QUERY_INPUT_SELECTORS[0]
        StealthUtils.human_type(page, input_selector, question)

        # Submit
        print("  📤 Submitting...")
        page.keyboard.press("Enter")

        # Small pause
        StealthUtils.random_delay(500, 1500)

        # Wait for response by monitoring visible page text
        print("  ⏳ Waiting for answer...")

        answer = None
        stable_count = 0
        last_text = None
        deadline = time.time() + 120  # 2 minutes timeout

        while time.time() < deadline:
            try:
                # Get visible page text
                page_text = page.inner_text('body')

                # Find our question in the text, then extract what comes after
                # Use a shorter, unique portion of the question to find it
                question_marker = question[:50]  # First 50 chars as marker
                if question_marker in page_text:
                    # Find where our question ends and response begins
                    q_idx = page_text.find(question_marker)
                    after_question = page_text[q_idx + len(question_marker):]

                    # Look for response pattern (starts with "Based on" or similar)
                    response_patterns = [
                        "Based on the",
                        "According to",
                        "The document",
                        "The sources",
                    ]

                    for pattern in response_patterns:
                        if pattern in after_question:
                            resp_start = after_question.find(pattern)
                            # Extract response until we hit footer/disclaimer
                            response_text = after_question[resp_start:]

                            # Clean up - remove footer text and UI artifacts
                            end_markers = [
                                "\nNotebookLM can be inaccurate",
                                "\nStart typing",
                                "\nkeep_pin",
                                "\nSave to note",
                                "\ncopy_all",
                                "\nthumb_up",
                                "\narrow_forward",
                                "\ndocs\n",
                            ]
                            for marker in end_markers:
                                if marker in response_text:
                                    response_text = response_text[:response_text.find(marker)]

                            # Check if response looks complete (has substantial text)
                            if len(response_text) > 100:
                                if response_text == last_text:
                                    stable_count += 1
                                    if stable_count >= 3:  # Stable for 3 polls
                                        answer = response_text.strip()
                                        break
                                else:
                                    stable_count = 0
                                    last_text = response_text
                            break
            except Exception as e:
                pass

            time.sleep(1)

        if not answer:
            print("  ❌ Timeout waiting for answer")
            return None

        print("  ✅ Got answer!")
        # Add follow-up reminder to encourage Claude to ask more questions
        return answer + FOLLOW_UP_REMINDER

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        # Always clean up
        if context:
            try:
                context.close()
            except:
                pass

        if playwright:
            try:
                playwright.stop()
            except:
                pass


def main():
    parser = argparse.ArgumentParser(description='Ask NotebookLM a question')

    parser.add_argument('--question', required=True, help='Question to ask')
    parser.add_argument('--notebook-url', help='NotebookLM notebook URL')
    parser.add_argument('--notebook-id', help='Notebook ID from library')
    parser.add_argument('--show-browser', action='store_true', help='Show browser')

    args = parser.parse_args()

    # Resolve notebook URL
    notebook_url = args.notebook_url

    if not notebook_url and args.notebook_id:
        library = NotebookLibrary()
        notebook = library.get_notebook(args.notebook_id)
        if notebook:
            notebook_url = notebook['url']
        else:
            print(f"❌ Notebook '{args.notebook_id}' not found")
            return 1

    if not notebook_url:
        # Check for active notebook first
        library = NotebookLibrary()
        active = library.get_active_notebook()
        if active:
            notebook_url = active['url']
            print(f"📚 Using active notebook: {active['name']}")
        else:
            # Show available notebooks
            notebooks = library.list_notebooks()
            if notebooks:
                print("\n📚 Available notebooks:")
                for nb in notebooks:
                    mark = " [ACTIVE]" if nb.get('id') == library.active_notebook_id else ""
                    print(f"  {nb['id']}: {nb['name']}{mark}")
                print("\nSpecify with --notebook-id or set active:")
                print("python scripts/run.py notebook_manager.py activate --id ID")
            else:
                print("❌ No notebooks in library. Add one first:")
                print("python scripts/run.py notebook_manager.py add --url URL --name NAME --description DESC --topics TOPICS")
            return 1

    # Ask the question
    answer = ask_notebooklm(
        question=args.question,
        notebook_url=notebook_url,
        headless=not args.show_browser
    )

    if answer:
        print("\n" + "=" * 60)
        print(f"Question: {args.question}")
        print("=" * 60)
        print()
        print(answer)
        print()
        print("=" * 60)
        return 0
    else:
        print("\n❌ Failed to get answer")
        return 1


if __name__ == "__main__":
    sys.exit(main())
