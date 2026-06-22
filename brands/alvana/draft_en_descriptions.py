"""Draft English product descriptions for alvana for REVIEW (writes to the 'EN Desc
Drafts' tab of the 26 S/S sheet; does NOT touch Shopify). Prose is translated by hand
below (keyed by one representative product title per unique JA description); the spec
table material is translated mechanically. After review, a separate step builds the
en body_html and registers it as the `en` translation.
"""

import re
import utils

client = utils.client("alvana")

REVIEW_SHEET_ID = "1l4RmXLPSeuLu9b2HY7oelKEyiPfaf1Wi7pFdb5rA614"
REVIEW_TAB = "EN Desc Drafts"

# EN prose keyed by ONE representative product title of each unique JA description.
# (<br> mirrors the source line breaks; identical copy is shared across a product group.)
EN_PROSE = {
    "1960s JP JACKET": "A light-ounce jacket in vintage-finished cupra.<br>Woven at high density for a rich, rustic surface and a cool, dry touch.<br>A moderate crispness harmonizes with cupra's natural, soft sheen for a finish full of depth.",
    "26/ FOOTBALL BALLON S/S TEE": "Light-ounce jersey.<br>An update to the [Tangis jersey] used until now: a light-ounce jersey knit tightly from 26-count yarn. Fine and light to the hand yet excellent in wash durability, with a clean face and a firm, resilient body that sits comfortably against the skin — an all-season material. alvana's new standard cut-and-sewn series.",
    "26/ OVERSIZE TEE SHIRTS": "Light-ounce jersey.<br>An update to the [Tangis jersey] used until now: a light-ounce jersey knit tightly from 26-count yarn. Fine and light to the hand yet excellent in wash durability, with a clean face and a firm, resilient body that sits comfortably against the skin — an all-season material. alvana's new standard cut-and-sewn series.",
    "ANTIQUE EFFECT RAGLAN FREEDOM L/S TEE": "A new material with a strong vintage feel, processed at the fabric stage.<br>By carefully removing excess fuzz at the yarn stage of the extra-long-staple cotton, we created a material with crispness, body, and strength.<br>Knit to a considered, moderately tight gauge, it has a refined dry hand and a distinctive, premium character.<br>It fades gently and naturally as you wear it — a material to grow and enjoy as its expression changes over time.",
    "ANTIQUE EFFECT S/S TEE": "A new material with a strong vintage feel, processed at the fabric stage.<br>By carefully removing excess fuzz at the yarn stage of the extra-long-staple cotton, we created a material with crispness, body, and strength.<br>Knit to a considered, moderately tight gauge, it has a refined dry hand and a distinctive, premium character.<br>It fades gently and naturally as you wear it — a material to grow and enjoy as its expression changes over time.",
    "BHARAT DENIM 3B JACKET": "BHARAT DENIM — a special material that puts the appeal of Indian cotton front and center. Indian cotton's characteristic strength, resilient body, and thick fibers give the cloth a rich surface and a singular hand. Heat-resistant and highly water-absorbent, this “Bharat” material is the base for our original denim items. Built with a considered balance of texture and crisp dryness, it is a lovable, versatile staple that suits a wide range of pieces.",
    "BHARAT DENIM JACKET": "A short jacket long loved as a brand staple. Cut with a comfortably roomy fit and a slightly relaxed ease, a back tuck creates a three-dimensional silhouette for a clean, beautifully balanced finish. Conceived with a simple, refined presence, side pockets keep the look minimal and elegant. Detail is pared back to the essentials for a grown-up piece that is understated yet full of presence. The “Bharat denim aging” that deepens with wear and washing is one of this jacket's signature charms — enjoy the evolving expression of the cloth, much like denim, over many years. A staple jacket that gains depth with time.",
    "BHARAT DENIM SKATE PANTS BLUE": "Skate pants in Bharat denim, prized for the natural irregularity and depth of Indian cotton. While preserving the material's inherent strength and body, a one-wash finish tames the stiffness for an easy, broken-in feel from the very first wear. The silhouette is a wide straight cut with room from the hip through the hem.<br>Easy to move in and reassuringly stable, it's the kind of balance you reach for naturally day to day. It softens the more you wear it, bringing out the character unique to Indian cotton. A pair of denim to keep company with for years, whatever your style.",
    "BHRAT DENIM OVER EASY PANTS": "BHARAT DENIM — a special material that puts the appeal of Indian cotton front and center. Indian cotton's characteristic strength, resilient body, and thick fibers give the cloth a rich surface and a singular hand. Heat-resistant and highly water-absorbent, this “Bharat” material is the base for our original denim items. Built with a considered balance of texture and crisp dryness, it is a lovable, versatile staple that suits a wide range of pieces.",
    "BLACK TWILL 3B JACKET（LIGHTWEIGHT MOLESKIN）": "Indian cotton has long been celebrated for the special character of its texture and luster, and for its renowned strength, yielding many high-quality materials over the years. The Indian cotton used here aims for a moderate lightness and a balanced, tight weave, achieving an exquisite weight that feels neither too heavy nor too light to wear. Specially dyed and finished entirely in black, this lineup expresses a true devotion to black. While pursuing black at its purest, we drew on the craftsmanship of Okayama artisans to fade the cloth without damaging it, chasing a refined vintage feel — an originality you'll find nowhere else. Experience this special piece, filled with the premium quality and fine attention of Japanese manufacturing.",
    "CORDUROY TRACKER JACKET": "A piece that crosses the architectural lines of a 1970s track jacket with the grainy texture unique to a corduroy woven from Indian cotton.<br>A garment wash brings out a deep, characterful surface that draws out the material's appeal all the more.",
    "DUCK WOOL DETROIT PARKA": "A full-zip parka in tough duck cloth. A sturdy cotton shell is paired with a warm wool lining for a piece that carries you comfortably through autumn and winter. Pared-back, simple design meets work-born function: a large front pocket and ribbed hem and cuffs lend just the right presence.<br>It goes naturally with denim or chinos and pairs just as well with wool trousers, slipping easily into grown-up casual style. Tough yet refined, it's a dependable everyday outer layer.",
    "DUCK WOOL SHORT JACKET": "A short jacket cut from rugged duck canvas. A sturdy cotton shell paired with a warm wool lining combines durability with warmth. A simple front zip and cropped length create an urban, refined silhouette. It pairs naturally with denim or chinos, and balances just as well with wide pants or slacks. Within its minimal, pared-back design lives a work-born toughness — a piece for grown-ups.",
    "FADE BALLON FOOTBALL OVER TEE SHIRTS": "By carefully removing excess fuzz at the yarn stage of the extra-long-staple cotton, we created a material with crispness, body, and strength.<br>Knit to a considered, moderately tight gauge, it has a refined dry hand and a distinctive, premium character.<br>It fades gently and naturally as you wear it — a material to grow and enjoy as its expression changes over time.",
    "FADE BALLON S/S PK TEE SHIRTS（ポケット付）": "A cut-and-sewn piece in a balloon silhouette, struck at a balance unlike anything before.<br>It wears with the lightness of a shirt — equally good on its own or layered naturally into a wide range of styles.<br><br>By carefully removing excess fuzz at the yarn stage of the extra-long-staple cotton, we created a material with crispness, body, and strength.<br>Knit to a considered, moderately tight gauge, it has a refined dry hand and a distinctive, premium character.<br>It fades gently and naturally as you wear it — a material to grow and enjoy as its expression changes over time.",
    "LINEN COTTON KNEE CARGO PANTS": "A light, spring–summer fabric that balances linen and cotton in just the right measure.<br>A cotton-linen blended yarn woven at high density gives a rich, rustic texture with a cool, layered hand.<br>A garment wash then draws out a naturally uneven surface and a soft, lived-in character.",
    "LINEN OPEN COLLAR SHIRT": "A light, spring–summer fabric that balances linen and cotton in just the right measure.<br>A cotton-linen blended yarn woven at high density gives a rich, rustic texture with a cool, layered hand.<br>A garment wash then draws out a naturally uneven surface and a soft, lived-in character.",
    "NATURAL HEMP EASY PANTS": "NATURAL TWILL “Muku” (pure)<br>— a refined attachment that can only be made here —<br>Natural twill “Muku” carefully draws out the depth unique to natural materials atop the plain, honest beauty inherent to Indian cotton.<br>Rare “Muku” yarn is woven slowly on vintage looms, creating a moist softness and a smooth texture that settles against the skin like a fine towel.<br>It is a special material that can only be made in a limited, dry environment.<br>Light yet with a moderate crispness, the cloth is everyday wear suited to all of Japan's four seasons. A natural fulling finish draws out the material's own expression, and the unsparing care and time devoted to it complete the refined hand unique to “Muku.”<br>The more you wear and wash it, the deeper the character grows — enjoy the “twill aging” that surfaces on the face of the cloth.",
    "NATURAL HEMP OPEN COLLAR SHIRTS": "“A one-of-a-kind open-collar shirt, woven by hand-craft.” This open-collar hemp shirt makes the most of the qualities of Pokhara hemp for a refined piece, defined by a superb natural hand and the distinctive texture of hemp grown at the foot of the Himalayas. The open-collar design is simple yet modern, offering relaxed wearing comfort while drawing out an elegance well suited to grown-up casual style. Hemp's natural breathability and lightness keep you comfortable even in the hot season, while its excellent durability preserves its appeal over a long life. Simple, yet with a depth woven from material and design, it blends naturally into any outfit — a piece that lets you feel nature's blessings, pairing comfort with a sense of quality.",
    "NATURAL TWILL EASY PANTS": "alvana's signature easy pants — a long-standing staple that has earned a strong following. The line is clean and balanced, with a natural roundness through the waist and knee that tapers gently toward the hem. A drawcord waist lets you cinch the slightly roomy fit to taste, for a look that feels relaxed yet quietly refined. Pared-back design and a flattering silhouette make this a pair that slips naturally into any genre or style. A true wardrobe staple to enjoy for seasons to come. *Designed so cut-and-sewn tops and tees tuck in easily, pairing effortlessly with a wide range of tops.",
    "NATURAL TWILL NO COLLAR JACKET": "A collarless jacket with a vintage-like hand and a rugged, commanding volume. A boxy silhouette makes it an easy, go-to layer, where a coverall's rough ease meets a contemporary essence. The collarless design keeps the neckline clean and works across seasons and a wide range of occasions — a piece worthy of a grown-up wardrobe, ready even for a refined casual style.",
    "NATURAL TWILL SHORT JACKET": "A short jacket long loved as a brand staple. Cut with a comfortably roomy fit and a slightly relaxed ease, a back tuck creates a three-dimensional silhouette for a clean, beautifully balanced finish. Conceived with a simple, refined presence, side pockets keep the look minimal and elegant. Detail is pared back to the essentials for a grown-up piece that is understated yet full of presence. The buttons are solid water-buffalo horn, made originally for the brand — each with its own matte, natural expression and a premium feel in the hand that gives it a vintage-like charm. The “twill aging” that deepens with wear and washing is another of this jacket's signature charms; enjoy the evolving expression of the cloth, much like denim, over many years. A staple jacket that gains depth with time.",
    "SHEEP SUEDE SHORT JACKET": "A premium short leather jacket made lavishly from thick sheep suede, balanced with a moderate weight.<br>Set into a simple work design, it carries an urban air within its ruggedness.<br>A powerful yet refined leather jacket with the ease of a grown-up.",
    "SHEEPSKIN LEATHER SHIRTS JACKET": "Sheepskin leather, characterized by its supple, soft texture.<br>Light to wear, yet possessed of an elegant luster and a natural expression.<br>It settles onto the body little by little with wear — a material to enjoy leather's inherent aging.<br>A basic, lovable shirt design to wear for years.<br>As the material is delicate, please take care to avoid strong friction and getting it wet.",
    "SUMMER WOOL FR TEE SHIRTS": "A summer-wool tee in 100% wool. A single piece in premium 100% wool, where wool's beautiful drape highlights the quality of the cloth. The neckline is moderately high for a clean, refined impression, while fine stitching at the hem and cuffs adds a subtle accent to the simple design. The silhouette is never overly loose, finished with a well-judged ease. Making the most of the material's stretch, the neck and cuffs use the same cloth — a unifying, premium detail. A summer wool for grown-ups, comfortable even in high summer. Please enjoy the refined hand this material offers.",
    "SUMMER WOOL SLEEVELESS": "A summer-wool tee in 100% wool. A single piece in premium 100% wool, where wool's beautiful drape highlights the quality of the cloth. The neckline is moderately high for a clean, refined impression, while fine stitching at the hem and cuffs adds a subtle accent to the simple design. The silhouette is never overly loose, finished with a well-judged ease. Making the most of the material's stretch, the neck and cuffs use the same cloth — a unifying, premium detail. A summer wool for grown-ups, comfortable even in high summer.<br><br>A 100% wool jersey knit at a high gauge.<br>A tight gauge gives it a moderate crispness and a beautiful drape, with a silk-like, smooth touch. Subtle irregularity, a deep color, and a natural sheen lend an understated sense of quality. It is also given a washable finish for easy home hand-washing — ease of care is one of its charms. A special wool jersey that pairs the hand of a premium material with relaxed, practical wearability.",
    "UNEVEN MOTOR JACKET": "A light-ounce shirting that prizes hand: textured Indian cotton woven loosely, then moderately tightened with a wash finish.<br>It has a hand-woven-like softness and natural irregularity, with each piece carrying a slightly different expression.<br>Light to wear yet strong, it's a daily material you can wear comfortably right through the spring–summer season.",
    "UNEVEN OPEN COLLAR S/S SHIRTS": "An open-collar shirt with the appeal of pared-back design. Simple, yet the collarless cut gives a sharp, modern impression that brings out a masculine air. It handles everything from casual to dressy — an all-rounder for many occasions. Refined and quietly commanding, this open-collar shirt is an essential proposition for the grown-up wardrobe.",
    "WASHI CARDIGAN KNIT": "*A singular lightness and crispness drawn from the qualities of Japanese washi paper. Washi — the distinctive paper developed in Japan since ancient times — is spun in-house here from two yarns of differing texture for a light, crisp hand. Twisted together with synthetic fiber, it evolves into a thoroughly modern material: breathable, lightweight, wrinkle-resistant, and quick-drying with good moisture absorption.",
    "WASHI CREWNECK S/S KNIT": "Washi knit<br><br>“Washi,” the traditional material handed down in Japan since ancient times.<br>A material created by bringing together washi's inherent qualities and modern technology.<br>By twisting two yarns of differing texture using an original technique, it achieves a lightweight hand with a distinctive crispness and a rich, characterful expression.<br>Combined with synthetic fiber, it has evolved into a material of excellent breathability and light weight, plus wrinkle resistance and quick-drying moisture absorption — strong in both function and durability.<br><br>It stays comfortable even in Japan's humid seasons, or in settings where harsh daytime heat and air-conditioned interiors would otherwise leave you chilled.",
    "WASHI L/S CREW KNIT": "A cool, premium summer knit built on a washi base. A light material with a faint sheerness meets washi's characteristic crispness, pleasant against the skin, keeping you cool and comfortable even in summer's heat. Outdoors it quietly screens strong sunlight; indoors it gently guards against the chill of air-conditioning — a surprisingly dependable piece. The silhouette has a moderate ease overall, while a compact neckline keeps it from feeling too relaxed, for an easy, well-put-together impression. Simple yet carefully balanced, it dresses the grown-up in an effortless, natural air. Across Japan's four seasons today it earns its place from early spring through summer and into early autumn. With coolness, comfort, and the quality unique to washi, it's a piece to wear and love for a long time.",
    "WASHI NEP CREWNECK KNIT": "Washi nep knit<br>Carefully knit from washi and cotton yarns, this knit has a singular hand. The use of nep yarn brings rich expression and depth to the surface, while a premium unevenness and an exquisite drape lend a calm, distinctly Japanese impression.",
    "WASHI SKIPPER L/S KNIT": "A cool, premium summer-knit skipper built on a washi base. The collar, with an opening judged just right for grown-up dressing, lends a well-measured sense of ease. A light material with a faint sheerness meets washi's characteristic crispness, gentle against the skin, for cool, comfortable wear even in the muggy season. The silhouette has a moderate ease overall, while a neatly compact neckline keeps it from going too casual — a finish with grown-up composure. Simple yet carefully balanced, it gives off an effortless, natural air. A piece to wear from early spring through summer and into early autumn, across the shifting of Japan's four seasons. With coolness, comfort, and the quality unique to washi, it's a summer knit you'll want to treasure for years.",
    "WOOL LINEN MILLING CAP": "Wool milling fabric (textured, fulled wool). The fulling brings out a naturally deep, dimensional surface — a weightlessness as if it holds air, with a quiet but solid presence. A blend of linen adds refined softness along with a moderate crispness and dry hand. The uneven, textured cloth, evocative of the best of Japanese craft, carries a distinctly Japanese sensibility.",
    "WOOL LINEN MILLING COVER COACH JACKET": "A distinctive design fusing elements of a coverall and a coach jacket.<br>A roomy body width gives it a balance that feels refined within its ruggedness — a coverall finished with poise.<br><br>Wool milling fabric (textured, fulled wool). The fulling brings out a naturally deep, dimensional surface — a weightlessness as if it holds air, with a quiet but solid presence. A blend of linen adds refined softness along with a moderate crispness and dry hand. The uneven, textured cloth, evocative of the best of Japanese craft, carries a distinctly Japanese sensibility.",
    "WOOL MILLING OVER COAT": "An over jacket that reinterprets military design through alvana's own lens.<br>Rugged in spirit, yet shaped with a contemporary silhouette and a light, easy balance — a new take on military wear that settles naturally into everyday life.<br><br>Wool milling fabric (textured, fulled wool). The fulling brings out a naturally deep, dimensional surface — a weightlessness as if it holds air, with a quiet but solid presence. A blend of linen adds refined softness along with a moderate crispness and dry hand. The uneven, textured cloth, evocative of the best of Japanese craft, carries a distinctly Japanese sensibility.",
    "空紡 CLASSIC PK TEE SHIRTS": "A short-sleeve tee knit from a custom open-end (air-spun) yarn developed with Japan's climate in mind, finished with a fabric feel that is “just right.” Plump and pleasantly substantial yet knit at high density, it has a distinctive firmness and a dry, smooth touch; highly moisture-absorbing, it earns daily wear all season long. The relaxed, beautifully balanced silhouette is set with a slightly shorter body length. A simple crew-neck design that lets the material speak, finished with careful stitching — at home dressed down, or styled up with slacks for a grown-up air. Tough enough to resist going limp wash after wash, it grows more comfortable and full of character the more you wear it.",
    "空紡 L/S TEE SHIRTS": "A tee knit from a custom open-end (air-spun) yarn developed with Japan's climate in mind, finished with a fabric feel that is “just right.” Plump and pleasantly substantial yet knit at high density, it has a distinctive firmness and a dry, smooth touch; highly moisture-absorbing, it earns daily wear all season long. The relaxed, beautifully balanced silhouette is set with a slightly shorter body length. A simple crew-neck design that lets the material speak, finished with careful stitching — at home dressed down, or styled up with slacks for a grown-up air. Tough enough to resist going limp wash after wash, it grows more comfortable and full of character the more you wear it.<br><br>KŪBŌ (air-spun) jersey<br>A cloth with a clean face, a moderate crispness, and a pleasant, non-clinging touch. Knit tightly from 18-count yarn for a sturdy, substantial finish — a well-balanced, all-season staple. Fuzz is kept down for a crisp hand, with an understated sense of quality and a dry wearing comfort. The yarn is an open-end yarn spun from short, thick fibers, giving the material its characteristic toughness and well-judged refinement — a grown-up, casual cloth.",
    "空紡 MIDDLENECK ROUND L/S TEE SHIRTS": "KŪBŌ (air-spun) jersey<br>A cloth with a clean face, a moderate crispness, and a pleasant, non-clinging touch. Knit tightly from 18-count yarn for a sturdy, substantial finish — a well-balanced, all-season staple. Fuzz is kept down for a crisp hand, with an understated sense of quality and a dry wearing comfort. The yarn is an open-end yarn spun from short, thick fibers, giving the material its characteristic toughness and well-judged refinement — a grown-up, casual cloth.",
    "空紡 S/S TEE SHIRTS": "A short-sleeve tee knit from a custom open-end (air-spun) yarn developed with Japan's climate in mind, finished with a fabric feel that is “just right.” Plump and pleasantly substantial yet knit at high density, it has a distinctive firmness and a dry, smooth touch; highly moisture-absorbing, it earns daily wear all season long. The relaxed, beautifully balanced silhouette is set with a slightly shorter body length. A simple crew-neck design that lets the material speak, finished with careful stitching — at home dressed down, or styled up with slacks for a grown-up air. Tough enough to resist going limp wash after wash, it grows more comfortable and full of character the more you wear it.",
    "空紡 SLEEVELESS TEE SHIRTS": "A sleeveless tee knit from a custom open-end (air-spun) yarn developed with Japan's climate in mind, finished with a fabric feel that is “just right.” Plump and pleasantly substantial yet knit at high density, it has a distinctive firmness and a dry, smooth touch; highly moisture-absorbing, it earns daily wear all season long. The relaxed, beautifully balanced silhouette is set with a slightly shorter body length. A simple crew-neck design that lets the material speak, finished with careful stitching. Tough enough to resist going limp wash after wash, it grows more comfortable and full of character the more you wear it.<br><br>KŪBŌ (air-spun) jersey<br>A cloth with a clean face, a moderate crispness, and a pleasant, non-clinging touch. Knit tightly from 18-count yarn for a sturdy, substantial finish — a well-balanced, all-season staple. Fuzz is kept down for a crisp hand, with an understated sense of quality and a dry wearing comfort. The yarn is an open-end yarn spun from short, thick fibers, giving the material its characteristic toughness and well-judged refinement — a grown-up, casual cloth.",
    "空紡 TANK TOP TEE SHIRTS": "An original alvana jersey developed with an air-filled open-end yarn. A soft, plump wearing comfort with a moderate crispness — a pleasant hand imagined to suit Japan's four seasons. With room through the body, it has a relaxed silhouette that doesn't cling. Easy in its comfort yet balanced in length, never too long; the armholes have ease too, so when you lower your arms the cloth falls into a clean drape. The neckline and armholes are binder-finished, slipping on and settling onto the body without any tightness. It works easily as an inner under a loose top — breezy and comfortable. Tough enough to resist going limp wash after wash, it grows more comfortable and full of character the more you wear it.",
}

FIBER = [
    ("表地", "Shell"),
    ("裏地", "Lining"),
    ("リブ部分", "Rib"),
    ("リブ", "Rib"),
    ("別布", "Contrast"),
    ("植物繊維（ヘンプ）", "Hemp"),
    ("植物繊維", "Plant fiber"),
    ("ヘンプ", "Hemp"),
    ("和紙", "Washi (Japanese paper)"),
    ("羊革", "Sheep Leather"),
    ("コットン", "Cotton"),
    ("綿", "Cotton"),
    ("ウール", "Wool"),
    ("リネン", "Linen"),
    ("麻", "Linen"),
    ("ナイロン", "Nylon"),
    ("ポリエステル", "Polyester"),
    ("ポリウレタン", "Polyurethane"),
    ("レーヨン", "Rayon"),
    ("キュプラ", "Cupra"),
    ("POLYESTEL", "Polyester"),
    ("POLYESTER", "Polyester"),
    ("POLYURETHANE", "Polyurethane"),
    ("COTTON", "Cotton"),
    ("WOOL", "Wool"),
    ("NYLON", "Nylon"),
    ("CUPRA", "Cupra"),
    ("LAMBSKIN", "Lambskin"),
    ("SHEEP LEATHER", "Sheep Leather"),
]


def translate_material(s):
    if not s:
        return s
    out = s.replace("：", ": ").replace("％", "%")
    for ja, en in FIBER:
        out = out.replace(ja, en)
    out = re.sub(r"([A-Za-z])(\d)", r"\1 \2", out)  # Cotton100% -> Cotton 100%
    return re.sub(r"[ \t]+", " ", out).strip()


def td_after(html, th):
    m = re.search(r"<th>\s*" + th + r"\s*</th>\s*<td>(.*?)</td>", html, re.S)
    return m.group(1).strip() if m else ""


def main():
    dq = "query($id: ID!) { product(id: $id) { descriptionHtml } }"
    tq = 'query($id: ID!) { translatableResource(resourceId: $id) { translations(locale: "en") { key outdated } } }'
    products = [
        p
        for p in client.products_by_query("")
        if p["status"] == "ACTIVE" and "(no image)" not in p["title"]
    ]
    # group by JA prose to resolve shared copy
    by_prose = {}
    rows_meta = []
    for p in products:
        html = client.run_query(dq, {"id": p["id"]})["product"]["descriptionHtml"] or ""
        mp = re.search(r"<p[^>]*>(.*?)</p>", html, re.S)
        if not mp:
            continue
        prose = mp.group(1).strip()
        en = client.run_query(tq, {"id": p["id"]})["translatableResource"][
            "translations"
        ]
        body = [t for t in en if t["key"] == "body_html"]
        status = (
            "outdated"
            if (body and body[0]["outdated"])
            else ("missing" if not body else "ok")
        )
        meta = {
            "title": p["title"],
            "prose": prose,
            "status": status,
            "material": td_after(html, "素材"),
            "origin": td_after(html, "原産国"),
            "hinban": td_after(html, "品番"),
        }
        rows_meta.append(meta)
        by_prose.setdefault(prose, []).append(meta)

    # map each prose group to an EN draft via any representative title present in EN_PROSE
    en_for_prose = {}
    unmatched = set()
    for prose, group in by_prose.items():
        en = next((EN_PROSE[m["title"]] for m in group if m["title"] in EN_PROSE), None)
        en_for_prose[prose] = en or ""
        if en is None and prose:
            unmatched.add(group[0]["title"])

    header = [
        "Title",
        "品番",
        "EN status",
        "JA prose",
        "EN prose (draft — edit here)",
        "JA material",
        "EN material (draft)",
        "Origin",
    ]
    out = [header]
    for m in sorted(rows_meta, key=lambda x: x["title"]):
        out.append(
            [
                m["title"],
                m["hinban"],
                m["status"],
                m["prose"],
                en_for_prose.get(m["prose"], ""),
                m["material"],
                translate_material(m["material"]),
                m["origin"],
            ]
        )

    ws = client.gspread_client.open_by_key(REVIEW_SHEET_ID).worksheet(REVIEW_TAB)
    ws.clear()
    ws.update(out, "A1")
    print(f"wrote {len(out) - 1} rows to '{REVIEW_TAB}'")
    if unmatched:
        print("NO EN DRAFT for prose groups repr by:", sorted(unmatched))


if __name__ == "__main__":
    main()
