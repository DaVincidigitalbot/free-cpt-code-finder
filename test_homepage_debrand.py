from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_homepage_title_and_metadata_do_not_use_cyrionyx_branding():
    assert '<title>Free CPT Code Finder — Search CPT & ICD-10 Codes Instantly</title>' in INDEX_HTML
    assert 'content="Free CPT Code Finder — Search CPT & ICD-10 Codes Instantly"' in INDEX_HTML
    assert 'Cyrionyx – Free CPT Code Finder' not in INDEX_HTML
    assert 'content="CYRIONYX"' not in INDEX_HTML


def test_homepage_top_shell_does_not_include_cyrionyx_header_markup():
    assert 'Powered by <a href="/"' not in INDEX_HTML
    assert 'class="cyrionyx-header"' not in INDEX_HTML
    assert 'About CYRIONYX' not in INDEX_HTML
    assert '<body class="brand-shell">' not in INDEX_HTML


def test_homepage_uses_freecptcodefinder_header_and_tagline():
    assert '<header class="header" id="main-header">' in INDEX_HTML
    assert 'FreeCPTCodeFinder' in INDEX_HTML
    assert 'Find the exact CPT or ICD-10 code in seconds' in INDEX_HTML
    assert "CYRIONYX medical coding platform" not in INDEX_HTML


def test_bottom_specialty_links_remain_present():
    assert 'id="bottomSpecialtyLinks"' in INDEX_HTML
    assert 'Browse by Specialty' in INDEX_HTML
