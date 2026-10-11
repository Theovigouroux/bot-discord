import json, os, subprocess, requests

WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
CREATORS = ["djik0s","kurozen94","ice_93zo"]  # sans le @
STATE = "state.json"

print("Webhook present :", bool(WEBHOOK), "| longueur :", len(WEBHOOK))

state = json.load(open(STATE)) if os.path.exists(STATE) else {}

for c in CREATORS:
    out = subprocess.run(
        ["yt-dlp", "--flat-playlist", "--playlist-end", "5", "-j",
         f"https://www.tiktok.com/@{c}"],
        capture_output=True, text=True).stdout
    vids = [json.loads(l) for l in out.splitlines() if l]
    ids = [v["id"] for v in vids]
    print(c, len(ids), "videos trouvees")
    if not ids:
        continue
    if c in state:
        for i in reversed(ids):
            if i not in state[c]:
                r = requests.post(WEBHOOK, json={
                    "content": f"Nouveau TikTok de @{c} : https://www.tiktok.com/@{c}/video/{i}"})
                print("Envoi Discord", i, "->", r.status_code, r.text[:100])
    state[c] = ids + [i for i in state.get(c, []) if i not in ids][:50]

json.dump(state, open(STATE, "w"))
