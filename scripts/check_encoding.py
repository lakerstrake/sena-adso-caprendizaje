import os

mojibake_patterns = ['Ã¡', 'Ã©', 'Ã­', 'Ã³', 'Ãº', 'Ã±', 'Â·', 'Ã\x81', 'Ã\x89', 'Ã\x8d', 'Ã\x93', 'Ã\x9a', 'Ã\x91', 'ðŸ', 'â€', 'âœ', 'â˜']

for root, dirs, files in os.walk('output'):
    for file in files:
        if file.endswith(('.html', '.js', '.css', '.json')):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            found = [p for p in mojibake_patterns if p in content]
            if found:
                print(f'{path}: contains mojibake patterns -> {found[:5]}')
            else:
                print(f'{path}: CLEAN')
