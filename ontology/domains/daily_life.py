"""Human-readable ontology branch selection for daily life and practical knowledge."""

from .seed_runtime import select_domain_nodes

NODES = select_domain_nodes({
    "agricoltura", "cucina_alimentazione", "sport", "vita_quotidiana",
    "competenze_pratiche", "cultura_digitale",
})
