The REST protocol itself is extremely simple.  As performed by ``daemos/hybrid.py``, it's just a one-way GET responder that listens for requests following two endpoints::

  /lookup/<address>
  /contacts/<keytup>

Each described in more detail below.


/lookup/
--------

The ``/lookup/`` service is used by the frontend to get basic summary information for a given address -- BBL, BIN, geocoding, and what we'll call "extras" (taxbill, HPD, and DHCR fields).  As an example, a client might make a request like::

  /lookup/1+West+72nd+St,+Manhattan

And (if it's a valid address), expect a payload of the following form::

  {
    "extras": {
        "dhcr_active": false,
        "nychpd_contacts": 5,
        "taxbill": {
            "active_date": "2015-06-05",
            "owner_address": [
                "DAKOTA INC. (THE)",
                "1 W. 72ND ST.",
                "NEW YORK , NY 10023-3486"
            ],
            "owner_name": "DAKOTA INC. (THE)"
        }
    },
    "nycgeo": {
        "bbl": 1011250025,
        "bin": 1028637,
        "geo_lat": 40.77640230806594,
        "geo_lon": -73.97636507868083
    }
  }


Or a suitable error message, if the address is garbled or otherwise invalid.  If valid then the the ``bbl`` and ``bin`` identifiers are used to from the ``<keytup>`` passed to the ``/contacts/`` endpoint, below. 

/contacts/
----------

The ``/contacts/`` provides HPD contacts (for those properties that have them).  The request goes like this::

  /contacts/1011250025,1028637

And a respond will look like this::
 
  [
    {
        "business_address": "675 THIRD AVENUE NEW YORK NY 10017",
        "contact_id": 11878003,
        "contact_name": null,
        "contact_type": "CorporateOwner",
        "corpname": "THE DAKOTA INC",
        "description": "CO-OP",
        "registration_id": 118780
    },
    {
        "business_address": "675 THIRD AVENUE NEW YORK NY 10017",
        "contact_id": 11878005,
        "contact_name": null,
        "contact_type": "HeadOfficer",
        "corpname": null,
        "description": "CO-OP",
        "registration_id": 118780
    },
    {
        "business_address": "675 THIRD AVENUE NEW YORK NY 10017",
        "contact_id": 11878006,
        "contact_name": null,
        "contact_type": "Officer",
        "corpname": null,
        "description": "CO-OP",
        "registration_id": 118780
    },
    {
        "business_address": "",
        "contact_id": 11878013,
        "contact_name": null,
        "contact_type": "SiteManager",
        "corpname": null,
        "description": "CO-OP",
        "registration_id": 118780
    },
    {
        "business_address": "675 THIRD AVENUE NEW YORK NY 10017",
        "contact_id": 11878004,
        "contact_name": null,
        "contact_type": "Agent",
        "corpname": "DOUGLAS ELLIMAN PROPERTY MANAGEMENT",
        "description": "CO-OP",
        "registration_id": 118780
    }
  ]
