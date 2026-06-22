"""Fix the 3 products whose description prose is wrapped in <p data-start="..."> (multiple
paragraphs) and were therefore missed by the <p> regex in the description flow — leaving
Japanese (BHARAT DENIM SKATE PANTS BLACK) or a stale 'DUMMY' en (FADE CENTER SEAM, FADE NO
SLEEVE VEST). Their base origin is already 'Japan'. Registers a full English body_html
(structure mirrors each base: prose paragraphs + spec table)."""

import utils

client = utils.client("alvana")
DRY_RUN = True

EN_BODY = {
    "BHARAT DENIM SKATE PANTS BLACK": """<p>Skate pants in Bharat denim, prized for the natural irregularity and depth of Indian cotton. While preserving the material's inherent strength and body, a one-wash finish tames the stiffness for an easy, broken-in feel from the very first wear. The silhouette is a wide straight cut with room from the hip through the hem.<br>Easy to move in and reassuringly stable, it's the kind of balance you reach for naturally day to day. It softens the more you wear it, bringing out the character unique to Indian cotton. A pair of denim to keep company with for years, whatever your style.</p>
<p></p>
<table width="100%">
<tbody>
<tr>
<th>Material</th>
<td>Cotton 100%</td>
</tr>
<tr>
<th>Country of Origin</th>
<td>Japan</td>
</tr>
<tr>
<th>Product No.</th>
<td>ALV-90102</td>
</tr>
</tbody>
</table>""",
    "FADE CENTER SEAM S/S TEE SHIRTS": """<div id="alvanaProduct">
<p>A center-seam design that lends a clear individuality within its simplicity.<br>The substantial hand of heavy jersey and its natural drape accentuate the clean, linear lines.</p>
<p>The length and width keep a basic balance while settling into a relaxed silhouette that sits naturally on the body.<br>A material with both toughness and refinement looks right worn on its own or layered underneath.</p>
<p>It holds its shape well through washing and gains character the more you wear it — a dependable piece.</p>
<br>
<table width="100%">
<tbody>
<tr>
<th>Material</th>
<td>Cotton 100%</td>
</tr>
<tr>
<th>Country of Origin</th>
<td>Japan</td>
</tr>
<tr>
<th>Product No.</th>
<td>ALV-00114</td>
</tr>
</tbody>
</table>
</div>""",
    "FADE NO SLEEVE VEST": """<div id="alvanaProduct">
<p>A piece with a moderately trimmed length and well-balanced overall proportions.<br>The armholes have a comfortable ease, and the natural drape when your arms are down brings out the texture of the material.</p>
<p>The neckline and armholes are binder-finished for a clean, tough construction.<br>It slips on smoothly for a stress-free wearing comfort.</p>
<p>Easy to wear on its own and just as useful as an inner layer under a voluminous top, with excellent breathability.<br>It resists going limp through repeated washing, settling onto the body and deepening in character the more you wear it.</p>

<table width="100%">
<tbody>
<tr>
<th>Material</th>
<td>Cotton 100%</td>
</tr>
<tr>
<th>Country of Origin</th>
<td>Japan</td>
</tr>
<tr>
<th>Product No.</th>
<td>ALV-00116</td>
</tr>
</tbody>
</table>
</div>""",
}


def register_en_body_html(product_id, en_html):
    content = client.run_query(
        "query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }",
        {"id": product_id},
    )["translatableResource"]["translatableContent"]
    digest = next(c["digest"] for c in content if c["key"] == "body_html")
    res = client.run_query(
        """mutation($id: ID!, $tr: [TranslationInput!]!) {
          translationsRegister(resourceId: $id, translations: $tr) { userErrors { field message } }
        }""",
        {
            "id": product_id,
            "tr": [
                {
                    "locale": "en",
                    "key": "body_html",
                    "value": en_html,
                    "translatableContentDigest": digest,
                }
            ],
        },
    )["translationsRegister"]
    if res["userErrors"]:
        raise RuntimeError(f"{product_id}: {res['userErrors']}")


def main():
    for title, en_html in EN_BODY.items():
        p = [
            x
            for x in client.products_by_title(title)
            if x["status"] == "ACTIVE" and "(no image)" not in x["title"]
        ][0]
        print(f"{'(dry) ' if DRY_RUN else ''}registering en for {title}")
        if not DRY_RUN:
            register_en_body_html(p["id"], en_html)


if __name__ == "__main__":
    main()
