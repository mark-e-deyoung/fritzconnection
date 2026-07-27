from fritzconnection.lib.fritztam import FritzTAM


class FakeFritzConnection:
    def __init__(self):
        self.calls = []

    def call_action(self, service, actionname, **kwargs):
        self.calls.append((service, actionname, kwargs))
        return {}


def test_mark_message_read():
    fc = FakeFritzConnection()
    tam = FritzTAM(fc=fc)

    tam.mark_message(index=1, message_index=17)

    assert fc.calls == [
        (
            'X_AVM-DE_TAM1',
            'MarkMessage',
            {
                'NewIndex': 1,
                'NewMessageIndex': 17,
                'NewMarkedAsRead': True,
            },
        )
    ]


def test_mark_message_unread():
    fc = FakeFritzConnection()
    tam = FritzTAM(fc=fc)

    tam.mark_message(index=0, message_index=7, read=False)

    assert fc.calls == [
        (
            'X_AVM-DE_TAM1',
            'MarkMessage',
            {
                'NewIndex': 0,
                'NewMessageIndex': 7,
                'NewMarkedAsRead': False,
            },
        )
    ]
