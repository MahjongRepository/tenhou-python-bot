import pytest


@pytest.fixture(scope="session", autouse=True)
def do_something(request):
    pass
    # uncomment it if you want to have logs in tests
    # from utils.logger import set_up_logging
    # set_up_logging(save_to_file=False)
