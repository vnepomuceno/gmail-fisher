from emoji import emojize


def success(message: str, data: dict):
    data_output = _output_data(data)
    print(f"{emojize(':check_mark:  ')} {message}{data_output}")


def info(message: str, data: dict):
    data_output = _output_data(data)
    print(f"{message}{data_output}")


def warning(message: str, data: dict):
    data_output = _output_data(data)
    print(f"{emojize(':warning:   ')} {message}{data_output}")


def _output_data(data: dict) -> str:
    data_output = ""
    if data.__sizeof__() != 0:
        data_output += f", with data {data}"
    return data_output
