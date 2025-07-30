from transformers import pipeline

def summarize_code(code: str) -> str:
    summarizer = pipeline("summarization", model="microsoft/codebert-base")
    summary = summarizer(code, max_length=100, min_length=30, do_sample=False)
    return summary[0]['summary_text']
