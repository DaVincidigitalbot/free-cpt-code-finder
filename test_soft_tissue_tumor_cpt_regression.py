import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "scripts" / "audit_soft_tissue_tumor_cpts.py"


def load_validator():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("audit_soft_tissue_tumor_cpts", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_soft_tissue_tumor_cpt_source_matches_production():
    validator = load_validator()
    assert validator.validate() == 0


def test_back_flank_shift_regression():
    validator = load_validator()
    cpt_db = validator.load_json(ROOT / "cpt_database.json")
    expected = {
        "21930": ("subcutaneous", "less than 3 cm"),
        "21931": ("subcutaneous", "3 cm or greater"),
        "21932": ("deep subfascial or intramuscular", "less than 5 cm"),
        "21933": ("deep subfascial or intramuscular", "5 cm or greater"),
        "21935": ("radical soft tissue resection", "less than 5 cm"),
        "21936": ("radical soft tissue resection", "5 cm or greater"),
    }
    for code, (depth, size) in expected.items():
        meta = cpt_db[code]["soft_tissue_tumor"]
        assert meta["body_region"] == "Back / flank"
        assert meta["depth_classification"] == depth
        assert meta["size_category"] == size


def test_soft_tissue_tumor_codes_are_unique_and_ordered():
    validator = load_validator()
    codes = list(validator.SOFT_TISSUE_TUMOR_CODES)
    assert len(codes) == len(set(codes))
    assert sorted(codes) == sorted(set(codes))
