# Step 1 – List of dangerous characters (homoglyphs)
homoglyphs = {
    'а': 'a',  # Cyrillic 'a'
    'е': 'e',  # Cyrillic 'e'
    'ο': 'o',  # Greek 'o'
    'ɡ': 'g',  # Latin script 'g'
    'і': 'i',  # Cyrillic 'i'
}

# Step 2 – Whitelist of safe domains
whitelist = ["google.com", "facebook.com", "microsoft.com", "apple.com"]

# Step 3 – Function to clean the domain
import unicodedata

def normalize_domain(domain):
    # Make text consistent
    domain = unicodedata.normalize('NFKC', domain)
    # Replace bad characters
    for bad, good in homoglyphs.items():
        domain = domain.replace(bad, good)
    return domain

# Step 4 – Function to check if domain is suspicious
import difflib

def is_suspicious(domain):
    fixed = normalize_domain(domain)
    # If exactly in whitelist → safe
    if fixed in whitelist:
        return False
    # If very similar to a whitelist domain → suspicious
    if difflib.get_close_matches(fixed, whitelist, cutoff=0.8):
        return True
    return False

# Step 5 – Test the detector
test_domains = [
    "google.com",      # Safe
    "ɡoogle.com",      # Fake
    "facebοok.com",    # Fake
    "microsoft.com"    # Safe
]

for site in test_domains:
    if is_suspicious(site):
        print(f"[ALERT] {site} is suspicious")
    else:
        print(f"[SAFE] {site} is OK")
