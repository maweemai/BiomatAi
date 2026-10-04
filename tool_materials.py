"""Local knowledge tools: indicative biomaterial and tissue data.
Values are approximate textbook-level ranges, NOT measurements. Agents must
verify important numbers with the literature tool."""
from crewai.tools import tool

MATERIALS = {
    "gelma": "GelMA (gelatin methacryloyl): photo-crosslinkable (UV/visible + photoinitiator); "
             "cell-adhesive (RGD) and MMP-degradable; typical 5-15% w/v; modulus roughly kPa to "
             "~100 kPa (rises with concentration, degree of substitution, exposure); "
             "degradation enzymatic, days to weeks. Limits: soft at low %, temperature-sensitive "
             "printability, photoinitiator/UV cytotoxicity risk.",
    "alginate": "Alginate: ionic crosslinking (Ca2+); good printability; typical 1-4% w/v; "
                "modulus kPa to ~100 kPa depending on Ca2+ and M/G ratio. No native cell adhesion "
                "motifs; slow, poorly controlled degradation (ion exchange) unless oxidized. "
                "Limit: needs RGD or a blend for cell attachment.",
    "chitosan": "Chitosan: cationic polysaccharide, soluble in mild acid; antibacterial; "
                "degraded by lysozyme (rate depends on degree of deacetylation); hydrogels are "
                "mechanically weak without crosslinking. Limit: acidic processing/pH can harm cells.",
    "collagen": "Collagen type I: native ECM protein, strongly cell-adhesive; gels thermally at "
                "~37 C; very soft (Pa to low kPa); cells may contract the gel; degrades by "
                "collagenases, fairly fast unless crosslinked.",
    "hyaluronic acid": "Hyaluronic acid (HA): native glycosaminoglycan, binds CD44, highly hydrated; "
                       "weak alone and cleared quickly by hyaluronidase; usually modified "
                       "(e.g. methacrylated HA) for crosslinking. Often favourable for cartilage.",
    "peg": "PEG / PEGDA: bio-inert synthetic; highly tunable modulus (kPa to MPa); photo-crosslinked; "
           "no cell adhesion unless RGD is added; PEGDA degrades slowly by ester hydrolysis. "
           "Limit: needs bioactive additions for cell-laden use.",
}
ALIASES = {"ha": "hyaluronic acid", "hyaluronan": "hyaluronic acid", "pegda": "peg"}

TISSUES = {
    "cartilage": "Articular cartilage: native compressive modulus ~0.5-1 MPa (method-dependent); "
                 "chondrocytes in low-oxygen, avascular tissue; key readouts: sulfated GAG and "
                 "collagen II, avoid hypertrophy/fibrocartilage (collagen I); degradation should be "
                 "slow enough for matrix deposition (weeks to months).",
    "bone": "Bone: trabecular compressive modulus ~0.1-2 GPa, far above hydrogels, so hydrogels "
            "usually need ceramic (e.g. hydroxyapatite) or polymer reinforcement; osteoblasts/MSCs; "
            "readouts: ALP, mineralization, osteocalcin; XRD/FTIR relevant for mineral phase.",
    "skin": "Skin/dermis: stiffness on the order of 0.1 to several MPa depending on test method; "
            "fibroblasts/keratinocytes; needs elasticity, moisture, vascularization/angiogenesis; "
            "faster degradation acceptable (days to weeks).",
    "muscle": "Skeletal muscle: ~10 kPa modulus; aligned myotubes; anisotropic/aligned scaffolds "
              "help; needs elasticity and nutrient diffusion.",
    "cardiac": "Cardiac muscle: ~10-20 kPa modulus; cardiomyocytes need electrical conductivity "
               "and cyclic-load tolerance; elastic, fatigue-resistant materials preferred.",
    "neural": "Neural tissue: very soft (~0.1-1 kPa); neurons/glia; needs soft, permeable gels "
              "and low inflammatory response.",
}


def _find(db: dict, text: str):
    t = ALIASES.get(text.strip().lower(), text.strip().lower())
    return next((v for k, v in db.items() if k in t or t in k), None)


@tool("Get biomaterial info")
def get_material_info(materials: str) -> str:
    """Look up indicative properties of biomaterials (GelMA, alginate, chitosan,
    collagen, hyaluronic acid, PEG). Input: one name or a comma-separated list,
    e.g. 'GelMA, alginate, hyaluronic acid'."""
    out = []
    for name in materials.split(","):
        found = _find(MATERIALS, name)
        out.append(found or f"No local entry for '{name.strip()}'. Use literature search instead.")
    return "\n".join(out)


@tool("Get tissue requirements")
def get_tissue_requirements(tissue: str) -> str:
    """Look up indicative mechanical and biological requirements of a target tissue
    (cartilage, bone, skin, muscle, cardiac, neural). Input: the tissue name."""
    return _find(TISSUES, tissue) or (
        f"No local entry for '{tissue}'. Use the literature search tool instead."
    )
