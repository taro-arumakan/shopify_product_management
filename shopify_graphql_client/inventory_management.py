class InventoryManagement:
    """
    This class provides methods to manage inventory in a Shopify store. Inherited by the ShopifyGraphqlClient class.
    """

    """ inventory management """
    def location_id_by_name(self, name):
        query = '''
        {
            locations(first:10, query:"name:%s") {
                nodes {
                    id
                }
            }
        }
        ''' % name
        res = self.run_query(query)
        res = res['locations']['nodes']
        assert len(res) == 1, f'{"Multiple" if res else "No"} locations found for {name}: {res}'
        return res[0]['id']

    def inventory_item_id_by_sku(self, sku):
        query = '''
        {
            inventoryItems(query:"sku:%s", first:5) {
                nodes{
                    id
                }
            }
        }''' % sku
        res = self.run_query(query)
        res = res['inventoryItems']['nodes']
        assert len(res) == 1, f'{"Multiple" if res else "No"} inventoryItems found for {sku}: {res}'
        return res[0]['id']

    def set_inventory_quantity_by_sku_and_location_id(self, sku, location_id, quantity):
        inventory_item_id = self.inventory_item_id_by_sku(sku)
        query = '''
        mutation inventorySetQuantities($locationId: ID!, $inventoryItemId: ID!, $quantity: Int!) {
            inventorySetQuantities(
                input: {name: "available", ignoreCompareQuantity: true, reason: "correction",
                        quantities: [{inventoryItemId: $inventoryItemId,
                                    locationId: $locationId,
                                    quantity: $quantity}]}
            ) {
                inventoryAdjustmentGroup {
                    id
                    changes {
                        name
                        delta
                        quantityAfterChange
                    }
                    reason
                }
                userErrors {
                    message
                    code
                    field
                }
            }
        }
        '''
        variables = {
            "inventoryItemId": inventory_item_id,
            "locationId": location_id,
            "quantity": quantity
        }
        res = self.run_query(query, variables)
        if res['inventorySetQuantities']['userErrors']:
            raise Exception(f"Error updating inventory quantity: {res['inventorySetQuantities']['userErrors']}")
        updates = res['inventorySetQuantities']['inventoryAdjustmentGroup']
        if not updates:
            self.logger.info(f'no updates found after updating inventory of {sku} to {quantity}')
        return updates
