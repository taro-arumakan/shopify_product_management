"""Known overseas package-forwarder / consolidation warehouses and member-code
signatures used to detect lememe orders the Korea->Japan personal-import lane cannot
deliver (see the rerouting rule). Soft signal: matches are tagged for CS review, not
blocked, so the list does not need to be exhaustive — grow it as new hubs surface.
"""

# Confirmed forwarder warehouses. A SHIPPING address matching `zip` AND containing
# `address_contains` (after NFKC normalization) is treated as a forwarder hub.
FORWARDER_HUBS = [
    {
        # 〒306-0608 茨城県坂東市幸神平1 C棟 (Buyandship Japan 合同会社)
        "service": "Buyandship",
        "zip": "306-0608",
        "address_contains": "幸神平",
        "source": "https://www.buyandship.co.jp/shipment-law/",
    },
]

# Member-code prefixes some forwarders prepend to the recipient name / address line.
# Buyandship codes look like "BS" + alphanumerics (e.g. BSZGRXHZ, BSNPWYHR).
FORWARDER_CODE_PREFIXES = [
    {"service": "Buyandship", "prefix": "BS"},
]

# Addresses that recur across distinct buyers and MAY be forwarders, but lack a
# member-code signature. Surfaced for human review before promotion to FORWARDER_HUBS;
# NOT auto-tagged (avoids false positives on legitimate repeat customers).
CANDIDATE_HUBS = [
    {"zip": "620-0221", "address_contains": "雲原", "note": "x5; verify"},
]
