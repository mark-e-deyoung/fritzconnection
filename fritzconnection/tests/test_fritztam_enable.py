import pytest

from fritzconnection.lib.fritztam import FritzTAM


class FakeFritzConnection:
    def __init__(self):
        self.calls = []

    def call_action(self, service, actionname, **kwargs):
        self.calls.append((service, actionname, kwargs))
        return {}


@pytest.mark.parametrize('enabled', [True, False])
def test_set_enabled_uses_explicit_index(enabled):
    fc = FakeFritzConnection()
    tam = FritzTAM(fc=fc)

    tam.set_enabled(index=2, enabled=enabled)

    assert fc.calls == [
        (
            'X_AVM-DE_TAM1',
            'SetEnable',
            {
                'NewIndex': 2,
                'NewEnable': enabled,
            },
        )
    ]
