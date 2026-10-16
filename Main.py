import os
from functions.importExport import (
    export_interactive, 
    export_from_browser, 
    import_to_browser, 
    import_to_requests
)

CACHE_DIR = "cache"

def get_cache_files():
    """Return all json files in cache directory."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)
        return []
    return [f for f in os.listdir(CACHE_DIR) if f.endswith(".json")]

def select_cache_file():
    """Interactive cache file selector."""
    files = get_cache_files()
    if not files:
        name = input("Enter new filename (e.g. cookies.json): ").strip()
        return name if name.endswith(".json") else name + ".json"

    print("\nCached files:")
    for i, file in enumerate(files, 1):
        print(f"  {i} - {file}")
    print("  0 - Custom filename")
    
    choice = input("Select: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(files):
        return files[int(choice) - 1]
            
    name = input("Enter filename: ").strip()
    return name if name.endswith(".json") else name + ".json"

def main():
    while True:
        print("\n--- COOKIE MANAGER ---")
        print("1 - Export: Interactive login")
        print("2 - Export: From browser profile")
        print("3 - Import: To browser")
        print("4 - Import: To requests session")
        print("0 - Exit")
        
        choice = input("Choice: ").strip()
        
        if choice == "1":
            url = input("URL: ").strip() or "https://youtube.com"
            if not url.startswith("http"): url = "https://" + url
            export_interactive(target_url=url, filename=select_cache_file())
            
        elif choice == "2":
            domain = input("Domain (.youtube.com): ").strip() or ".youtube.com"
            browser = input("Browser (chrome/firefox/edge) [chrome]: ").strip() or "chrome"
            export_from_browser(domain_name=domain, filename=select_cache_file(), browser_type=browser)
            
        elif choice == "3":
            url = input("URL: ").strip() or "https://youtube.com"
            if not url.startswith("http"): url = "https://" + url
            import_to_browser(target_url=url, filename=select_cache_file())

        elif choice == "4":
            session = import_to_requests(filename=select_cache_file())
            if session:
                test_url = input("Test GET URL (blank to skip): ").strip()
                if test_url:
                    if not test_url.startswith("http"): test_url = "https://" + test_url
                    try:
                        res = session.get(test_url)
                        print(f"Status: {res.status_code} | Preview: {res.text[:150]}")
                    except Exception as e:
                        print(f"Error: {e}")
                        
        elif choice == "0":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()