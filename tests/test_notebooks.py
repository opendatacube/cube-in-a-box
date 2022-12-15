from pathlib import Path
from testbook import testbook

TEST_DIR = Path(__file__).parent.parent.resolve()
NB_DIR = TEST_DIR.parent


@testbook(f'{NB_DIR}/notebooks/Indexing_More_Data.ipynb', execute=True, timeout=180)
def test_indexing_more_data(tb):
    assert True  # ok


@testbook(f'{NB_DIR}/notebooks/ESRI_Land_Cover.ipynb', execute=True, timeout=180)
def test_esri_land_cover(tb):
    assert True  # ok


@testbook(f'{NB_DIR}/notebooks/NASADEM.ipynb', execute=True, timeout=180)
def test_nasadem(tb):
    assert True  # ok


@testbook(f'{NB_DIR}/notebooks/Sentinel_2.ipynb', execute=True, timeout=180)
def test_sentinel_2(tb):
    assert True  # ok