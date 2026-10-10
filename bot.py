import json, os, subprocess, requests

WEBHOOK = os.environ["DISCORD_WEBHOOK"]
CREATORS = ["khaby.lame", "charlidamelio"]  # sans le @
STATE = "state.json"

state = json.load(open(STATE)) if os.path.exists(STATE) else {}

for c in CREATORS:
    out = subprocess.run(
        ["yt-dlp", "--flat-playlist", "--playlist-end", "5", "-j",
         f"https://www.tiktok.com/@{c}"],
        capture_output=True, text=True).stdout
    vids = [json.loads(l) for l in out.splitlines() if l]
    ids = [v["id"] for v in vids]
    if not ids:
        continue
    if c in state:  # pas de spam au 1er lancement
        for i in reversed(ids):
            if i not in state[c]:
                requests.post(WEBHOOK, json={
                    "content": f"Nouveau TikTok de @{c} : https://www.tiktok.com/@{c}/video/{i}"})
    state[c] = ids + [i for i in state.get(c, []) if i not in ids][:50]

json.dump(state, open(STATE, "w"))
