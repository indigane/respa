Respa-Exchange
==============


A connector for bidirectional synchronization of [Respa][respa]
event information with Microsoft Exchange resource calendars.

Installation
------------

Respa-Exchange is a Django app that hooks to Respa using Django signals.

* Add `respa_exchange` to your `INSTALLED_APPS`.
* Run Django `migrate` and restart your app server, etc.
* You should now see Respa-Exchange entries in the Django admin.

Development/howto
-----------------

You'll need a copy of [Respa][respa] to develop Respa-Exchange against.

* Set up a virtualenv.
* Install Respa's requirements: `pip install -r requirements.txt`
* Run `py.test`. Everything should work.

Requirements
------------

* Microsoft Exchange On-Premises installation with
  Exchange Web Services enabled
  
Acknowledgements
----------------

* [LinkedIn's PyExchange][pyex] project was a tremendous help. Thanks!

---

[respa]: https://github.com/City-of-Helsinki/respa
[pyex]: https://github.com/linkedin/pyexchange









Notes on current documentation
------------------------------

- "Requirements: Microsoft _Exchange On-Premises_ installation with _Exchange Web Services_ enabled"
- "https://github.com/linkedin/pyexchange was a tremendous help"
- Models
    - `ExchangeConfiguration`
        - `name` -- a descriptive name for this Exchange configuration
        - `url` -- EWS URL, the URL to the Exchange Web Service (e.g. https://contoso.com/EWS/Exchange.asmx)
        - `username` -- the service user to authenticate as, in domain\username format
        - `password` -- the user's password (stored as plain-text)
        - `enabled` -- whether synchronization is enabled at all against this Exchange instance
    - `ExchangeResource`
        - `exchange` -- ForeignKey: `ExchangeConfiguration`
        - `resource` -- OneToOne: respa `Resource`
        - `sync_to_respa` -- if disabled, events will not be synced from the Exchange calendar to Respa
        - `sync_from_respa` -- if disabled, new events will not be synced from Respa to the Exchange calendar; pre-existing events continue to be updated
        - `principal_email` -- the email address for this resource in Exchange
    - `ExchangeReservation`
        - `exchange` -- ForeignKey: `ExchangeConfiguration`, cached value of related resource `exchange`
        - `reservation` -- OneToOne: respa `Reservation`
        - Exchange ItemID consists of two parts: id and change key
        - `item_id_hash` -- md5 hash of the id part of ItemID, for smaller (=faster) index size
        - `_item_id` -- id part of Exchange ItemID
        - `_change_key` -- change key part of Exchange ItemID
        - `organizer` -- ForeignKey: `ExchangeUser`
        - `managed_in_exchange` -- Whether or not this reservation came from Exchange
            - Reservations made in Exchange will only be downloaded, changes will not be uploaded.
            - Reservations made in Respa will only allow Exchange to update start and end times, no other fields.
        - `principal_email` -- Cached value of resource `principal_email`
        - `created_at`
        - `modified_at` -- Not automatically updated.
        - @property `item_id` -- Return ItemID object based on `_item_id` and `_change_key`
        - @.setter `item_id` -- Set `_item_id`, `_change_key` and `item_id_hash` based on an ItemID object. `_item_id`, if already set, is immutable.
    - `ExchangeUser`
        - `exchange` -- ForeignKey: `ExchangeConfiguration`
        - `email_address`
        - `name`
        - `given_name`
        - `surname`
        - `user` -- OneToOne: `User`, get_user_model()
        - `updated_at` -- `auto_now=True`
    - `ExchangeUserX500Address`
        - X500 addresses are a type of additional Exchange email addresses tied to an Exchange user.
          Exchange docs: "The additional addresses are called proxy addresses. A proxy address lets a user receive email that's sent to a different email address."
          In Respa these may be used to find the correct ExchangeUser.
        - `exchange` -- ForeignKey: `ExchangeConfiguration`
        - `user` -- ForeignKey: `ExchangeUser`
        - `address`


Exchange on-premises to Exchange Online (Office365) migration
-------------------------------------------------------------

- `respa_exchange` uses NTLM authentication for it's API sessions (`session.py::ExchangeSession`)
- NTLM authentication is only available for Exchange on-premises. OAuth 2.0 is currently the only viable alternative for Exchange Online, as Basic authentication is being removed Oct 2020. https://web.archive.org/web/20190419210714/https://docs.microsoft.com/en-us/exchange/client-developer/exchange-web-services/authentication-and-ews-in-exchange
- Based on this https://stackoverflow.com/questions/56148996/ it would seem that other than for authentication, the URL change is all that's needed.
- `https://outlook.office365.com/ews/Exchange.asmx`
- `Authorization: Bearer <oauth token>`


X500 Addresses
--------------

- (this is an ad, but somewhat useful info) https://www.quadrotech-it.com/blog/what-is-the-x500-email-address/
- ExchangeUserX500Address objects are referred when `RoutingType` in Exchange is `'EX'`. Not sure if EX and X500 are interchangeable terms or not. Some docs mention them separately https://docs.microsoft.com/en-us/exchange/mail-flow/mail-routing/recipient-resolution?view=exchserver-2019#encapsulated-email-addresses
- Example of EX RoutingType address: `/O=HOSTING-ORGANIZATION/OU=EXCHANGE ADMINISTRATIVE GROUP (XXXXXXXXXXX)/CN=RECIPIENTS/CN=XXXXXXXXXXXXXXXXXXXXX-INITIALS`
- Another example, referred to as X500 address `:/o=TE/ou=St/cn=Recipients/cn=username`
- Another example "try adding EX" `EX:/o=TE/ou=St/cn=Recipients/cn=username`
- Another example `x500:/O=Nokia/OU=HUB/cn=Recipients/cn=useralias`
- "That is the EX or X500 address which is how Exchange will store the address for
  any Internal user (so in Office365 meaning any Mailbox in the tenant) If you look
  at the appointment in a Mapi Editor like OutlookSpy or MFCMapi this is the address
  you will see PR_EMAIL_ADDRESS_W property in the Recipient collection. EWS should
  resolve this address to an SMTP when you use GetItem (its important to not that
  doesn't happening when you use FindItems). You can try resolving the address
  yourself using ResolveName"
  "The Appointment was imported into the calendar (eg if somebody has just done
  a PST export and PST import (or other migration method) then they may have imported
  the X500 address from their OnPremise envioment). Its pretty easy to tell if this
  is happened because the X500 address for Office365 should look like
  /O=EXCHANGELABS/OU=EXCHANGE ADMINISTRATIVE GROUP...."
  "If its a hybrid or they are using dirsync etc then the LegacyDN's from the source
  environment should be synced as an addition X500 proxy Address on the Mailbox which
  should then allow the old X500 address then to be resolved by EWS or Outlook."

```
<t:Mailbox>
    <t:Name>unknown1</t:Name>
    <t:EmailAddress>/o=ExchangeLabs/ou=Exchange Administrative Group (FYDIBOHF23SPDLT)/cn=Recipients/cn=95d91709c4c246b7a4ca5c7541f2b19a-unknown1</t:EmailAddress>
    <t:RoutingType>EX</t:RoutingType>
    <t:MailboxType>Contact</t:MailboxType>
</t:Mailbox>
<t:Mailbox>
    <t:Name>gs test</t:Name>
    <t:EmailAddress>/O=EXCHANGELABS/OU=EXCHANGE ADMINISTRATIVE GROUP (FYDIBOHF23SPDLT)/CN=RECIPIENTS/CN=63A7E24920DA46F9974B330A05270EAD-GSTEST</t:EmailAddress>
    <t:RoutingType>EX</t:RoutingType>
    <t:MailboxType>OneOff</t:MailboxType>
</t:Mailbox>
<t:EmailAddresses>
    <t:Entry Key="EmailAddress1">EUM:usr@microsoft.com;phone-context=O365-USA-OCS-SIPSec.c6b0fa26-f115-4ad9-a50e-546786134a92</t:Entry>
    <t:Entry Key="EmailAddress2">eum:14257076604;phone-context=O365-USA-OCS-SIPSec.c6b0fa26-f115-4ad9-a50e-546786134a92</t:Entry>
    <t:Entry Key="EmailAddress3">x500:/O=Nokia/OU=HUB/cn=Recipients/cn=useralias</t:Entry>
</t:EmailAddresses>
```

