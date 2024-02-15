import requests
from typing import Optional
from config_data.config import head
from utils.misc.logging import logger


def get_request(param: dict) -> Optional[dict]:
    url = "https://currency-conversion-and-exchange-rates.p.rapidapi.com/convert"
    try:
        response = requests.get(
            url=url,
            headers=head,
            params=param
        )
    except requests.RequestException as error:
        logger.log_error(f"Error processing message: {str(error)}")
        return None
    logger.log_debug(f"Status code: {response.status_code}")
    if response.status_code == requests.codes.ok:
        return response.json()

