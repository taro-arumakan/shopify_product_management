"""Check the local copy of the EPOKHE Dropbox share against the SKU mapping.

    python -m brands.leisureallstars.verify_local_images [local_root]

Prints one line per mapped SKU and, at the end, the Dropbox folders that still
need downloading. The share was pulled folder-by-folder, so partial downloads
are the norm rather than the exception -- run this before any product create.
"""

import os
import sys
import urllib.parse

from brands.leisureallstars import image_mapping as m

EXPECTED_MIN = 4  # every colourway shot so far has 5-6 images


def report(root=None):
    ok, problems = [], []
    for sku, (path, prefix, confidence, _note) in m.SKU_IMAGE_SOURCE.items():
        if confidence == m.TODO:
            continue
        files = m.local_files(sku, root)
        roots = (root,) if root else m.LOCAL_ROOTS
        directory = next(
            (d for d in (m.local_dir(sku, r) for r in roots) if d and os.path.isdir(d)),
            None,
        )
        if not directory:
            problems.append((sku, path, "folder not downloaded"))
        elif not files:
            problems.append((sku, path, "folder is empty"))
        elif len(files) < EXPECTED_MIN:
            problems.append((sku, path, f"only {len(files)} images"))
        else:
            ok.append((sku, len(files), directory))

    for sku, count, directory in ok:
        print(f"  OK   {sku:20} {count:>2} files  {directory}")
    for sku, path, why in problems:
        print(f"  --   {sku:20} {why:22} {path}")

    print(f"\n{len(ok)} of {len(ok) + len(problems)} mapped SKUs have images locally.")

    if problems:
        print(
            "\nDownload these folders individually -- a folder-level download of\n"
            "1_COLLECTION omits them every time:"
        )
        for path in sorted({p for _s, p, _w in problems}):
            full = path if path.startswith("/") else f"{m.EYEWEAR_ROOT}/{path}"
            print(f"  {m.SHARED_LINK_ROOT}{urllib.parse.quote(full)}?dl=0")
    return not problems


if __name__ == "__main__":
    sys.exit(0 if report(*sys.argv[1:2]) else 1)
