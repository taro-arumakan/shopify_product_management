"""Update the ASHEIS storefront shipping note in the LIVE theme.

Companion to update_shipping.py, which renames the *checkout* shipping methods.
This one updates the two *storefront* places the note is rendered:

  templates/product.json        settings.shipping_note   (Buy buttons block ->
                                inside the カートに追加 button, main form + sticky bar)
  sections/overlay-group.json   settings.shipping_notice (cart drawer, above the
                                checkout button)

Note the different key spellings ("shipping_note" vs "shipping_notice"), and that
the cart drawer's effective value lives in the overlay-group section group, NOT in
the schema default in sections/cart-drawer.liquid — editing the .liquid default has
no effect once a value is stored.

The theme changes independently of this job (banner swaps, collection shuffling), so
the live file is fetched at run time and only the note value is substituted. We
deliberately do NOT json.dumps() the whole template back: that would drop Shopify's
auto-generated header comment and reformat every line, producing a huge diff that
can collide with a concurrent theme-editor save. Instead we locate the value via the
parsed dict, then do a single guarded string substitution on the raw content (same
approach as .github/actions/roh_slideshow_weekly_rotate.py).

Pass new_note="" to hide the note (both templates test `!= blank`).

Wire from Shopify Flow -> `run_func` GitHub Action:
    script_path  brands/asheis/update_theme_shipping_note.py
    func_name    update_theme_shipping_note
    params       {"new_note": "", "execute": true}
"""

import json
import logging
import re

import utils

logger = logging.getLogger(__name__)

# (theme file, setting key) — the key is looked up wherever it appears in the file,
# so merchant-regenerated block/section ids do not break this.
NOTE_TARGETS = [
    ("templates/product.json", "shipping_note"),
    ("sections/overlay-group.json", "shipping_notice"),
]


def find_setting_values(data, key):
    """Return every value stored under `key` anywhere in a parsed theme JSON dict."""
    found = []
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            for k, v in node.items():
                if k == key:
                    found.append(v)
                else:
                    stack.append(v)
        elif isinstance(node, list):
            stack.extend(node)
    return found


def substitute_setting(content, key, old_value, new_value):
    """Replace the single `"key": "old_value"` pair in raw content. Raises if the
    match is missing or ambiguous, so a silent no-op is impossible."""
    pattern = re.compile(
        r'("'
        + re.escape(key)
        + r'"\s*:\s*)'
        + re.escape(json.dumps(old_value, ensure_ascii=False))
    )
    matches = pattern.findall(content)
    if len(matches) != 1:
        raise RuntimeError(
            f"expected exactly 1 occurrence of {key!r}={old_value!r}, found {len(matches)}"
        )
    return pattern.sub(
        lambda m: m.group(1) + json.dumps(new_value, ensure_ascii=False),
        content,
        count=1,
    )


def update_theme_shipping_note(new_note, execute=False, theme_name=None):
    """run_func entrypoint — patch the shipping note in the live (MAIN) theme.

    kwargs-only; the run_func runner calls resolved_func(**params) with no client.
    Idempotent: files already showing `new_note` are skipped, so a retried or
    duplicated trigger is a no-op. Defaults to a dry run.
    """
    logging.basicConfig(level=logging.INFO)
    client = utils.client("asheis")

    if theme_name:
        themes = client.themes_by_names(theme_name)
        if len(themes) != 1:
            raise RuntimeError(f"theme not found or ambiguous: {theme_name!r}")
        theme = themes[0]
    else:
        theme = client.current_theme()
        if not theme:
            raise RuntimeError("no active theme found (role=MAIN)")

    print(f"THEME {theme['name']} ({theme['id']}, role={theme['role']})")
    print(f"new note -> {new_note!r}\n")

    pending = []
    for file_name, key in NOTE_TARGETS:
        nodes = [
            n
            for n in client.theme_file_by_theme_name_and_file_name(
                theme["name"], file_name
            )
            if n["filename"] == file_name
        ]
        if not nodes:
            raise RuntimeError(f"theme file not found: {file_name}")
        content = nodes[0]["body"]["content"]

        values = find_setting_values(client.theme_json_to_dict(content), key)
        if len(values) != 1:
            raise RuntimeError(
                f"{file_name}: expected 1 {key!r} setting, found {len(values)}"
            )
        old_value = values[0]

        if old_value == new_note:
            print(f"  = {file_name:<30} {key} already {new_note!r} — skipping")
            continue

        print(f"  ~ {file_name:<30} {key}: {old_value!r} -> {new_note!r}")
        pending.append(
            (file_name, substitute_setting(content, key, old_value, new_note))
        )

    if not pending:
        print("\nNothing to update — all notes already current.")
        return

    if not execute:
        print(
            f"\nDRY RUN — {len(pending)} file(s) would be updated. Set execute=True to apply."
        )
        return

    for file_name, new_content in pending:
        client.upsert_theme_file(theme["id"], file_name, new_content)
        print(f"  ✅ upserted {file_name}")

    # Re-read to confirm the change actually landed (this runs unattended).
    for file_name, key in NOTE_TARGETS:
        nodes = [
            n
            for n in client.theme_file_by_theme_name_and_file_name(
                theme["name"], file_name
            )
            if n["filename"] == file_name
        ]
        values = find_setting_values(
            client.theme_json_to_dict(nodes[0]["body"]["content"]), key
        )
        status = "OK" if values and values[0] == new_note else f"MISMATCH {values!r}"
        print(f"  verify {file_name:<30} {status}")


def main():
    # ── Run ON/BEFORE 8/24, alongside update_shipping.rename_shipping_methods.
    #    Verify the dry run, then set execute=True (or trigger the run_func Action).
    update_theme_shipping_note(new_note="", execute=False)


if __name__ == "__main__":
    main()
