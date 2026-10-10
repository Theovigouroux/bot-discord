import json, os, requests
import xml.etree.ElementTree as ET

WEBHOOK = os.environ["DISCORD_WEBHOOK"]
CREATORS = ["khaby.lame", "charlidamelio"]  # sans le @
INSTANCES = ["https://rsshub.app"]  # tu pourras en ajouter d'autres
STATE = "state.json"

state = json.load(open(STATE)) if os.path.exists(STATE) else {}

def get_links(c):
    for base in INSTANCES:
        try:
            r = requests.get(f"{base}/tiktok/user/@{c}", timeout=30,
                             headers={"User-Agent": "Mozilla/5.0"})
            print(c, base, r.status_code)
            if r.status_code != 200:
                continue
            root = ET.fromstring(r.content)
            links = [i.findtext("link") for i in root.iter("item")]
            links = [l for l in links if l]
            if links:
                return links[:10]
        except Exception as e:
            print(c, base, "erreur", e)
    return []

for c in CREATORS:
    links = get_links(c)
    print(c, len(links), "videos trouvees")
    if not links:
        continue
    if c in state:  # pas de spam au 1er lancement
        for l in reversed(links):
            if l not in state[c]:
                requests.post(WEBHOOK, json={
                    "content": f"Nouveau TikTok de @{c} : {l}"})
    state[c] = links + [l for l in state.get(c, []) if l not in links][:50]

json.dump(state, open(STATE, "w"))
