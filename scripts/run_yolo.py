
import os
import pandas as pd
from ultralytics import YOLO

PROJECT_ROOT = "/content/drive/MyDrive/medical_telegram_warehouse"
model = YOLO("yolov8n.pt")
image_base = f"{PROJECT_ROOT}/data/raw/images"
results = []

for channel in os.listdir(image_base):
    channel_path = os.path.join(image_base, channel)
    if not os.path.isdir(channel_path):
        continue
    for img_file in os.listdir(channel_path):
        if not img_file.endswith(".jpg"):
            continue
        img_path = os.path.join(channel_path, img_file)
        detections = model(img_path)
        classes = []
        confs = []
        for r in detections:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                classes.append(model.names[cls])
                confs.append(conf)
        has_person = "person" in classes
        has_product = any(c in ["bottle", "cup", "cell phone", "book", "tv", "laptop"] for c in classes)
        if has_person and has_product:
            category = "promotional"
        elif has_product and not has_person:
            category = "product_display"
        elif has_person and not has_product:
            category = "lifestyle"
        else:
            category = "other"
        msg_id = int(os.path.splitext(img_file)[0])
        results.append({
            "message_id": msg_id,
            "channel": channel,
            "image_path": img_path,
            "detected_classes": ", ".join(classes),
            "confidences": ", ".join(map(str, confs)),
            "image_category": category,
            "has_person": has_person,
            "has_product": has_product
        })
        print(f"Processed {img_file} -> {category}")

df = pd.DataFrame(results)
df.to_csv(f"{PROJECT_ROOT}/data/yolo_results.csv", index=False)
print("YOLO run complete")
