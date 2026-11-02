import hashlib
import io
import unittest
import zipfile
from scripts.ppg_policy_body_identity import qualify_body, unpack_single_document


class PolicyBodyIdentityTests(unittest.TestCase):
    def setUp(self):
        self.policy = {"DocumentUID": "fictional-uid", "sourceDocumentId": "ORG-Clin-Proc-Pump-42-V3-06/28",
                       "sourceTitle": "Amber Pump Operation"}
        self.doc = self.body("Document Number ORG-Clin-Proc-Pump-42-V2-05/26\nAmber Pump Operation\n" +
                             "Inspect the amber pump before use. " * 8)

    @staticmethod
    def body(text):
        return {"sha256": "a" * 64, "text": text, "textSHA256": hashlib.sha256(text.encode()).hexdigest(),
                "scope": "full document", "error": None}

    def test_same_family_is_retained_edition_not_current_authority(self):
        result = qualify_body(self.policy, self.doc)
        self.assertEqual(result["status"], "retained-body-bound")
        self.assertFalse(result["currentAuthority"])
        self.assertIn("not established", result["editionRelation"])

    def test_title_only_and_body_reference_do_not_bind(self):
        for text in ("Amber Pump Operation\n" + "A generic instruction. " * 20,
                     "Amber Pump Operation\nPurpose\nRelated document:\n" + self.doc["text"],
                     "Amber Pump Operation\n" + "A generic instruction. " * 100 + self.doc["text"]):
            with self.subTest(text=text[:50]):
                self.assertEqual(qualify_body(self.policy, self.body(text))["status"], "held")

    def test_native_uid_and_heading_can_bind_missing_printed_code(self):
        doc = self.body("Amber Pump Operation\n" + "Inspect the amber pump. " * 15)
        self.assertEqual(qualify_body(self.policy, doc, native_uid="fictional-uid")["status"], "retained-body-bound")
        with self.assertRaises(ValueError):
            qualify_body(self.policy, doc, native_uid="other-uid")

    def test_number_conflict_cannot_be_approved_by_title(self):
        text = self.doc["text"].replace("Pump-42", "Pump-43")
        doc = self.body(text)
        variant = {"expectedId": self.policy["sourceDocumentId"], "printedId": "ORG-Clin-Proc-Pump-43-V2-05/26",
                   "sha256": doc["sha256"], "reason": "Same title"}
        self.assertEqual(qualify_body(self.policy, doc, variant=variant)["status"], "held")

    def test_reviewed_segment_variant_is_capture_pinned(self):
        doc = self.body(self.doc["text"].replace("Proc-Pump", "Proc-Device"))
        variant = {"expectedId": self.policy["sourceDocumentId"], "printedId": "ORG-Clin-Proc-Device-42-V2-05/26",
                   "sha256": doc["sha256"], "reason": "Reviewed same number and heading"}
        self.assertEqual(qualify_body(self.policy, doc, variant=variant)["status"], "retained-body-bound")
        variant["sha256"] = "b" * 64
        with self.assertRaises(ValueError):
            qualify_body(self.policy, doc, variant=variant)

    def test_changed_text_and_summary_are_not_qualified(self):
        self.doc["text"] += " changed"
        with self.assertRaises(ValueError):
            qualify_body(self.policy, self.doc)
        self.doc["scope"] = "first two pages"
        self.assertEqual(qualify_body(self.policy, self.doc)["status"], "held")

    def test_spacing_is_normalised_but_truncated_codes_do_not_bind(self):
        doc = self.body(self.doc["text"].replace("Pump-42", "Pump- 42"))
        self.assertEqual(qualify_body(self.policy, doc)["status"], "retained-body-bound")
        self.policy["sourceDocumentId"] = "ORG-Clin-Proc-Pump"
        doc = self.body(self.doc["text"].replace("Pump-42-V2-05/26", "Pump"))
        self.assertEqual(qualify_body(self.policy, doc)["status"], "held")

    def test_common_drug_heading_and_body_mentions_cannot_replace_named_medicine(self):
        self.policy["sourceTitle"] = "Drug Infusion Guideline - Ambermedicine"
        doc = self.body("Document Number ORG-Clin-Proc-Pump-42-V2-05/26\n"
                        "Drug Infusion Guideline - Othermedicine\nPresentation\n"
                        "Ambermedicine is mentioned as an interaction. " * 8)
        self.assertEqual(qualify_body(self.policy, doc, native_uid="fictional-uid")["status"], "held")

    def test_wrapped_original_retains_both_hashes(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as package:
            package.writestr("original.doc", b"fictional original")
        result = unpack_single_document(stream.getvalue())
        self.assertEqual(result["content"], b"fictional original")
        self.assertEqual(result["containerSHA256"], hashlib.sha256(stream.getvalue()).hexdigest())
        self.assertEqual(result["memberSHA256"], hashlib.sha256(b"fictional original").hexdigest())

    def test_multiple_versions_and_unsafe_member_are_not_silently_selected(self):
        for names in (("one.doc", "two.doc"), ("../original.doc",), ("..\\original.doc",)):
            with self.subTest(names=names):
                stream = io.BytesIO()
                with zipfile.ZipFile(stream, "w") as package:
                    for name in names:
                        package.writestr(name, b"fictional")
                with zipfile.ZipFile(io.BytesIO(stream.getvalue())) as package:
                    self.assertEqual(package.namelist(), list(names))
                with self.assertRaises(ValueError):
                    unpack_single_document(stream.getvalue())


if __name__ == "__main__":
    unittest.main()
