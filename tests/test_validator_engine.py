from dataclasses import dataclass

from ikg.validator import Finding, Severity, ValidationEngine


@dataclass(frozen=True)
class StubRule:
    rule_id: str
    finding: Finding

    def validate(self, graph: object) -> tuple[Finding, ...]:
        return (self.finding,)


def test_engine_orders_rules_and_findings_deterministically() -> None:
    rules = [
        StubRule("IKG002", Finding("IKG002", Severity.WARNING, "second", "b")),
        StubRule("IKG001", Finding("IKG001", Severity.ERROR, "first", "a")),
    ]

    report = ValidationEngine(rules).validate(graph={})

    assert [item.rule_id for item in report.findings] == ["IKG001", "IKG002"]
    assert report.is_valid is False
    assert report.error_count == 1
    assert report.warning_count == 1
