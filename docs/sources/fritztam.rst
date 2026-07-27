FritzTAM
========

``FritzTAM`` provides access to the telephone answering machines configured on
a FRITZ!Box and to their voicemail message lists.

The FRITZ!Box user requires the ``Phone`` permission for the underlying
``X_AVM-DE_TAM1`` actions.

Example::

    from fritzconnection.lib.fritztam import FritzTAM

    tam = FritzTAM(address='192.168.178.1', password='password')

    answering_machines = tam.get_list()
    for answering_machine in answering_machines:
        print(
            answering_machine.index,
            answering_machine.name,
            answering_machine.enabled,
        )

    messages = tam.get_messages(index=0, maximum=25)
    for message in messages:
        print(message.index, message.Name, message.Date, message.path)

    # Use the stable message index returned by get_messages().
    tam.mark_message(index=0, message_index=messages[0].index, read=True)

``get_info()`` returns the values provided directly by the TR-064 ``GetInfo``
action. ``get_list()`` returns a :class:`TAMList` with global status values and
one :class:`TAMListItem` for each configured answering machine.

``get_messages()`` obtains the temporary message-list URL from the router and
returns a list of :class:`TAMMessage` objects. A message's ``index`` property is
the stable message identifier used by the documented message actions. The
``path`` property is the router-relative path of the recording; this module
does not download recordings.

``mark_message()`` marks one explicitly selected message as read or unread. The
``message_index`` argument must be the stable index obtained from the message
list; the method does not infer or search for a target message.

FritzTAM API
------------

.. automodule:: fritzconnection.lib.fritztam
    :members:
