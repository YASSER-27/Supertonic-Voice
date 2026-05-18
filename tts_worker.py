import sys
import json
import argparse
import os
import re
import io

# Force UTF-8 for Windows pipes
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)

LANG_PATTERNS = {
    'ar': re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'),
    'ja': re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]'),
    'ko': re.compile(r'[\uAC00-\uD7AF\u1100-\u11FF]'),
    'hi': re.compile(r'[\u0900-\u097F]'),
    'el': re.compile(r'[\u0370-\u03FF]'),
    'ru': re.compile(r'[\u0400-\u04FF]'),
    'uk': re.compile(r'[\u0400-\u04FF]'),
    'bg': re.compile(r'[\u0400-\u04FF]'),
    'vi': re.compile(r'[\u00C0-\u024F\u1E00-\u1EFF]'),
}

SUPPORTED_LANGS = ['en', 'ko', 'ja', 'ar', 'bg', 'cs', 'da', 'de', 'el', 'es', 'et', 'fi', 'fr', 'hi', 'hr', 'hu', 'id', 'it', 'lt', 'lv', 'nl', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sv', 'tr', 'uk', 'vi']

def detect_language(text: str) -> str:
    for lang, pattern in LANG_PATTERNS.items():
        if len(pattern.findall(text)) > len(text) * 0.15:
            return lang
    return 'en'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-dir', required=True)
    args = parser.parse_args()

    # Preload the TTS engine
    try:
        from supertonic import TTS
        tts = TTS(model_dir=args.model_dir, auto_download=False)
        print(json.dumps({"status": "ready"}))
        sys.stdout.flush()
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.stdout.flush()
        sys.exit(1)

    while True:
        line = sys.stdin.readline()
        if not line: break
        line = line.strip()
        if not line: continue
        
        try:
            req = json.loads(line)
            if req.get("action") == "stop":
                break
                
            text = req.get("text", "")
            voice = req.get("voice", "F1")
            output = req.get("output", "out.wav")
            req_id = req.get("id", "0")
            
            style = tts.get_voice_style(voice_name=voice)
            lang = detect_language(text)
            if lang not in SUPPORTED_LANGS: lang = 'en'
            
            wav, duration = tts.synthesize(text, voice_style=style, lang=lang)
            tts.save_audio(wav, output)
            
            dur_val = duration.item() if hasattr(duration, 'item') else float(duration)
            
            print(json.dumps({
                "id": req_id,
                "success": True,
                "duration": round(dur_val, 2),
                "output": output
            }))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}))
            sys.stdout.flush()

if __name__ == '__main__':
    main()
