import os
import csv
import json
import asyncio
import argparse
import logging
import random
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datalake import write_channel_messages_json, write_manifest

load_dotenv()

api_id_str = os.getenv("TG_API_ID")
api_hash = os.getenv("TG_API_HASH")

TODAY = datetime.today().strftime("%Y-%m-%d")
DEFAULT_CHANNEL_DELAY = 3.0
DEFAULT_MESSAGE_DELAY = 1.0

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("telegram_scraper")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(
    os.path.join(LOG_DIR, f"scrape_{TODAY}.log"), encoding="utf-8"
)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# ============================================================
# MEDICAL / PHARMA SAMPLE DATA (matches challenge channels)
# ============================================================
SAMPLE_MESSAGES = {
    "CheMed123": {
        "title": "CheMed Medical Products",
        "posts": [
            ("Amoxicillin 500mg capsules, 100pcs/bottle. Exp 2028. Wholesale price: 450 ETB.", True),
            ("Paracetamol 500mg tablets. 1000pcs pack. Bulk order available. 320 ETB.", False),
            ("NEW: Ibuprofen 400mg. Anti-inflammatory. 50 strips per box. 550 ETB.", True),
            ("Medical glucose test strips. Box of 50. Accurate reading. 280 ETB.", False),
            ("Cough syrup (Guaifenesin) 100ml. Cherry flavor. 180 ETB. Stock available.", True),
            ("Vitamin C 1000mg effervescent. 20 tablets/tube. Boosts immunity. 210 ETB.", False),
            ("Insulin syringe 1ml U-100. Box of 100. Sterile. 340 ETB.", True),
            ("Blood pressure monitor (digital). Wrist type. 1,200 ETB. 1-year warranty.", False),
            ("Antibiotic ointment (Neomycin). 15g tube. For skin infections. 95 ETB.", True),
            ("Multivitamin syrup for kids. 200ml. Iron + Zinc. 250 ETB.", False),
            ("Salbutamol inhaler (Asthma). 200 doses. 320 ETB. In stock.", True),
            ("Surgical masks (3-ply). Box of 50. 180 ETB. High quality.", False),
        ]
    },
    "lobelia4cosmetics": {
        "title": "Lobelia Cosmetics & Health",
        "posts": [
            ("Vitamin E cream. 50ml. Anti-aging. 450 ETB. Organic ingredients.", True),
            ("Coconut oil hair mask. 250ml. Deep conditioning. 320 ETB.", False),
            ("Activated charcoal face wash. 150ml. Removes impurities. 280 ETB.", True),
            ("Aloe vera gel. 100% pure. 200ml. Soothes skin. 210 ETB.", False),
            ("Tea tree oil (antiseptic). 30ml. For acne & fungal infections. 340 ETB.", True),
            ("Rose water toner. 200ml. Natural pH balance. 180 ETB.", False),
            ("Shea butter body lotion. 500ml. SPF 15. 420 ETB.", True),
            ("Nail strengthener (keratin). 15ml. 120 ETB. Quick dry.", False),
            ("Lavender essential oil. 10ml. Relaxation. 250 ETB.", True),
        ]
    },
    "tikvahpharma": {
        "title": "Tikvah Pharmaceuticals",
        "posts": [
            ("Azithromycin 500mg. 3 tablets/blister. Antibiotic. 210 ETB.", True),
            ("Doxycycline 100mg. 10 capsules. Broad-spectrum. 280 ETB.", False),
            ("Metformin 500mg. Diabetes control. 100 tablets. 340 ETB.", True),
            ("Omeprazole 20mg. Acid reflux. 14 capsules. 150 ETB.", False),
            ("Ciprofloxacin 500mg. 10 tablets. 260 ETB. In stock.", True),
            ("Losartan 50mg. Hypertension. 30 tablets. 320 ETB.", False),
            ("Cetirizine 10mg. Antihistamine. 20 tablets. 120 ETB.", True),
            ("Prednisolone 5mg. 100 tablets. Steroid. 450 ETB.", False),
            ("Saline nasal spray. 100ml. 95 ETB. For congestion.", True),
        ]
    }
}

CHANNEL_COLORS = {
    "CheMed123": (0, 100, 200),
    "lobelia4cosmetics": (200, 50, 120),
    "tikvahpharma": (30, 150, 70),
}

def _create_placeholder_image(path: str, channel_name: str = "", msg_id: int = 0, text_snippet: str = ""):
    from PIL import Image, ImageDraw, ImageFont
    bg = CHANNEL_COLORS.get(channel_name, (60, 60, 60))
    img = Image.new("RGB", (400, 300), bg)
    draw = ImageDraw.Draw(img)
    try:
        font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except OSError:
        font_lg = ImageFont.load_default()
        font_sm = font_lg
    draw.text((20, 20), f"@{channel_name}", fill="white", font=font_lg)
    draw.text((20, 55), f"Message #{msg_id}", fill=(200, 200, 200), font=font_sm)
    words = text_snippet[:120].split()
    lines, line = [], ""
    for w in words:
        if len(line + " " + w) > 40:
            lines.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        lines.append(line)
    y = 100
    for ln in lines[:5]:
        draw.text((20, y), ln, fill=(220, 220, 220), font=font_sm)
        y += 22
    draw.text((20, 270), "DEMO IMAGE", fill=(255, 255, 255, 128), font=font_sm)
    img.save(path, "JPEG", quality=85)

def run_demo(base_path: str, limit: int):
    logger.info("[DEMO MODE] Generating sample medical/pharma data")
    date_str = TODAY
    csv_dir = os.path.join(base_path, "raw", "csv", date_str)
    os.makedirs(csv_dir, exist_ok=True)
    csv_file_path = os.path.join(csv_dir, "telegram_data.csv")
    channel_counts = {}
    now = datetime.now(timezone.utc)

    with open(csv_file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["message_id", "channel_name", "channel_title", "message_date",
                         "message_text", "has_media", "image_path", "views", "forwards"])

        for channel_name, channel_data in SAMPLE_MESSAGES.items():
            channel_title = channel_data["title"]
            posts = channel_data["posts"][:limit]
            messages = []
            channel_image_dir = os.path.join(base_path, "raw", "images", channel_name)
            os.makedirs(channel_image_dir, exist_ok=True)

            logger.info(f"[DEMO] Scraping @{channel_name} (limit={len(posts)})")

            for i, (text, has_media) in enumerate(posts):
                msg_id = 1000 + i
                msg_date = (now - timedelta(hours=i * 4 + random.randint(0, 3))).isoformat()
                image_path = None
                if has_media:
                    image_path = os.path.join(channel_image_dir, f"{msg_id}.jpg")
                    _create_placeholder_image(image_path, channel_name, msg_id, text)
                views = random.randint(80, 8000)
                forwards = random.randint(0, views // 10)
                msg = {
                    "message_id": msg_id,
                    "channel_name": channel_name,
                    "channel_title": channel_title,
                    "message_date": msg_date,
                    "message_text": text,
                    "has_media": has_media,
                    "image_path": image_path,
                    "views": views,
                    "forwards": forwards,
                }
                messages.append(msg)
                writer.writerow(list(msg.values()))

            write_channel_messages_json(
                base_path=base_path,
                date_str=date_str,
                channel_name=channel_name,
                messages=messages,
            )
            channel_counts[channel_name] = len(messages)
            logger.info(f"[DEMO] Finished @{channel_name}: {len(messages)} messages")

    write_manifest(base_path=base_path, date_str=date_str, channel_message_counts=channel_counts)
    total = sum(channel_counts.values())
    logger.info(f"[DEMO] Complete. Total messages: {total}")
    for ch, count in channel_counts.items():
        logger.info(f"  @{ch}: {count} messages")
    logger.info(f"[DEMO] Data lake populated at: {base_path}/raw/")
    logger.info(f"[DEMO] Log file: logs/scrape_{date_str}.log")

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telegram Scraper for Medical Channels")
    parser.add_argument("--path", type=str, default="data", help="Base data path")
    parser.add_argument("--limit", type=int, default=100, help="Messages per channel")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode")
    args = parser.parse_args()

    if args.demo:
        run_demo(args.path, args.limit)
    else:
        # Live mode (requires TG_API_ID and TG_API_HASH in .env)
        if not api_id_str or not api_hash:
            print("ERROR: Missing TG_API_ID or TG_API_HASH in .env")
            sys.exit(1)
        from telethon import TelegramClient
        api_id = int(api_id_str)
        # Placeholder for live scraping - you can adapt from the PDF
        print("Live mode not fully implemented in this snippet. Use --demo for testing.")