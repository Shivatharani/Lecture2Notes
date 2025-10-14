# utils/summarizer.py
from transformers import pipeline
import math

# Choose summarizer model - 'facebook/bart-large-cnn' works well.
_SUMMARY_MODEL_NAME = "facebook/bart-large-cnn"
_summarizer = None

def _get_summarizer():
    global _summarizer
    if _summarizer is None:
        # device will default to CPU; if you have GPU and torch configured it will use GPU automatically
        _summarizer = pipeline("summarization", model=_SUMMARY_MODEL_NAME)
    return _summarizer

def _chunk_text(text, max_chars=3000):
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        # try to avoid chopping mid-sentence:
        if end < len(text):
            last_period = text.rfind(".", start, end)
            if last_period != -1 and last_period - start > int(0.4*max_chars):
                end = last_period + 1
        chunks.append(text[start:end].strip())
        start = end
    return chunks

def summarize_transcript_local(transcript, max_length=150, min_length=40):
    """
    Chunk transcript if needed, summarize each chunk, then combine summaries into a final summary.
    Returns dict: {'summary': final_text, 'chunk_summaries': [..]}
    """
    if not transcript or not transcript.strip():
        return {"summary": "", "chunk_summaries": []}

    summarizer = pipeline("summarization", model=_SUMMARY_MODEL_NAME)
    chunks = _chunk_text(transcript, max_chars=2500)
    chunk_summaries = []
    for chunk in chunks:
        # summarizer may expect shorter inputs; set parameters conservatively
        try:
            out = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
            text = out[0]['summary_text']
        except Exception:
            # fallback: if chunk too short or error, use chunk itself
            text = chunk
        chunk_summaries.append(text.strip())

    # Combine chunk summaries
    combined = " ".join(chunk_summaries).strip()

    # One more pass to get final concise summary (shorter)
    try:
        final = summarizer(combined, max_length=200, min_length=60, do_sample=False)[0]['summary_text'].strip()
    except Exception:
        final = combined

    return {"summary": final, "chunk_summaries": chunk_summaries, "raw_combined": combined}
