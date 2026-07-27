from fritzconnection.lib.fritztam import FritzTAM


class FakeFritzConnection:
    def __init__(self):
        self.calls = []

    def call_action(self, service, actionname, **kwargs):
        self.calls.append((service, actionname, kwargs))
        return {}


def test_delete_message_uses_explicit_stable_indices():
    fc = FakeFritzConnection()
    tam = FritzTAM(fc=fc)

    tam.delete_message(index=1, message_index=42)

    assert fc.calls == [
        (
            'X_AVM-DE_TAM1',
            'DeleteMessage',
            {
                'NewIndex': 1,
                'NewMessageIndex': 42,
            },
        )
    ]
