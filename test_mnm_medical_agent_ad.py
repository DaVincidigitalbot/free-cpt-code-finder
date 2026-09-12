from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
LOGO = ROOT / "assets" / "partners" / "make-no-mistakes-logo.png"
CAPTIONS = ROOT / "assets" / "captions" / "mnm-ai-agent-demo-en.vtt"


def page():
    return INDEX.read_text(encoding="utf-8")


def test_ad_is_compact_and_inside_case_rail():
    html = page()
    rail_start = html.index('<aside class="rail"')
    ad_start = html.index('<section class="mnm-agent-ad mnm-agent-ad--rail"')
    rail_end = html.index("</aside>", rail_start)
    active_case = html.index('<div class="rh">', rail_start)
    assert rail_start < ad_start < active_case < rail_end
    assert "mnm-agent-ad__workflow" not in html
    assert "mnm-agent-ad__examples" not in html
    assert "document.addEventListener('DOMContentLoaded',function()" in html


def test_medical_agent_ad_is_present_and_targets_clinicians():
    html = page()
    assert 'id="mnm-agent-ad"' in html
    assert "A chatbot answers." in html
    assert "An AI agent gets the work done." in html
    assert "For physicians · surgeons · residents · medical students" in html
    assert "monitor journals and prepare evidence briefs" in html


def test_ad_links_safely_to_make_no_mistakes():
    html = page()
    assert 'href="https://makenomistakes.shop/?utm_source=freecptcodefinder' in html
    assert 'rel="sponsored noopener"' in html
    assert "Learn more" in html


def test_ad_actions_emit_distinct_ga4_events():
    html = page()
    assert "'mnm_ad_'+action+'_click'" in html
    assert "watch_demo" in html
    assert "learn_more" in html
    assert "typeof window.gtag==='function'" in html
    assert "ad_placement:'homepage_right_rail'" in html
    assert "try{" in html
    assert "if(cta)cta.addEventListener" in html


def test_ad_uses_company_logo_and_accessible_video_dialog():
    html = page()
    assert LOGO.is_file()
    assert 'src="/assets/partners/make-no-mistakes-logo.png"' in html
    assert 'id="mnmAgentVideoDialog"' in html
    assert 'aria-label="AI agent demonstration video"' in html
    assert 'https://makenomistakes.shop/assets/video/mnm-ai-agent-updates-website.mp4' in html
    assert "autoplay" not in html.lower()
    assert "playsinline" in html


def test_video_controls_reference_the_rendered_element_ids():
    html = page()
    for element_id in ("mnmAgentVideoOpen", "mnmAgentVideoClose", "mnmAgentVideo"):
        assert f'id="{element_id}"' in html
        assert f"getElementById('{element_id}')" in html


def test_video_modal_is_captioned_and_keyboard_contained():
    html = page()
    assert CAPTIONS.is_file()
    assert 'kind="captions"' in html
    assert 'src="/assets/captions/mnm-ai-agent-demo-en.vtt"' in html
    assert "previousOverflow" in html
    assert "backgroundElements" in html
    assert "event.key==='Tab'" in html
    assert "getClientRects().length" in html
    assert 'src="/assets/partners/make-no-mistakes-logo.png" alt=""' in html
    assert "Running on your hardware" not in html


def test_ad_is_responsive_and_does_not_make_unverified_privacy_claims():
    html = page()
    assert "@media(max-width:760px)" in html
    assert "HIPAA compliant" not in html
    assert "Illustrative non-clinical workflow" in html
    assert "Human review remains essential" in html
