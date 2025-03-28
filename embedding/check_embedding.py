import pickle
with open("embedding.py", "rb") as f:
    meta = pickle.load(f)
    print(f"✅ 총 {len(meta)} 개 저장됨")
    for m in meta:
        print("📌 문장:", m["text"])