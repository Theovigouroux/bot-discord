import json, os, subprocess, time, glob, requests

WEBHOOK = os.environ["DISCORD_WEBHOOK"]
CREATORS = [
    "djik0s", "kurozen94", "ice_93zo", "hms.v7", "kheph35", "laquika898",
    "100sans1000", "zeyox78.2", "corneliusssssssssssssss", "sh1x777",
    "mekinat", "reverse.griffith", "worxx_7", "zaburo27k", "garmadon078",
    "suppositoiree", "jsvtbz6", "jvtlc3", "master..br", "etre.0",
]
STATE = "state.json"
MAX_BYTES = int(9.5 * 1024 * 1024)  # limite Discord (serveur non boosté)

state = json.load(open(STATE)) if os.path.exists(STATE) else {}

def get_ids(c):
    for t in range(3):
        p = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--playlist-end", "5", "-j",
             f"https://www.tiktok.com/@{c}"],
            capture_output=True, text=True)
        ids = [json.loads(l)["id"] for l in p.stdout.splitlines() if l.startswith("{")]
        if ids:
            return ids
        err = [l for l in p.stderr.splitlines() if "ERROR" in l]
        print(c, "essai", t + 1, "echec :", err[0][:200] if err else p.stderr[:200])
        time.sleep(4)
    return []


def cleanup():
    for f in glob.glob("video_*"):
        os.remove(f)

def download(url):
    cleanup()
    ok = False
    for t in range(3):
        p = subprocess.run(
            ["yt-dlp", "-f", "b[ext=mp4]/b", "-o", "video_raw.%(ext)s", url],
            capture_output=True, text=True)
        if glob.glob("video_raw.*"):
            ok = True
            break
        err = [l for l in p.stderr.splitlines() if "ERROR" in l]
        print("download echec", t + 1, err[0][:200] if err else p.stderr[:200])
        time.sleep(3)
    if not ok:
        return None
    f = glob.glob("video_raw.*")[0]
    print("taille video :", os.path.getsize(f) // 1024, "Ko")
    if os.path.getsize(f) <= MAX_BYTES:
        return f
    subprocess.run(["ffmpeg", "-y", "-i", f, "-vf", "scale=-2:540",
                    "-c:v", "libx264", "-crf", "32", "-preset", "veryfast",
                    "-c:a", "aac", "-b:a", "64k", "video_small.mp4"],
                   capture_output=True)
    if os.path.exists("video_small.mp4") and os.path.getsize("video_small.mp4") <= MAX_BYTES:
        return "video_small.mp4"
    return None


def send(c, i):
    url = f"https://www.tiktok.com/@{c}/video/{i}"
    f = download(url)
    if f:
        with open(f, "rb") as fh:
            r = requests.post(WEBHOOK,
                              data={"content": f"Nouveau TikTok de @{c}"},
                              files={"file": (f"{i}.mp4", fh)})
        print("Envoi video", i, "->", r.status_code)
        if r.status_code in (200, 204):
            cleanup()
            return
    # secours : lien
    r = requests.post(WEBHOOK, json={"content": f"Nouveau TikTok de @{c} : {url}"})
    print("Envoi lien", i, "->", r.status_code)
    cleanup()

for c in CREATORS:
    ids = get_ids(c)
    print(c, len(ids), "videos trouvees")
    if not ids:
        continue
    if c in state:
        for i in reversed(ids):
            if i not in state[c]:
                send(c, i)
    state[c] = ids + [i for i in state.get(c, []) if i not in ids][:50]

json.dump(state, open(STATE, "w"))
