from pathlib import Path
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


@pytest.fixture
def normal_hand_text():
    return load_fixture("normal_hand.txt")


@pytest.fixture
def fast_fold_hand_text():
    return load_fixture("fast_fold_hand.txt")


@pytest.fixture
def showdown_hand_text():
    return load_fixture("showdown_hand.txt")


@pytest.fixture
def run_it_twice_hand_text():
    return load_fixture("run_it_twice_hand.txt")


@pytest.fixture
def multi_hand_text():
    return load_fixture("multi_hand.txt")


@pytest.fixture
def bb_call_hand_text():
    return load_fixture("bb_call_hand.txt")
