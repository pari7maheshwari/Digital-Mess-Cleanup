import unittest

import torch
from transformers.modeling_outputs import BaseModelOutputWithPooling

from digital_mess_cleanup.ai_classifier import _extract_features


class ExtractFeaturesTests(unittest.TestCase):
    def test_returns_tensor_features_unchanged(self):
        features = torch.randn(1, 768)

        self.assertIs(_extract_features(features, torch), features)

    def test_extracts_pooled_features_from_transformers_output(self):
        features = torch.randn(1, 768)
        output = BaseModelOutputWithPooling(
            last_hidden_state=torch.randn(1, 77, 768),
            pooler_output=features,
        )

        self.assertIs(_extract_features(output, torch), features)

    def test_extracts_pooled_features_from_tuple_output(self):
        features = torch.randn(1, 768)
        output = (torch.randn(1, 77, 768), features)

        self.assertIs(_extract_features(output, torch), features)


if __name__ == "__main__":
    unittest.main()
