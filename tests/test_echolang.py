"""Offline unit tests (models/network are mocked). Run: python -m unittest discover tests"""
import os, sys, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import echolang


class TestEchoLang(unittest.TestCase):
    def test_rejects_unsupported_language(self):
        with self.assertRaises(ValueError):
            echolang.load_translator("xx")

    def test_rejects_empty_text(self):
        with self.assertRaises(ValueError):
            echolang.translate("   ", "hi")

    def test_translate_uses_pipeline_output(self):
        fake = mock.Mock(return_value=[{"translation_text": "Bonjour"}])
        with mock.patch.dict(echolang._translators, {"fr": fake}):
            self.assertEqual(echolang.translate("Hello", "fr"), "Bonjour")

    def test_run_survives_tts_failure(self):
        with mock.patch.object(echolang, "translate", return_value="Hola"), \
             mock.patch.object(echolang, "text_to_speech", side_effect=OSError("offline")):
            self.assertEqual(echolang.run("Hello", "es", play=False), "Hola")


if __name__ == "__main__":
    unittest.main()
