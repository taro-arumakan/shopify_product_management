import utils


def main():

    client = utils.client("ssil")
    import pprint

    pprint.pprint(
        client.update_delivery_flat_rate(
            profile_name="General profile",
            zone_name="国内配送",
            new_price=880,
            new_method_name="通常配送 お支払い完了から10-14日を目安にお届けします",
            testrun=False,
        )
    )


if __name__ == "__main__":
    main()
