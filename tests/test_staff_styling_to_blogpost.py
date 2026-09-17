import json
import unittest

from brands.asheis import staff_styling_to_blogpost as sut

STAFF = {
    "name": "佐藤 咲",
    "display_name": "Saki",
    "height": "165cm",
    "instagram": "asheis_saki",
    "shop": "本店",
    "is_new": False,
}


def submission(**overrides):
    base = {
        "response_id": "resp-1",
        "staff": STAFF,
        "caption": "",
        "manual_jan_codes": [],
        "styling_photo_ids": ["photo-1"],
        "tag_photo_ids": ["tag-1"],
    }
    base.update(overrides)
    return base


def keys(metafields):
    return [m["key"] for m in metafields]


class TestBuildMetafields(unittest.TestCase):
    def test_omits_empty_lists_rather_than_writing_empty_json(self):
        # articleCreate rejects the whole batch on one bad entry, and an unset
        # field is what the operator fills in by hand.
        res = sut.build_metafields(STAFF, [], [], "")
        self.assertNotIn("styling_product_variants", keys(res))
        self.assertNotIn("styling_main_images", keys(res))

    def test_includes_lists_when_populated(self):
        res = sut.build_metafields(STAFF, ["gid://v/1"], ["gid://f/1"], "")
        by_key = {m["key"]: m for m in res}
        self.assertEqual(
            json.loads(by_key["styling_product_variants"]["value"]), ["gid://v/1"]
        )
        self.assertEqual(
            json.loads(by_key["styling_main_images"]["value"]), ["gid://f/1"]
        )

    def test_omits_every_blank_optional_field(self):
        staff = dict(STAFF, height="", instagram="", shop="")
        res = sut.build_metafields(staff, [], [], "   \n  ")
        self.assertEqual(keys(res), ["styling_model_name"])

    def test_instagram_becomes_a_url_and_tolerates_an_at_sign(self):
        res = sut.build_metafields(dict(STAFF, instagram="@asheis_saki"), [], [], "")
        by_key = {m["key"]: m for m in res}
        self.assertEqual(
            by_key["styling_model_instagram_link"]["value"],
            "https://www.instagram.com/asheis_saki/",
        )

    def test_shop_is_snapshotted_onto_the_article(self):
        # The blog card shows it, and it must not change when the staff member
        # transfers to another shop.
        by_key = {m["key"]: m for m in sut.build_metafields(STAFF, [], [], "")}
        self.assertEqual(by_key["styling_shop_name"]["value"], "本店")
        self.assertNotIn(
            "styling_shop_name",
            keys(sut.build_metafields(dict(STAFF, shop=""), [], [], "")),
        )

    def test_response_id_is_written_as_the_idempotency_marker(self):
        res = sut.build_metafields(STAFF, [], [], "", "resp-1")
        by_key = {m["key"]: m for m in res}
        self.assertEqual(by_key["styling_submission_id"]["value"], "resp-1")
        self.assertNotIn(
            "styling_submission_id", keys(sut.build_metafields(STAFF, [], [], ""))
        )


def report(**overrides):
    base = {
        "resolved": [{"sku": "1"}],
        "unresolved": [],
        "unreadable_tags": [],
        "failed_photos": [],
        "uploaded_photos": 3,
    }
    base.update(overrides)
    return base


class TestCollectWarnings(unittest.TestCase):
    def test_no_warnings_when_everything_resolved(self):
        self.assertEqual(sut.collect_warnings(report()), [])

    def test_flags_unidentified_products(self):
        res = sut.collect_warnings(report(resolved=[], unresolved=["4550351287507"]))
        joined = "\n".join(res)
        self.assertIn("4550351287507", joined)
        self.assertIn("Styling - Product Variants", joined)

    def test_flags_unreadable_tags_missing_photos_and_failed_photos(self):
        res = sut.collect_warnings(
            report(
                resolved=[],
                unreadable_tags=["tag-1", "tag-2"],
                failed_photos=["photo-9"],
                uploaded_photos=0,
            )
        )
        joined = "\n".join(res)
        self.assertIn("2枚", joined)
        self.assertIn("スタイリング写真がありません", joined)
        self.assertIn("取り込めませんでした", joined)

    def test_photos_submitted_but_none_imported_still_warns_about_the_cover(self):
        # Only the upload result can tell us the article ended up bare.
        res = sut.collect_warnings(
            report(failed_photos=["p1", "p2"], uploaded_photos=0)
        )
        self.assertIn("スタイリング写真がありません", "\n".join(res))

    def test_a_partial_match_points_at_the_metafield_too(self):
        # Two items matched, one did not: the operator still has to open
        # Styling - Product Variants and add the missing one.
        res = sut.collect_warnings(report(unresolved=["999"]))
        joined = "\n".join(res)
        self.assertIn("999", joined)
        self.assertIn("Styling - Product Variants", joined)


class TestArticleLookup(unittest.TestCase):
    ARTICLES = [
        {"id": "gid://a/1", "title": "Miki17", "submissionId": None},
        {"id": "gid://a/2", "title": "MIKI18", "submissionId": {"value": "resp-9"}},
        {"id": "gid://a/3", "title": "Miki11-2", "submissionId": None},
        {"id": "gid://a/4", "title": "Saki3", "submissionId": None},
    ]

    def test_numbering_ignores_case_so_it_cannot_reissue_a_title(self):
        self.assertEqual(sut.next_article_title(self.ARTICLES, "Miki"), "Miki19")

    def test_numbering_ignores_suffixed_manual_duplicates(self):
        self.assertEqual(sut.next_article_title(self.ARTICLES, "Saki"), "Saki4")

    def test_first_article_for_a_new_staff_member(self):
        self.assertEqual(sut.next_article_title(self.ARTICLES, "Newcomer"), "Newcomer1")

    def test_finds_the_article_a_previous_run_left(self):
        found = sut.existing_article_for_submission(self.ARTICLES, "resp-9")
        self.assertEqual(found["title"], "MIKI18")

    def test_no_match_for_an_unseen_or_blank_response_id(self):
        self.assertIsNone(sut.existing_article_for_submission(self.ARTICLES, "resp-x"))
        self.assertIsNone(sut.existing_article_for_submission(self.ARTICLES, ""))


class TestShouldPublish(unittest.TestCase):
    def test_one_product_and_one_photo_is_enough(self):
        self.assertTrue(sut.should_publish(report(uploaded_photos=1)))

    def test_an_unidentified_extra_item_does_not_hold_it_back(self):
        # A warning, not a reason to hide a post that already has a product.
        self.assertTrue(
            sut.should_publish(report(unresolved=["999"], unreadable_tags=["t2"]))
        )

    def test_no_identified_product_stays_hidden(self):
        self.assertFalse(sut.should_publish(report(resolved=[], unresolved=["999"])))

    def test_counts_photos_that_reached_shopify_not_photos_submitted(self):
        self.assertFalse(
            sut.should_publish(report(failed_photos=["p1", "p2"], uploaded_photos=0))
        )


SUBMISSION = submission(spreadsheet_id="sheet-1")
VARIANT = {"displayName": "COAT - BEIGE / F", "sku": "2126", "barcode": "4550351287507"}


def outcome(**overrides):
    r = report(resolved=[VARIANT], **overrides)
    r["warnings"] = sut.collect_warnings(r)
    r["published"] = sut.should_publish(r)
    return sut.outcome_mail(SUBMISSION, STAFF, "Saki20", "gid://shopify/Article/1", r)


class TestOutcomeMail(unittest.TestCase):
    def test_clean_submission_says_it_is_live(self):
        subject, lines = outcome()
        self.assertEqual(subject, "【スタイリング投稿】公開: Saki20 (佐藤 咲)")
        self.assertIn("公開しました", lines[0])
        self.assertNotIn("要確認:", lines)

    def test_published_with_a_problem_still_asks_for_a_look(self):
        subject, lines = outcome(unresolved=["999"])
        self.assertEqual(subject, "【スタイリング投稿】公開・要確認: Saki20 (佐藤 咲)")
        self.assertIn("公開しました", lines[0])
        self.assertIn("999", "\n".join(lines))

    def test_below_the_threshold_it_says_why_it_is_hidden(self):
        r = report(resolved=[], unresolved=["999"])
        r["warnings"] = sut.collect_warnings(r)
        r["published"] = sut.should_publish(r)
        subject, lines = sut.outcome_mail(
            SUBMISSION, STAFF, "Saki20", "gid://shopify/Article/1", r
        )
        self.assertEqual(
            subject, "【スタイリング投稿】非公開・要確認: Saki20 (佐藤 咲)"
        )
        self.assertIn("非公開で作成しました", lines[0])
        self.assertIn("着用商品1点以上", lines[0])
        self.assertTrue(any(l.startswith("確認・公開: ") for l in lines))


class TestVariantLine(unittest.TestCase):
    def test_names_the_jan_because_that_is_what_is_on_the_tag(self):
        line = sut.variant_line(
            {
                "displayName": "COAT - BEIGE / F",
                "sku": "2126",
                "barcode": "4550351287507",
            }
        )
        self.assertIn("SKU: 2126", line)
        self.assertIn("JAN: 4550351287507", line)

    def test_omits_the_jan_when_the_variant_has_no_barcode(self):
        line = sut.variant_line({"displayName": "COAT", "sku": "2126", "barcode": None})
        self.assertNotIn("JAN", line)


class TestCaptionRichText(unittest.TestCase):
    def test_each_non_blank_line_becomes_a_paragraph(self):
        value = json.loads(sut.caption_rich_text("一行目\n\n 二行目 "))
        self.assertEqual(value["type"], "root")
        self.assertEqual(
            [c["children"][0]["value"] for c in value["children"]], ["一行目", "二行目"]
        )


class TestUrls(unittest.TestCase):
    def test_admin_article_url_uses_the_numeric_id(self):
        self.assertEqual(
            sut.admin_article_url("gid://shopify/Article/578503901322"),
            "https://admin.shopify.com/store/asheis/content/articles/578503901322",
        )

    def test_drive_file_url(self):
        self.assertEqual(
            sut.drive_file_url("abc123"), "https://drive.google.com/file/d/abc123/view"
        )


if __name__ == "__main__":
    unittest.main()
