import logging
import os
import pprint
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("apricot-studios")
    local_dir = r"/Users/taro/Downloads/model_info_translation"
    paths = [os.path.join(local_dir, fn) for fn in sorted(os.listdir(local_dir))]

    res = client.replace_image_files(paths)
    pprint.pprint(res)


if __name__ == "__main__":
    main()
