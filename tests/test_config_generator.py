import json
from pathlib import Path
from doc_flesh.configtools.siteinfo_generator import handle_existing_siteinfo
from doc_flesh.models import SiteInfo

VALID = Path("tests/data/valid.siteinfo.json")
NONEXT = Path("tests/data/nonexistent.siteinfo.json")
PARTIAL = Path("tests/data/partial.siteinfo.json")

def test_handle_existing_siteinfo():
    """Test handle_existing_siteinfo function."""
    result = handle_existing_siteinfo(VALID)

    expected = json.loads(VALID.read_text())

    assert isinstance(result, SiteInfo)
    assert result.site_name == expected["site_name"]
    assert result.site_name_slug == expected["site_name_slug"]
    assert result.category == expected["category"]
    assert result.related_repo == expected["related_repo"]

def test_handle_existing_siteinfo_no_file():
    """Test handle_existing_siteinfo function with siteinfo.json missing completely."""
    result = handle_existing_siteinfo(NONEXT)

    assert isinstance(result, SiteInfo)
    assert result.site_name == ""
    assert result.site_name_slug == "data" # Parent directory name is offered by default
    assert result.category == "Learning tools"
    assert result.related_repo == ""


def test_handle_existing_siteinfo_partial():
    """Test handle_existing_siteinfo function with partial file."""
    result = handle_existing_siteinfo(PARTIAL)

    expected = json.loads(PARTIAL.read_text())

    assert isinstance(result, SiteInfo)
    assert result.site_name == "" 
    assert result.site_name_slug == "data" # Parent directory name is offered by default
    assert result.category == expected["category"]
    assert result.related_repo == ""
