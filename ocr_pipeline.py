import os
import pytesseract
from PIL import Image
from testing import extract_with_retry, clean_roles, merge_with_resolution, make_doc_id, load_progress, save_progress
import json

def process_folder(folder_path, dataset_name):
    filenames = sorted(f for f in os.listdir(folder_path) if f.lower().endswith('.jpg'))
    print(f"Found {len(filenames)} images in {folder_path}\n")

    progress = load_progress(dataset_name)
    all_data = progress["all_data"]
    done = set(progress["processed_docs"])

    for i, fname in enumerate(filenames):
        path = os.path.join(folder_path, fname)
        doc_id = make_doc_id(fname)  # hash the filename, since it's stable per page

        if doc_id in done:
            print(f"[{i+1}/{len(filenames)}] {fname} — already done, skipping")
            continue

        text = pytesseract.image_to_string(Image.open(path))

        if len(text.strip()) < 100:
            print(f"[{i+1}/{len(filenames)}] {fname} — too little text, skipping")
            done.add(doc_id)
            progress["processed_docs"] = list(done)
            save_progress(dataset_name, progress)
            continue

        print(f"[{i+1}/{len(filenames)}] {fname} — OCR'd {len(text)} chars, extracting...")

        data = extract_with_retry(text)
        role_map = clean_roles(data)
        data["entities"] = [e for e in data["entities"] if e["name"] not in role_map]
        for r in data["relations"]:
            r["source"] = role_map.get(r["source"], r["source"])
            r["target"] = role_map.get(r["target"], r["target"])

        all_data.append(data)
        done.add(doc_id)

        progress["all_data"] = all_data
        progress["processed_docs"] = list(done)
        save_progress(dataset_name, progress)

        print(f"    -> {len(data['entities'])} entities, {len(data['relations'])} relations found. Total progress: {len(done)}/{len(filenames)}")

    return all_data

if __name__ == "__main__":
    folder = "raw_files/batch2"
    dataset = "epstein_batch1"

    all_data = process_folder(folder, dataset)
    merged = merge_with_resolution(all_data)

    with open("graph_data_epstein.json", "w") as f:
        json.dump(merged, f, indent=2)

    print(f"\nDone. Nodes: {len(merged['nodes'])}")