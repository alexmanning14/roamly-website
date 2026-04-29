"""Generate photorealistic iPhone mockups via Gemini 2.5 Flash Image (nano-banana).
Uploads each app screenshot with a prompt, downloads the generated image,
saves it to assets/screens/.
"""
import os, sys, json, base64, time
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API_KEY = os.environ['GEMINI_API_KEY']
MODEL = 'gemini-2.5-flash-image'
URL = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}'

ROOT = '/Users/alexmanning/Desktop/roamly-website/assets/screens'

JOBS = [
    # (input, output, prompt)
    ('places.png', 'places-hero.png',
     "Generate a photorealistic image of a hand holding an iPhone 16 Pro in natural style. "
     "The phone's screen must show this exact app screenshot pixel-perfect, with no edits to the screen content. "
     "The hand is holding the phone tilted slightly to the right, with the phone angled at about 15 degrees so the right edge comes forward. "
     "Soft studio lighting from the upper left, gentle drop shadow, clean off-white cream-colored background (#FAF6F2). "
     "Realistic skin tones and lighting on the hand. The phone's titanium bezel and dynamic island are clearly visible. "
     "Crop tightly so the hand and phone fill most of the frame. Output in portrait orientation."),
    ('itinerary.png', 'itinerary-mockup.png',
     "Generate a photorealistic image of an iPhone 16 Pro at an angle, showing this exact app screenshot pixel-perfect on its screen. "
     "The phone is tilted with its left edge coming forward at about 12 degrees, sitting on a soft surface. "
     "Soft warm lighting from the upper left, realistic shadow beneath the phone, clean cream paper-textured background. "
     "Visible titanium bezel and dynamic island. Portrait orientation, phone fills most of the frame. No hands."),
    ('globe.png', 'globe-mockup.png',
     "Generate a photorealistic image of an iPhone 16 Pro at an angle, showing this exact app screenshot pixel-perfect on its screen. "
     "The phone is tilted with its right edge coming forward at about 12 degrees. "
     "Cool blue-gray atmospheric background suggesting night sky, soft glow around the phone, realistic shadow. "
     "Visible titanium bezel and dynamic island. Portrait orientation."),
    ('browse.png', 'browse-mockup.png',
     "Generate a photorealistic image of an iPhone 16 Pro at an angle, showing this exact app screenshot pixel-perfect on its screen. "
     "The phone is tilted with its left edge coming forward at about 12 degrees. "
     "Soft mint green pastel background, gentle shadow. Visible titanium bezel and dynamic island. Portrait orientation."),
    ('myposts.png', 'myposts-mockup.png',
     "Generate a photorealistic image of an iPhone 16 Pro at an angle, showing this exact app screenshot pixel-perfect on its screen. "
     "The phone is tilted with its right edge coming forward at about 12 degrees. "
     "Warm coral peach pastel background, gentle shadow. Visible titanium bezel and dynamic island. Portrait orientation."),
]

def call(input_path, prompt):
    with open(input_path, 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode()
    body = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/png", "data": img_b64}}
            ]
        }],
    }
    req = Request(URL, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=180) as r:
            return json.loads(r.read())
    except HTTPError as e:
        print('HTTP', e.code, e.read().decode()[:500])
        raise

for inp, out, prompt in JOBS:
    print(f'-- {inp} -> {out}')
    in_path = f'{ROOT}/{inp}'
    out_path = f'{ROOT}/{out}'
    try:
        resp = call(in_path, prompt)
    except Exception as e:
        print('  FAILED:', e)
        continue
    # Find image in response
    saved = False
    for cand in resp.get('candidates', []):
        for part in cand.get('content', {}).get('parts', []):
            inline = part.get('inline_data') or part.get('inlineData')
            if inline and inline.get('data'):
                with open(out_path, 'wb') as f:
                    f.write(base64.b64decode(inline['data']))
                print(f'  SAVED -> {out_path}')
                saved = True
                break
            if part.get('text'):
                print('  text:', part['text'][:200])
        if saved:
            break
    if not saved:
        print('  no image in response:', json.dumps(resp)[:400])
    time.sleep(1)
print('Done.')
