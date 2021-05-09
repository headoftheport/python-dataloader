import logging

from .main import dataloader
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()

formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)







