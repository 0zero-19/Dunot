import os
import json
import requests
import browser_cookie3
from playwright.sync_api import sync_playwright

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def export_interactive(target_url="https://example.com", filename="cookies_interactive.json"):
    """Export cookies via Playwright interactive login."""
    output_path = os.path.join(CACHE_DIR, filename)
    print(f"\n[Export] Opening browser: {target_url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--disable-infobars"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto(target_url)

        input("Log in, then press Enter here to save cookies: ")
        cookies = context.cookies()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=4)

        print(f"Saved {len(cookies)} cookies to '{output_path}'")
        browser.close()


def export_from_browser(domain_name=".example.com", filename="cookies_profile.json", browser_type="chrome"):
    """Export cookies directly from browser profile storage."""
    output_path = os.path.join(CACHE_DIR, filename)
    print(f"\n[Export] Reading {browser_type} profile for {domain_name}...")
    
    try:
        if browser_type.lower() == "firefox":
            cj = browser_cookie3.firefox(domain_name=domain_name)
        elif browser_type.lower() == "edge":
            cj = browser_cookie3.edge(domain_name=domain_name)
        else:
            cj = browser_cookie3.chrome(domain_name=domain_name)
    except Exception as e:
        print(f"Error (is browser open?): {e}")
        return

    cookies_list = []
    for cookie in cj:
        cookies_list.append({
            "domain": cookie.domain,
            "name": cookie.name,
            "value": cookie.value,
            "path": cookie.path,
            "expires": cookie.expires,
            "secure": cookie.secure,
            "httpOnly": cookie.has_nonstandard_attr('HttpOnly') if hasattr(cookie, 'has_nonstandard_attr') else False
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cookies_list, f, ensure_ascii=False, indent=4)

    print(f"Saved {len(cookies_list)} cookies to '{output_path}'")


def import_to_browser(target_url="https://example.com", filename="cookies_interactive.json"):
    """Import cookies into a new Playwright browser session."""
    file_path = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        cookies = json.load(f)

    print(f"\n[Import] Injecting cookies into {target_url}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(target_url)
        context.add_cookies(cookies)
        page.reload()

        input("Press Enter to close browser: ")
        browser.close()


def import_to_requests(filename="cookies_interactive.json"):
    """Import cookies into a requests.Session object."""
    file_path = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        cookies_list = json.load(f)

    session = requests.Session()
    for cookie in cookies_list:
        session.cookies.set(
            name=cookie['name'],
            value=cookie['value'],
            domain=cookie.get('domain'),
            path=cookie.get('path', '/')
        )

    print(f"Loaded {len(cookies_list)} cookies into requests session.")
    return session