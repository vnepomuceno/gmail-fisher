import json

from gmail_fisher import logger


class JsonUtils:
    @classmethod
    def load_dict_from_json(cls, filters_path):
        with open(filters_path) as filters:
            json_content = filters.read()

        filters_dict = json.loads(json_content)

        return filters_dict

    @classmethod
    def write_to_json_file(cls, json_content, json_path):
        file = open(json_path, "w")
        file.write(json_content)
        file.close()
        logger.success(f"Successfully written results to {json_path=}")
