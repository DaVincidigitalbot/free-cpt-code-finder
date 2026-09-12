from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
LOGO = ROOT / "assets" / "partners" / "make-no-mistakes-logo.png"
CAPTIONS = ROOT / "assets" / "captions" / "mnm-ai-agent-demo-en.vtt"


def page():
    return INDEX.read_text(encoding="utf-8")


def test_medical_agent_ad_is_present_and_targets_clinicians():
    html = page()
    assert 'id="mnm-agent-ad"' in html
    assert "A chatbot answers." in html
    assert "An AI agent gets the work done." in html
    assert "For physicians · surgeons · residents · medical students" in html
    assert "Monitor journals and prepare evidence briefs" in html


def test_ad_links_safely_to_make_no_mistakes():
    html = page()
    assert 'href="https://makenomistakes.shop/"' in html
    assert 'rel="sponsored noopener"' in html
    assert "Get your own AI agent" in html


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
