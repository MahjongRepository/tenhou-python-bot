import pytest
from utils.logger import set_up_logging


@pytest.fixture(scope="session", autouse=True)
def do_something(request):
    set_up_logging(save_to_file=False)
