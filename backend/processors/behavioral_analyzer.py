"""
LEVEL 3 — THE WRONG PERSON
Behavioral anomaly detection through linguistic feature analysis.
"""

import re
from typing import List, Dict
from dataclasses import dataclass
import statistics


@dataclass
class AuthorMessage:
    author: str
    text: str
    sentences: List[str]
    words: List[str]


@dataclass
class AnomalyScore:
    author: str
    specificity_score: float
    hedge_density: float
    self_reference_ratio: float
    knowledge_claim_ratio: float
    question_ratio: float
    temporal_specificity: float
    vocabulary_overlap: float
    response_latency: float
    anomaly_count: int
    z_scores: Dict[str, float]


class BehavioralAnalyzer:
    """Analyze communication for behavioral anomalies."""

    def __init__(self, messages_text: str):
        self.text = messages_text
        self.messages = self._parse_messages(messages_text)
        self.scores: Dict[str, AnomalyScore] = {}

    def analyze(self) -> Dict:
        """Run behavioral anomaly detection."""
        if len(self.messages) < 2:
            return {"error": "Need at least 2 messages from different authors"}

        # Calculate features for each author
        for author, msg in self.messages.items():
            self.scores[author] = self._calculate_features(author, msg)

        # Calculate z-scores
        z_scores_dict = self._calculate_z_scores()

        # Identify anomalies
        anomalies = self._identify_anomalies(z_scores_dict)

        return {
            "messages": {author: msg.text for author, msg in self.messages.items()},
            "scores": {author: self._score_to_dict(score) for author, score in self.scores.items()},
            "anomalies": anomalies,
            "z_scores": z_scores_dict
        }

    def _parse_messages(self, text: str) -> Dict[str, AuthorMessage]:
        """Parse messages in format: Author: message"""
        messages = {}
        # Match "Name: text" format
        pattern = r'(\w+):\s*([^\n]+(?:\n(?!\w+:)[^\n]*)*)'
        
        for match in re.finditer(pattern, text):
            author = match.group(1)
            message_text = match.group(2).strip()
            
            sentences = [s.strip() for s in re.split(r'[.!?]+', message_text) if s.strip()]
            words = message_text.split()
            
            messages[author] = AuthorMessage(
                author=author,
                text=message_text,
                sentences=sentences,
                words=words
            )
        
        return messages

    def _calculate_features(self, author: str, msg: AuthorMessage) -> AnomalyScore:
        """Calculate all 8 linguistic features for an author."""
        
        specificity = self._specificity_score(msg)
        hedge_dens = self._hedge_density(msg)
        self_ref = self._self_reference_ratio(msg)
        knowledge = self._knowledge_claim_ratio(msg)
        question = self._question_ratio(msg)
        temporal = self._temporal_specificity(msg)
        vocab = self._vocabulary_overlap(author, msg)
        latency = self._response_latency_pattern(msg)

        return AnomalyScore(
            author=author,
            specificity_score=specificity,
            hedge_density=hedge_dens,
            self_reference_ratio=self_ref,
            knowledge_claim_ratio=knowledge,
            question_ratio=question,
            temporal_specificity=temporal,
            vocabulary_overlap=vocab,
            response_latency=latency,
            anomaly_count=0,
            z_scores={}
        )

    def _specificity_score(self, msg: AuthorMessage) -> float:
        """Count specific indicators (numbers, proper nouns, exact times)."""
        specific_count = 0
        specific_count += len(re.findall(r'\d+', msg.text))  # Numbers
        specific_count += msg.text.count('this')  # Demonstratives
        specific_count += msg.text.count('that')
        # Proper nouns (capitalized, not at start)
        proper_nouns = len([w for w in msg.words[1:] if w[0].isupper()])
        specific_count += proper_nouns
        return specific_count / max(len(msg.words), 1)

    def _hedge_density(self, msg: AuthorMessage) -> float:
        """Count hedge words (maybe, I think, probably, etc.)."""
        hedge_words = ['maybe', 'perhaps', 'possibly', 'probably', 'might', 'could', 
                      'seems', 'appears', 'sort of', 'kind of', 'I think', 'I guess',
                      'not sure', 'somewhat', 'relatively', 'apparently']
        
        text_lower = msg.text.lower()
        hedge_count = sum(text_lower.count(word) for word in hedge_words)
        return hedge_count / max(len(msg.sentences), 1)

    def _self_reference_ratio(self, msg: AuthorMessage) -> float:
        """Count first-person pronouns and self-references."""
        self_words = ['i ', 'me ', 'my ', 'mine', "i'm", "i've", "i'll", 'myself']
        text_lower = msg.text.lower()
        self_count = sum(text_lower.count(word) for word in self_words)
        return self_count / max(len(msg.words), 1)

    def _knowledge_claim_ratio(self, msg: AuthorMessage) -> float:
        """Count authoritative claims (I know, I saw, I checked, etc.)."""
        knowledge_words = ['i saw', 'i checked', 'i know', 'i found', 'i noticed',
                          'confirmed', 'verified', 'observed', 'witnessed', 'verified']
        text_lower = msg.text.lower()
        knowledge_count = sum(text_lower.count(word) for word in knowledge_words)
        return knowledge_count / max(len(msg.sentences), 1)

    def _question_ratio(self, msg: AuthorMessage) -> float:
        """Count questions asked."""
        return msg.text.count('?') / max(len(msg.sentences), 1)

    def _temporal_specificity(self, msg: AuthorMessage) -> float:
        """Count temporal references and specificity about when/where."""
        temporal_words = ['morning', 'noon', 'evening', 'yesterday', 'today', 'time',
                         'am', 'pm', 'o\'clock', 'before', 'after', 'during']
        text_lower = msg.text.lower()
        temporal_count = sum(text_lower.count(word) for word in temporal_words)
        return temporal_count / max(len(msg.words), 1)

    def _vocabulary_overlap(self, author: str, msg: AuthorMessage) -> float:
        """Measure overlap with other authors' vocabulary."""
        author_vocab = set(word.lower() for word in msg.words)
        other_vocab = set()
        
        for other_author, other_msg in self.messages.items():
            if other_author != author:
                other_vocab.update(word.lower() for word in other_msg.words)
        
        if not other_vocab:
            return 0.0
        
        overlap = len(author_vocab & other_vocab)
        return overlap / len(other_vocab) if other_vocab else 0.0

    def _response_latency_pattern(self, msg: AuthorMessage) -> float:
        """Estimate if response timing seems off (heuristic based on message length and coherence)."""
        # Messages that are very short or very fragmented might indicate rushed response
        avg_word_count = sum(len(s.split()) for s in msg.sentences) / max(len(msg.sentences), 1)
        
        # Low word count per sentence might indicate rushed/evasive
        if avg_word_count < 5:
            return 0.7
        elif avg_word_count > 15:
            return 0.2
        else:
            return 0.5

    def _calculate_z_scores(self) -> Dict[str, Dict[str, float]]:
        """Calculate z-scores for each feature across authors."""
        features = [
            'specificity_score', 'hedge_density', 'self_reference_ratio',
            'knowledge_claim_ratio', 'question_ratio', 'temporal_specificity',
            'vocabulary_overlap', 'response_latency'
        ]
        
        z_scores = {}
        
        for feature in features:
            values = [getattr(score, feature) for score in self.scores.values()]
            
            if len(values) < 2:
                continue
            
            mean_val = statistics.mean(values)
            try:
                std_val = statistics.stdev(values)
            except:
                std_val = 1.0
            
            for author, score in self.scores.items():
                if author not in z_scores:
                    z_scores[author] = {}
                
                feature_val = getattr(score, feature)
                if std_val > 0:
                    z_score = (feature_val - mean_val) / std_val
                else:
                    z_score = 0
                
                z_scores[author][feature] = z_score
                score.z_scores[feature] = z_score

        return z_scores

    def _identify_anomalies(self, z_scores_dict: Dict) -> List[Dict]:
        """Identify authors with anomalous behavior."""
        anomalies = []
        
        for author, z_scores in z_scores_dict.items():
            # Count features with |z-score| > 1.5
            anomalies_count = sum(1 for z in z_scores.values() if abs(z) > 1.5)
            
            if anomalies_count >= 3:
                anomalies.append({
                    "author": author,
                    "anomaly_count": anomalies_count,
                    "anomalous_features": {k: v for k, v in z_scores.items() if abs(v) > 1.5},
                    "severity": "CRITICAL" if anomalies_count >= 5 else "HIGH"
                })
        
        return sorted(anomalies, key=lambda a: a["anomaly_count"], reverse=True)

    def _score_to_dict(self, score: AnomalyScore) -> dict:
        """Convert AnomalyScore to dict for serialization."""
        return {
            "author": score.author,
            "specificity_score": round(score.specificity_score, 3),
            "hedge_density": round(score.hedge_density, 3),
            "self_reference_ratio": round(score.self_reference_ratio, 3),
            "knowledge_claim_ratio": round(score.knowledge_claim_ratio, 3),
            "question_ratio": round(score.question_ratio, 3),
            "temporal_specificity": round(score.temporal_specificity, 3),
            "vocabulary_overlap": round(score.vocabulary_overlap, 3),
            "response_latency": round(score.response_latency, 3)
        }
