import collections
import logging
from helpers.exceptions import (
    NoProductsFoundException,
    MultipleProductsFoundException,
)

logger = logging.getLogger(__name__)


class SanityChecks:

    def check_size_field(self, product_info_list, raise_on_error=True):
        res = []
        for product_info in product_info_list:
            try:
                size_text = self.get_size_field(product_info)
            except Exception as e:
                m = f"Error formatting size text for {product_info['title']}: {e}"
                if raise_on_error:
                    logger.error(m)
                    raise
                else:
                    res.append(m)
            else:
                if raise_on_error:
                    print(size_text)
        return res

    def check_description(self, product_info_list, raise_on_error=True):
        res = []
        for product_info in product_info_list:
            try:
                description_html = self.get_description_html(product_info)
            except Exception as e:
                m = f"Error formatting description for {product_info['title']}: {e}"
                if raise_on_error:
                    logger.error(m)
                    raise
                else:
                    res.append(m)
            else:
                if raise_on_error:
                    print(description_html)
        return res

    def check_drive_image(self, product_info_list):
        res = []
        for product_info in product_info_list:
            try:
                drive_ids, _ = self.populate_drive_ids_and_skuss(product_info)
                for drive_id in drive_ids:
                    image_details = self.get_drive_image_details(drive_id)
                    if not image_details:
                        res.append(
                            f"Missing or inaccessible drive image for {product_info['title']}: {drive_id}"
                        )
            except Exception as e:
                res.append(
                    f"Error checking drive images for {product_info['title']}: {e}"
                )
        return res

    def product_info_to_skus(self, product_info):
        options = self.populate_option_dicts(product_info)
        return [o["sku"] for o in options]

    def check_sku_duplicates(self, product_info_list):
        skus = sum([self.product_info_to_skus(pi) for pi in product_info_list], [])
        counts_by_sku = collections.Counter(skus)
        counts_by_sku = {
            sku: count for sku, count in counts_by_sku.items() if count > 1
        }
        if counts_by_sku:
            m = "\n".join(
                ": ".join(map(str, [sku, count]))
                for sku, count in counts_by_sku.items()
            )
            raise RuntimeError(f"Duplicate SKUs found:\n{m}")

    def check_existing_skus(self, product_info_list):
        res = []
        skus = sum((self.product_info_to_skus(pi) for pi in product_info_list), [])
        query = query = " OR ".join(f"sku:'{sku}'" for sku in skus)
        exists = self.product_variants_by_query(query)
        for r in exists:
            res.append(f"Existing SKU found: {r['product']['title']} - {r['sku']}")
        return res

    def check_existing_products(self, product_info_list):
        res = []
        for pi in product_info_list:
            try:
                checking = "handle" if "handle" in pi else "title"
                func = getattr(self, f"product_by_{checking}")
                param = pi[checking]
                func(param)
            except NoProductsFoundException:
                pass
            except MultipleProductsFoundException:
                res.append(f"Existing product found by {checking}: {param}")
            else:
                res.append(f"Existing product found by {checking}: {param}")
        return res

    def sanity_check_product_info_list(self, product_info_list):
        res = []
        try:
            self.check_sku_duplicates(product_info_list)
        except RuntimeError as e1:
            logger.error(e1)
            res.append(e1)
        res = self.check_existing_skus(product_info_list)
        res += self.check_existing_products(product_info_list)
        res += self.check_size_field(product_info_list, raise_on_error=False)
        res += self.check_description(product_info_list, raise_on_error=False)
        res += self.check_drive_image(product_info_list)
        for r in res:
            logger.error(r)

        if res:
            raise RuntimeError("Failed sanity check")
