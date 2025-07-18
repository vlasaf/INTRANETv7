# -*- coding: utf-8 -*-
"""
Calculates scores for the Schwartz Value Survey (SVS).
"""
import numpy as np
from typing import Dict, Any, List, Tuple

class SVSScorer:
    """
    Calculates SVS scores based on user responses.

    The scoring process involves:
    1. Ipsatization: Adjusting scores to control for individual response biases.
    2. Calculating 10 basic human values.
    3. Calculating higher-order value dimensions (clusters).
    """

    # Mapping from question ID (1-based) to value type
    # These are the numbers of the questions as provided by the user.
    VALUE_MAP: Dict[str, List[int]] = {
        'Power': [3, 12, 23, 27, 46],
        'Achievement': [14, 34, 39, 43, 48, 55],
        'Hedonism': [4, 50, 57],
        'Stimulation': [9, 25, 37],
        'Self-Direction': [5, 16, 31, 41, 53],
        'Universalism': [1, 2, 6, 15, 17, 24, 26, 29, 30, 35, 38],
        'Benevolence': [19, 28, 33, 45, 49, 52, 54],
        'Tradition': [18, 36, 40, 44, 51],
        'Conformity': [11, 20, 32, 47],
        'Security': [7, 8, 13, 21, 22, 42, 56]
    }

    # Higher-order value dimensions (clusters)
    CLUSTERS: Dict[str, List[str]] = {
        'Self-Transcendence': ['Universalism', 'Benevolence'],
        'Self-Enhancement': ['Power', 'Achievement'],
        'Openness-to-Change': ['Self-Direction', 'Stimulation', 'Hedonism'], # Corrected name to avoid issues with hyphens in keys
        'Conservation': ['Security', 'Conformity', 'Tradition']
    }

    def calculate_scores(self, responses: Dict[int, int]) -> Dict[str, Any]:
        """
        Calculates SVS scores from raw responses.

        Args:
            responses: A dictionary mapping question ID (1-57) to the user's raw score
                       (e.g., -1, 0, 3, 6, 7).

        Returns:
            A dictionary containing:
                - 'raw_scores': The original responses.
                - 'ipsatized_scores': Ipsatized scores for each question.
                - 'mean_raw_score': The mean of all raw scores.
                - 'value_type_scores': Mean ipsatized scores for each of the 10 value types.
                - 'cluster_scores': Mean ipsatized scores for the 4 higher-order clusters.
                - 'sorted_value_types': Value types sorted by their mean ipsatized scores (descending).
        """
        if not responses or len(responses) != 57:
            # Or handle more gracefully, e.g., log a warning and return partial results
            # For now, require all 57 responses
            raise ValueError("SVS scorer requires all 57 responses.")

        raw_scores_list = [responses[i] for i in range(1, 58) if i in responses]

        if not raw_scores_list:
            mean_raw_score = 0.0
        else:
            mean_raw_score = np.mean(raw_scores_list)

        ipsatized_scores: Dict[int, float] = {}
        for q_id, raw_score in responses.items():
            ipsatized_scores[q_id] = float(raw_score - mean_raw_score)

        value_type_scores: Dict[str, float] = {}
        for value_type, question_ids in self.VALUE_MAP.items():
            type_scores = [ipsatized_scores[q_id] for q_id in question_ids if q_id in ipsatized_scores]
            if type_scores:
                value_type_scores[value_type] = np.mean(type_scores)
            else:
                value_type_scores[value_type] = 0.0 # Or handle as NaN or error

        cluster_scores: Dict[str, float] = {}
        for cluster_name, comprised_values in self.CLUSTERS.items():
            cluster_component_scores = [value_type_scores[val_type] for val_type in comprised_values if val_type in value_type_scores]
            if cluster_component_scores:
                cluster_scores[cluster_name] = np.mean(cluster_component_scores)
            else:
                cluster_scores[cluster_name] = 0.0

        sorted_value_types = sorted(value_type_scores.items(), key=lambda item: item[1], reverse=True)

        return {
            'raw_scores': responses,
            'ipsatized_scores': ipsatized_scores,
            'mean_raw_score': mean_raw_score,
            'value_type_scores': value_type_scores,
            'cluster_scores': cluster_scores,
            'sorted_value_types': sorted_value_types
            # The interpretation part (разрывы >= 1 балла, etc.) is more for textual report generation,
            # which would typically happen in the handler or a separate reporting module.
            # This scorer focuses on calculating the numerical scores.
        }

if __name__ == '__main__':
    # Example usage:
    # Create dummy responses (all 3s, for simplicity)
    dummy_responses = {i: 3 for i in range(1, 58)}
    
    scorer = SVSScorer()
    results = scorer.calculate_scores(dummy_responses)

    print("SVS Scoring Example (all 3s as input):")
    print(f"Mean Raw Score: {results['mean_raw_score']:.2f}")
    print("\nIpsatized Scores (first 5):")
    for i in range(1, 6):
        print(f"  Q{i}: {results['ipsatized_scores'].get(i, 'N/A'):.2f}")

    print("\nValue Type Scores (ipsatized means):")
    for value_type, score in results['value_type_scores'].items():
        print(f"  {value_type}: {score:.2f}")

    print("\nCluster Scores (ipsatized means):")
    for cluster, score in results['cluster_scores'].items():
        print(f"  {cluster}: {score:.2f}")
        
    print("\nSorted Value Types:")
    for value_type, score in results['sorted_value_types']:
        print(f"  {value_type}: {score:.2f}")

    # Example with varied responses
    varied_responses = {
        **{i: 7 for i in SVSScorer.VALUE_MAP['Self-Direction']}, # High Self-Direction
        **{i: 6 for i in SVSScorer.VALUE_MAP['Stimulation']},    # High Stimulation
        **{i: 0 for i in SVSScorer.VALUE_MAP['Tradition']},      # Low Tradition
        **{i: -1 for i in SVSScorer.VALUE_MAP['Conformity']}     # Low Conformity
    }
    # Fill the rest with a neutral score (e.g., 3) to have all 57
    for i in range(1, 58):
        if i not in varied_responses:
            varied_responses[i] = 3
            
    print("\n\nSVS Scoring Example (varied responses):")
    results_varied = scorer.calculate_scores(varied_responses)
    print(f"Mean Raw Score: {results_varied['mean_raw_score']:.2f}")
    
    print("\nValue Type Scores (ipsatized means):")
    for value_type, score in results_varied['value_type_scores'].items():
        print(f"  {value_type}: {score:.2f}")

    print("\nSorted Value Types:")
    for value_type, score in results_varied['sorted_value_types']:
        print(f"  {value_type}: {score:.2f}")
    
    print("\nCluster Scores (ipsatized means):")
    for cluster, score in results_varied['cluster_scores'].items():
        print(f"  {cluster}: {score:.2f}") 