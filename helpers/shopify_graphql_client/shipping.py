import logging
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)


class Shipping:
    def delivery_profiles(self):
        query = """
        query GetDeliveryProfiles {
            deliveryProfiles(first: 50, merchantOwnedOnly: true) {
                nodes {
                    id
                    name
                    profileLocationGroups {
                        locationGroup {
                            id
                        }
                        locationGroupZones(first: 50) {
                            nodes {
                                zone {
                                    id
                                    name
                                }
                                methodDefinitions(first: 50) {
                                    nodes {
                                        id
                                        name
                                        rateProvider {
                                            __typename
                                            ... on DeliveryRateDefinition {
                                                id
                                                price { amount currencyCode }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        res = self.run_query(query)
        return res["deliveryProfiles"]["nodes"]

    def update_delivery_profile(self, profile_id, profile_input):
        mutation = """
        mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) {
            deliveryProfileUpdate(id: $id, profile: $profile) {
                profile { id name }
                userErrors { field message }
            }
        }
        """
        res = self.run_query(mutation, {"id": profile_id, "profile": profile_input})
        if user_errors := res["deliveryProfileUpdate"]["userErrors"]:
            raise RuntimeError(f"Error updating delivery profile: {user_errors}")
        return res["deliveryProfileUpdate"]["profile"]

    def delivery_profile_by_name(self, name="General profile"):
        res = self.delivery_profiles()
        for dp in res:
            if dp["name"] == name:
                return dp
        else:
            raise RuntimeError(f"profile {name} not found")

    def location_group_zone_by_name(self, delivery_profile, zone_name):
        location_groups = delivery_profile["profileLocationGroups"]
        assert (
            len(location_groups) == 1
        ), f"multiple location zones not supported: {location_groups}"
        for location_group_zone in location_groups[0]["locationGroupZones"]["nodes"]:
            if location_group_zone["zone"]["name"] == zone_name:
                return location_group_zone
        raise RuntimeError(
            f"zone {zone_name} not found in profile {delivery_profile['name']}"
        )

    @staticmethod
    def _condition_id_from_method_definition_id(method_definition_id):
        """Conditional rates are returned as the base method definition id with a
        `?source=RateRangeCondition&source_id=<id>` suffix. Pull out the condition id.
        """
        source_id = parse_qs(urlparse(method_definition_id).query).get(
            "source_id", [None]
        )[0]
        if not source_id:
            return None
        return f"gid://shopify/DeliveryCondition/{source_id}"

    def update_delivery_flat_rate(
        self,
        new_price,
        profile_name="General profile",
        zone_name="国内配送",
        currency_code="JPY",
        new_method_name=None,
        testrun=True,
    ):
        """Update the flat rate for a zone, deleting any conditional ("discount")
        rates such as a free-shipping campaign, and optionally renaming the method."""
        dp = self.delivery_profile_by_name(profile_name)
        profile_id = dp["id"]
        location_group = dp["profileLocationGroups"][0]
        zone = self.location_group_zone_by_name(dp, zone_name)
        method_nodes = zone["methodDefinitions"]["nodes"]

        base_method = next(m for m in method_nodes if "?" not in m["id"])
        condition_ids = [
            condition_id
            for m in method_nodes
            if (condition_id := self._condition_id_from_method_definition_id(m["id"]))
        ]

        method_input = {
            "id": base_method["id"],
            "rateDefinition": {
                "id": base_method["rateProvider"]["id"],
                "price": {"amount": str(new_price), "currencyCode": currency_code},
            },
        }
        if new_method_name is not None:
            method_input["name"] = new_method_name

        profile_input = {
            "locationGroupsToUpdate": [
                {
                    "id": location_group["locationGroup"]["id"],
                    "zonesToUpdate": [
                        {"id": zone["id"], "methodDefinitionsToUpdate": [method_input]}
                    ],
                }
            ],
        }
        if condition_ids:
            profile_input["conditionsToDelete"] = condition_ids

        logger.info(
            f"Updating {profile_name} / {zone_name}: "
            f"'{base_method['name']}' ({base_method['rateProvider']['price']['amount']} "
            f"{base_method['rateProvider']['price']['currencyCode']}) "
            f"-> '{new_name or base_method['name']}' ({new_price} {currency_code}); "
            f"deleting {len(condition_ids)} condition(s)"
        )
        if testrun:
            logger.info("Test run mode - no changes will be made")
            return profile_input
        else:
            return self.update_delivery_profile(profile_id)


def main():
    import utils

    client = utils.client("dev")
    import pprint

    pprint.pprint(
        client.update_delivery_flat_rate(
            profile_name="General profile",
            zone_name="国内配送",
            new_price=880,
            new_method_name="通常配送 お支払い完了から10-14日を目安にお届けします",
            testrun=True,
        )
    )


if __name__ == "__main__":
    main()
