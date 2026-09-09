import glob
import re

for f in glob.glob('templates/*.html'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    new_content = re.sub(r'href="#"\s+class="nav-item"(?:\s+id="[^"]*")?>\s*<i\s+class="fa-solid fa-gear"></i>\s*Settings', 'href="/settings" class="nav-item"><i class="fa-solid fa-gear"></i> Settings', content)
    
    if new_content != content:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Updated {f}")
