# utils/quizgen.py
from transformers import pipeline, set_seed
import textwrap

_QUIZ_MODEL_NAME = "google/flan-t5-base"  # smaller than large, good balance
_generator = None

def _get_generator():
    global _generator
    if _generator is None:
        _generator = pipeline("text2text-generation", model=_QUIZ_MODEL_NAME, do_sample=True, max_length=512)
        set_seed(42)
    return _generator

def generate_quiz_local(summary_text, num_questions=6):
    """
    Generate a readable quiz from the summary using local FLAN-T5.
    Output is plain text containing numbered MCQs. Post-processing is minimal.
    """
    if not summary_text or not summary_text.strip():
        return ""

    generator = _get_generator()

    prompt = (
        f"Create {num_questions} multiple choice questions (4 options each) from the text below. "
        "For each question, provide the correct option letter (a/b/c/d) and a one-line explanation. "
        "Output in a clear numbered format like:\n\n"
        "1) Question?\n a) option\n b) option\n c) option\n d) option\n Answer: b\n Explanation: ...\n\n"
        f"Text:\n{summary_text}"
    )

    try:
        output = generator(prompt, max_length=512, do_sample=True, temperature=0.7)[0]['generated_text']
    except Exception as e:
        output = f"Quiz generation failed: {e}"

    # clean/truncate if very long
    return textwrap.dedent(output).strip()
