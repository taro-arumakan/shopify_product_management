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

    def enable_and_activate_inventory(self, sku, location_names):
        inventory_item_id = self.inventory_item_id_by_sku(sku)
        ress = [self.enable_inventory_tracking(inventory_item_id)]
        for location_name in location_names:
            ress.append(self.activate_inventory_item(inventory_item_id,
                                                     self.location_id_by_name(location_name)))
        return ress

    def enable_inventory_tracking(self, inventory_item_id):
        query = """
        mutation inventoryItemUpdate($id: ID!) {
            inventoryItemUpdate(id: $id, input: {
                                                   tracked: true
                                                }) {
                inventoryItem {
                    id
                    tracked
                }
                userErrors {
                    message
                }
            }
        }
        """
        variables = {
            'id': inventory_item_id,
            'input': {
                'tracked': "true"
            }
        }
        res = self.run_query(query, variables)
        if res['inventoryItemUpdate']['userErrors']:
            raise Exception(f"Error updating inventory quantity: {res['inventoryItemUpdate']['userErrors']}")
        return res['inventoryItemUpdate']['inventoryItem']

    def activate_inventory_item(self, inventory_item_id, location_id, available=0):
        query = '''
        mutation ActivateInventoryItem($inventoryItemId: ID!, $locationId: ID!%s) {
          inventoryActivate(inventoryItemId: $inventoryItemId, locationId: $locationId%s) {
                inventoryLevel {
                    id
                    quantities(names: ["available"]) {
                        name
                        quantity
                    }
                    item {
                        id
                    }
                    location {
                        id
                    }
                }
                userErrors {
                    field
                    message
                }
            }
        }
        ''' % ((', $available: Int', ', available: $available') if available else ('', ''))
        variables = {
            'inventoryItemId': inventory_item_id,
            'locationId': location_id,
            }
        if available:
            variables['available'] = available
        res = self.run_query(query, variables)
        if user_errors := res['inventoryActivate']['userErrors']:
            raise RuntimeError(f'Failed to activate an inventory item: {user_errors}')
        return res['inventoryActivate']['inventoryLevel']

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
