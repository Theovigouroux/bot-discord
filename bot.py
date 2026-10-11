import json, os, subprocess, time, requests

WEBHOOK = os.environ["DISCORD_WEBHOOK"]
CREATORS = ["djik0s", "kurozen94", "ice_93zo", "hms.v7", "kheph35", "laquika898", "100sans1000", "zeyox78.2"]
STATE = "state.json"

state = json.load(open(STATE)) if os.path.exists(STATE) else {}

def get_ids(c):
    for t in range(2):
        p = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--playlist-end", "5", "-j",
             f"https://www.tiktok.com/@{c}"],
            capture_output=True, text=True)
        ids = [json.loads(l)["id"] for l in p.stdout.splitlines() if l.startswith("{")]
        if ids:
            return ids
        print(c, "essai", t + 1, "echec :", p.stderr[-200:])
        time.sleep(5)
    return []

for c in CREATORS:
    ids = get_ids(c)
    print(c, len(ids), "videos trouvees")
    if not ids:
        continue
    if c in state:
        for i in reversed(ids):
            if i not in state[c]:
                r = requests.post(WEBHOOK, json={
                    "content": f"Nouveau TikTok de @{c} : https://www.tiktok.com/@{c}/video/{i}"})
                print("Envoi Discord", i, "->", r.status_code)
    state[c] = ids + [i for i in state.get(c, []) if i not in ids][:50]

json.dump(state, open(STATE, "w"))
