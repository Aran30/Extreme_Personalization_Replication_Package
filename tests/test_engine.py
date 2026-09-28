import unittest

from personalization.engine import ValidationError, derive_variant


class PersonalizationTests(unittest.TestCase):
    def setUp(self):
        self.agent = {
            "name": "guide", "protected_states": ["welcome"],
            "states": [
                {"id": "welcome", "replies": ["Welcome."], "next": "answer"},
                {"id": "answer", "replies": ["I can provide a short explanation."], "next": "welcome"},
            ],
        }

    def test_variant_preserves_state_structure(self):
        profile = {"id": "reader", "conditions": {"vision": "reduced"}, "adaptations": [
            {"kind": "text_complexity", "value": "simple"},
            {"kind": "interface_style", "value": {"size": 20}},
        ]}
        variant = derive_variant(self.agent, profile)
        self.assertEqual([s["id"] for s in variant["states"]], ["welcome", "answer"])
        self.assertEqual(variant["protected_states"], ["welcome"])
        self.assertEqual(variant["presentation"]["interface_style"]["size"], 20)

    def test_unsupported_adaptation_is_rejected(self):
        profile = {"id": "reader", "conditions": {}, "adaptations": [
            {"kind": "replace_state", "value": "welcome"},
        ]}
        with self.assertRaises(ValidationError):
            derive_variant(self.agent, profile)


if __name__ == "__main__":
    unittest.main()
