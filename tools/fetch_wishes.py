#!/usr/bin/env python3
"""Holt offene Bau- und Plugin-Wünsche (GitHub-Issues) für die Website.

Läuft im Workflow mit GH_TOKEN und GITHUB_REPOSITORY. Ohne Token passiert nichts,
die Website zeigt dann einfach keine Wünsche an.
"""
import json, os, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
repo = os.environ.get('GITHUB_REPOSITORY', 'Savox76/minecraft-tools')
token = os.environ.get('GH_TOKEN')
ziel = os.path.join(ROOT, 'tools', 'cache', 'wuensche.json')
ARTEN = {'bauwunsch': 'bau', 'plugin-wunsch': 'plugin'}

wuensche = []
try:
    for seite in range(1, 6):
        req = urllib.request.Request(
            f'https://api.github.com/repos/{repo}/issues?state=open&per_page=100&page={seite}',
            headers={'Accept': 'application/vnd.github+json', **({'Authorization': f'Bearer {token}'} if token else {})})
        with urllib.request.urlopen(req, timeout=20) as r:
            daten = json.load(r)
        for i in daten:
            if 'pull_request' in i:
                continue
            labels = [l['name'] for l in i.get('labels', [])]
            art = next((ARTEN[l] for l in labels if l in ARTEN), None)
            if not art:
                continue
            wuensche.append({'nr': i['number'], 'titel': i['title'], 'url': i['html_url'],
                             'stimmen': i.get('reactions', {}).get('+1', 0), 'art': art,
                             'angenommen': 'angenommen' in labels})
        if len(daten) < 100:
            break
except Exception as e:  # Website soll auch ohne Wünsche gebaut werden
    print('Wünsche konnten nicht geladen werden:', e)

os.makedirs(os.path.dirname(ziel), exist_ok=True)
with open(ziel, 'w', encoding='utf-8') as f:
    json.dump(wuensche, f, ensure_ascii=False)
print(len(wuensche), 'Wünsche')
