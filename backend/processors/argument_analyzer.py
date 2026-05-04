"""
LEVEL 2 — THE RIGGED QUESTION
Logical fallacy detection in arguments using claim extraction and structural matching.
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class FallacyType(Enum):
    HASTY_GENERALIZATION = "HASTY_GENERALIZATION"
    FALSE_CAUSATION = "FALSE_CAUSATION"
    APPEAL_TO_AUTHORITY = "APPEAL_TO_AUTHORITY"
    SLIPPERY_SLOPE = "SLIPPERY_SLOPE"
    FALSE_DICHOTOMY = "FALSE_DICHOTOMY"
    CIRCULAR_REASONING = "CIRCULAR_REASONING"
    STRAWMAN = "STRAWMAN"
    AD_HOMINEM = "AD_HOMINEM"


@dataclass
class Claim:
    text: str
    line_number: int
    is_evidence: bool
    is_conclusion: bool


@dataclass
class FallacyFinding:
    fallacy_type: FallacyType
    description: str
    triggering_claims: List[int]
    severity: str


class ArgumentAnalyzer:
    """Analyze arguments for logical fallacies."""

    def __init__(self, text: str):
        self.text = text
        self.sentences = self._split_sentences(text)
        self.claims: List[Claim] = []
        self.conclusion_idx = -1

    def analyze(self) -> Dict:
        """Run full fallacy detection."""
        # STEP 1: Extract claims
        self.claims = self._extract_claims()
        
        # STEP 2: Find conclusion
        self.conclusion_idx = self._find_conclusion()
        
        # STEP 3: Build dependency graph
        dependencies = self._build_dependency_graph()
        
        # STEP 4: Detect fallacies
        fallacies = self._detect_fallacies(dependencies)
        
        return {
            "claims": self.claims,
            "conclusion_idx": self.conclusion_idx,
            "dependencies": dependencies,
            "fallacies": fallacies
        }

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Basic sentence splitting on periods, exclamation, question marks
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_claims(self) -> List[Claim]:
        """Extract factual claims from text."""
        claims = []
        for i, sentence in enumerate(self.sentences):
            # Filter out questions, rhetorical statements
            if sentence.endswith('?'):
                continue
            if len(sentence.split()) < 3:
                continue
            
            # Mark as claim
            claim = Claim(
                text=sentence,
                line_number=i,
                is_evidence=self._looks_like_evidence(sentence),
                is_conclusion=False
            )
            claims.append(claim)
        return claims

    def _looks_like_evidence(self, sentence: str) -> bool:
        """Check if sentence provides evidence."""
        evidence_markers = ['shows', 'proves', 'demonstrates', 'data', '%', 'according', 'study',
                          'research', 'evidence', 'fact', 'number', 'drop', 'increase', 'loss']
        return any(marker in sentence.lower() for marker in evidence_markers)

    def _find_conclusion(self) -> int:
        """Find the conclusion (usually last sentence or after 'therefore'/'so')."""
        # Look for conclusion markers
        conclusion_words = ['therefore', 'thus', 'so', 'hence', 'as a result', 'consequently']
        
        for i, sentence in enumerate(self.sentences):
            for word in conclusion_words:
                if word in sentence.lower():
                    return i
        
        # Default to last meaningful sentence
        return len(self.sentences) - 1

    def _build_dependency_graph(self) -> Dict[int, List[int]]:
        """Map which claims support the conclusion."""
        dependencies = {}
        conclusion = self.claims[self.conclusion_idx] if self.conclusion_idx < len(self.claims) else None
        
        if not conclusion:
            return dependencies
        
        # Find claims that logically precede conclusion
        for i, claim in enumerate(self.claims):
            if i != self.conclusion_idx:
                # Simple heuristic: claims before conclusion that aren't contingent
                if i < self.conclusion_idx:
                    dependencies[i] = [self.conclusion_idx]
        
        return dependencies

    def _detect_fallacies(self, dependencies: Dict) -> List[FallacyFinding]:
        """Detect logical fallacies in the argument structure."""
        fallacies = []
        
        # Check for hasty generalization (broad claim from limited evidence)
        if self._has_hasty_generalization():
            fallacies.append(FallacyFinding(
                fallacy_type=FallacyType.HASTY_GENERALIZATION,
                description="Broad conclusion drawn from insufficient evidence",
                triggering_claims=[c for c, claim in enumerate(self.claims) if not claim.is_evidence],
                severity="MEDIUM"
            ))
        
        # Check for false causation (assumes causes that aren't proven)
        if self._has_false_causation():
            fallacies.append(FallacyFinding(
                fallacy_type=FallacyType.FALSE_CAUSATION,
                description="Claims causation between events without establishing it",
                triggering_claims=list(dependencies.keys()),
                severity="HIGH"
            ))
        
        # Check for circular reasoning
        if self._has_circular_reasoning():
            fallacies.append(FallacyFinding(
                fallacy_type=FallacyType.CIRCULAR_REASONING,
                description="The conclusion is used to support its own premise",
                triggering_claims=[self.conclusion_idx],
                severity="CRITICAL"
            ))
        
        # Check for false dichotomy (only two options presented)
        if self._has_false_dichotomy():
            fallacies.append(FallacyFinding(
                fallacy_type=FallacyType.FALSE_DICHOTOMY,
                description="Presents false choice between only two options",
                triggering_claims=[self.conclusion_idx],
                severity="MEDIUM"
            ))
        
        return fallacies

    def _has_hasty_generalization(self) -> bool:
        """Check for hasty generalization patterns."""
        # Look for broad claims ("all", "everyone", "always") 
        broad_words = ['all', 'every', 'everyone', 'always', 'never', 'nothing']
        evidence_count = sum(1 for c in self.claims if c.is_evidence)
        
        if evidence_count == 0 and len(self.claims) > 1:
            return any(word in s.lower() for s in self.sentences for word in broad_words)
        return False

    def _has_false_causation(self) -> bool:
        """Check for temporal sequence mistaken for causation."""
        causation_words = ['because', 'since', 'caused', 'led to', 'resulted in', 'caused by']
        causation_mentioned = any(word in self.text.lower() for word in causation_words)
        
        # Check if causal claims have evidence
        if causation_mentioned:
            evidence_count = sum(1 for c in self.claims if c.is_evidence)
            return evidence_count < len(self.claims) // 2
        return False

    def _has_circular_reasoning(self) -> bool:
        """Check if conclusion restates premise."""
        # Very basic: check for exact/near-duplicate sentences
        if self.conclusion_idx < 0 or self.conclusion_idx >= len(self.claims):
            return False
        
        conclusion_text = self.claims[self.conclusion_idx].text.lower()
        for i, claim in enumerate(self.claims):
            if i != self.conclusion_idx:
                # Check for significant textual overlap
                overlap = sum(1 for word in claim.text.lower().split() if word in conclusion_text)
                if overlap > len(claim.text.split()) * 0.4:
                    return True
        return False

    def _has_false_dichotomy(self) -> bool:
        """Check for false either-or choices."""
        dichotomy_words = ['either', 'or', 'only', 'choice']
        sentences_with_or = [s for s in self.sentences if ' or ' in s.lower()]
        
        if len(sentences_with_or) > 0:
            # Check if there are only two options presented as exhaustive
            conclusion = self.sentences[self.conclusion_idx] if self.conclusion_idx < len(self.sentences) else ""
            return 'or' in conclusion.lower() and 'either' in conclusion.lower()
        return False
