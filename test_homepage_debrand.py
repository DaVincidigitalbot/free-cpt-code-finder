from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_homepage_title_and_metadata_use_current_branding():
    assert '<title>FreeCPTCodeFinder.com | CPT Code Lookup, wRVUs, Modifiers & Case Builder</title>' in INDEX_HTML
    assert 'Free CPT code lookup for medical students, residents, APPs, surgeons, and coders.' in INDEX_HTML
    assert 'content="FreeCPTCodeFinder.com"' in INDEX_HTML
    assert 'CYRIONYX' not in INDEX_HTML
    assert 'Cyrionyx' not in INDEX_HTML


def test_homepage_top_shell_uses_freecptcodefinder_brand():
    assert '<div class="title">FreeCPTCodeFinder.com</div>' in INDEX_HTML
    assert 'class="cyrionyx-header"' not in INDEX_HTML
    assert 'About CYRIONYX' not in INDEX_HTML
    assert '<body class="brand-shell">' not in INDEX_HTML


def test_homepage_keeps_key_internal_brand_links():
    for needle in [
        '/codes/',
        '/blog/',
        '/cpt-code-for/',
        '/blog/modifiers/',
        '/blog/rvu/understanding-work-rvus.html',
        '/blog/guides/global-surgical-package-explained.html',
        '/about.html',
        '/editorial-policy.html',
        '#case-builder',
    ]:
        assert needle in INDEX_HTML
