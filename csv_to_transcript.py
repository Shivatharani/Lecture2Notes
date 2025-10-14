# utils/csv_to_transcript.py
import csv
import os
from datetime import timedelta

def seconds_to_hhmmss(seconds):
    try:
        sec = float(seconds)
        td = timedelta(seconds=round(sec))
        hhmmss = str(td)
        if len(hhmmss.split(":")) == 2:
            hhmmss = "00:" + hhmmss
        return hhmmss
    except Exception:
        return str(seconds)

def detect_columns(header):
    lower = [h.lower() for h in header]
    colmap = {"text": None, "start": None, "end": None, "speaker": None, "full": None}
    for i, h in enumerate(lower):
        if h in ("text", "transcript", "content", "sentence"):
            colmap["text"] = i
        if h in ("start", "start_time", "start_seconds"):
            colmap["start"] = i
        if h in ("end", "end_time", "end_seconds"):
            colmap["end"] = i
        if h in ("speaker", "role"):
            colmap["speaker"] = i
        if h in ("full_transcript", "full"):
            colmap["full"] = i
    return colmap

def convert_csv_to_txt(csv_path, out_dir="outputs/transcripts", output_name=None, include_timestamps=True, include_speakers=True):
    os.makedirs(out_dir, exist_ok=True)
    base = output_name or os.path.splitext(os.path.basename(csv_path))[0]
    out_path = os.path.join(out_dir, base + ".txt")
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            raise ValueError("Empty CSV")
        colmap = detect_columns(header)

        if colmap.get("full") is not None:
            rows = [row for row in reader]
            if rows:
                full_text = rows[0][colmap["full"]].strip()
                with open(out_path, "w", encoding="utf-8") as out:
                    out.write(full_text)
                return out_path

        lines = []
        for row in reader:
            if not row: continue
            text = None
            if colmap.get("text") is not None and colmap["text"] < len(row):
                text = row[colmap["text"]].strip()
            else:
                for cell in row:
                    if cell and cell.strip():
                        text = cell.strip()
                        break
            if not text:
                continue
            ts = ""
            if include_timestamps and colmap.get("start") is not None and colmap["start"] < len(row):
                start = row[colmap["start"]].strip()
                end = None
                if colmap.get("end") is not None and colmap["end"] < len(row):
                    end = row[colmap["end"]].strip()
                if end:
                    ts = f"[{seconds_to_hhmmss(start)} - {seconds_to_hhmmss(end)}] "
                else:
                    ts = f"[{seconds_to_hhmmss(start)}] "
            speaker = ""
            if include_speakers and colmap.get("speaker") is not None and colmap["speaker"] < len(row):
                sp = row[colmap["speaker"]].strip()
                if sp:
                    speaker = f"{sp}: "
            lines.append(f"{ts}{speaker}{text}")
    with open(out_path, "w", encoding="utf-8") as out:
        out.write("\n".join(lines))
    return out_path
