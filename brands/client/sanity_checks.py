import collections
import logging
from helpers.exceptions import (
    NoProductsFoundException,
    MultipleProductsFoundException,
)

logger = logging.getLogger(__name__)


class SanityChecks:

    def check_size_field(self, product_inputs, raise_on_error=True):
        res = []
        for product_input in product_inputs:
            try:
                size_text = self.get_size_field(product_input)
            except Exception as e:
                m = f"Error formatting size text for {product_input['title']}: {e}"
                if raise_on_error:
                    logger.error(m)
                    raise
                else:
                    res.append(m)
            else:
                if raise_on_error:
                    print(size_text)
        return res

    def check_description(self, product_inputs, raise_on_error=True):
        res = []
        for product_input in product_inputs:
            try:
                description_html = self.get_description_html(product_input)
            except Exception as e:
                m = f"Error formatting description for {product_input['title']}: {e}"
                if raise_on_error:
                    logger.error(m)
                    raise
                else:
                    res.append(m)
            else:
                if raise_on_error:
                    print(description_html)
        return res

    def check_drive_image(self, product_inputs):
        res = []
        for product_input in product_inputs:
            try:
                drive_ids, _ = self.populate_drive_ids_and_skuss(product_input)
                for drive_id in drive_ids:
                    image_details = self.get_drive_image_details(drive_id)
                    if not image_details:
                        res.append(
                            f"Missing or inaccessible drive image for {product_input['title']}: {drive_id}"
                        )
            except Exception as e:
                res.append(
                    f"Error checking drive images for {product_input['title']}: {e}"
                )
        return res

    def check_sku_duplicates(self, product_inputs):
        skus = sum([self.product_input_to_skus(pi) for pi in product_inputs], [])
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

    def check_existing_skus(self, product_inputs):
        res = []
        skus = sum((self.product_input_to_skus(pi) for pi in product_inputs), [])
        query = query = " OR ".join(f"sku:'{sku}'" for sku in skus)
        exists = self.product_variants_by_query(query)
        for r in exists:
            res.append(f"Existing SKU found: {r['product']['title']} - {r['sku']}")
        return res

    def check_existing_products(self, product_inputs):
        res = []
        for pi in product_inputs:
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

    def sanity_check_product_inputs(self, product_inputs, ignore_product_titles=None):
        product_inputs = [
            pi
            for pi in product_inputs
            if pi["title"] not in (ignore_product_titles or [])
        ]
        res = []
        try:
            self.check_sku_duplicates(product_inputs)
        except RuntimeError as e1:
            logger.error(e1)
            res.append(e1)
        res = self.check_existing_skus(product_inputs)
        res += self.check_existing_products(product_inputs)
        res += self.check_size_field(product_inputs, raise_on_error=False)
        res += self.check_description(product_inputs, raise_on_error=False)
        res += self.check_drive_image(product_inputs)
        for r in res:
            logger.error(r)

        if res:
            raise RuntimeError("Failed sanity check")

    def sanity_check_sheet(
        self, sheet_name, handle_suffix=None, ignore_product_titles=None
    ):
        product_inputs = self.product_inputs_by_sheet_name(
            sheet_name, handle_suffix=handle_suffix
        )
        logger.info(
            f"Sanity checking {len(product_inputs)} products from sheet {sheet_name}"
        )
        return self.sanity_check_product_inputs(
            product_inputs, ignore_product_titles=ignore_product_titles
        )
