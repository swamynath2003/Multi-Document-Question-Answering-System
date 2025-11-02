import string
import re
from collections import Counter
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
import nltk

# Download required NLTK data
nltk.download('punkt', quiet=True)

def normalize_answer(s):
    """Normalize the answer text for metrics calculation"""
    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)
    def white_space_fix(text):
        return ' '.join(text.split())
    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)
    def lower(text):
        return text.lower()
    return white_space_fix(remove_articles(remove_punc(lower(s))))

def calculate_metrics(prediction, ground_truth):
    """Calculate various NLP metrics between prediction and ground truth"""
    if not prediction or not ground_truth:
        return {
            'f1': 0.0,
            'exact_match': 0.0,
            'bleu': 0.0,
            'rouge': {'rouge1': 0.0, 'rouge2': 0.0, 'rougeL': 0.0}
        }
    
    norm_pred = normalize_answer(prediction)
    norm_truth = normalize_answer(ground_truth)
    
    pred_tokens = norm_pred.split()
    truth_tokens = norm_truth.split()
    
    common = Counter(pred_tokens) & Counter(truth_tokens)
    num_same = sum(common.values())
    
    if num_same == 0:
        f1 = 0.0
    else:
        precision = num_same / len(pred_tokens)
        recall = num_same / len(truth_tokens)
        f1 = (2 * precision * recall) / (precision + recall)
    
    exact_match = float(norm_pred == norm_truth)
    
    try:
        smoother = SmoothingFunction().method1
        bleu = sentence_bleu([truth_tokens], pred_tokens, smoothing_function=smoother)
    except:
        bleu = 0.0
    
    try:
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        rouge_scores = scorer.score(norm_truth, norm_pred)
        rouge = {
            'rouge1': rouge_scores['rouge1'].fmeasure,
            'rouge2': rouge_scores['rouge2'].fmeasure,
            'rougeL': rouge_scores['rougeL'].fmeasure
        }
    except:
        rouge = {'rouge1': 0.0, 'rouge2': 0.0, 'rougeL': 0.0}
    
    return {'f1': f1, 'exact_match': exact_match, 'bleu': bleu, 'rouge': rouge}