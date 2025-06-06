handles = """mellow-cap
tom-sawyer-safari-hat
plant-seersucker-ball-cap
babycot-ivy-frill-bonnet
babycot-rabbit-dot-bonnet
babycot-cloudy-denim-cap
babycot-haven-ruffle-knit-bonnet
babycot-haven-knit-bonnet
babycot-citrus-knit-bonnet
babycot-cake-knit-bonnet
babycot-caper-bucket-hat""".split(
    "\n"
)

import utils

client = utils.client("apricot-studios")
for handle in handles:
    product = client.product_by_handle(handle)
    tags = product["tags"] + ["hat"]
    client.update_product_tags(product["id"], ",".join(tags))
