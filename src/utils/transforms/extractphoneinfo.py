
from canari.maltego.transform import Transform
from canari.maltego.message import LinkColor
import canari.maltego.entities as ents

import phonenumbers \
    , pycountry

from fuzzywuzzy import process
from phonenumbers import carrier
from phonenumbers.geocoder import description_for_number

from geopy.geocoders import Photon as Geocoder
from geopy.exc import GeocoderTimedOut


__author__ = 'foo-manroot'
__copyright__ = 'Copyright 2018, utils Project'
__credits__ = []

__license__ = 'GPLv3'
__version__ = '0.1'
__maintainer__ = 'foo-manroot'
__email__ = 'foo@oi.m8'
__status__ = 'Development'


class ExtractPhoneInfo (Transform):
    """Extracts all information available from the phone number (carrier, country...)"""

    # The transform input entity type.
    input_type = ents.PhoneNumber

    # Lookup table used to translate between phone types and integers, as returned by
    # phonenumbers.number_type ()
    #
    # Copied from the source code of phonenumberutil.py, on
    #   https://github.com/daviddrysdale/python-phonenumbers
    phonetype_lookup = {
            0: "Fixed line"
            , 1: "Moblie"
            # In some regions (e.g. the USA), it is impossible to distinguish between
            # fixed-line and mobile numbers by looking at the phone number itself.
            , 2: "Fized or mobile line"
            # Freephone lines
            , 3: "Toll free"
            , 4: "Premium rate"
            # The cost of this call is shared between the caller and the recipient,
            # and is hence typically less than PREMIUM_RATE calls. See
            # http://en.wikipedia.org/wiki/Shared_Cost_Service for more information.
            , 5: "Shared cost"
            # Voice over IP numbers. This includes TSoIP (Telephony Service over IP).
            , 6: "VoIP"
            # A personal number is associated with a particular person, and may be
            # routed to either a MOBILE or FIXED_LINE number. Some more information
            # can be found here: http://en.wikipedia.org/wiki/Personal_Numbers
            , 7: "Personal number"
            , 8: "Pager"
            # Used for "Universal Access Numbers" or "Company Numbers". They may be
            # further routed to specific offices, but allow one number to be used for
            # a company.
            , 9: "Universal Access Number"
            # Used for "Voice Mail Access Numbers".
            , 10: "Voice Mail Access Number"
            # A phone number is of type UNKNOWN when it does not fit any of the known
            # patterns for a specific region.
            , 99: "Unknown"
    }


    def extract_location (self, location_str, country_code):
        """
        Creates a location with the information

        Args:
            location_str -> String with the aproximate location (country, city...)
            country_code -> Code to extract more information, if it wasn't deduced
                with only the location string
        """
        city = None
        country = None
        area = None
        area_name = None
        area_code = None

        if country_code:
            country = pycountry.countries.lookup (country_code)
            if country:
                country = country.name

        if location_str:
            # Uses the location string to create a more precise location

            # Geolocation
            geolocator = Geocoder (user_agent = "Maltego", timeout = 2)

            try:
                location = geolocator.geocode (location_str, exactly_one = True)

            except:
                # Tries it again after sleeping a couple of seconds
                try:
                    sleep (2)
                    location = geolocator.geocode (location_str, exactly_one = True)

                except:
                    location = None

            # If the returned value isn't a country or a continent
            loc_properties = location.raw ["properties"]
            if "osm_value" in loc_properties \
                and loc_properties ["osm_value"].lower () != "continent" \
                and loc_properties ["osm_value"].lower () != "country":

                if "name" in loc_properties:
                    area = loc_properties ["name"]

                if "country" in loc_properties:
                    # Overrides the country extracted with the country code (if any)
                    country = loc_properties ["country"]

                if loc_properties ["osm_value"].lower () == "city" \
                    and "name" in loc_properties:

                    city = loc_properties ["name"]


        # State or province
        if area and country_code:
            choices = pycountry.subdivisions.get (country_code = country_code)
            found = process.extractOne (area, choices)

            # Discards it if the score is lower than 50
            if found and found [1] > 50:
                state = found [0]

                area_name = state.name.decode ("utf-8")
                area_code = state.code.decode ("utf-8")

                if not country_code:
                    # Gets the country code from the state info
                    country_code = state.country_code.decode ("utf-8")


        # Sanitizes all values before creating the XML
        country = country.decode ("utf-8") if country else None
        city = city.decode ("utf-8") if city else None

        return ents.Location (
            name = (city + ", " + country) if city else country
            , city = city
            , country = country
            , area = area
            , areacode = area_code
            , countrycode = country_code
            , longitude = location.longitude if location else 0
            , latitude = location.latitude if location else 0
        )




    def do_transform (self, request, response, config):

        phone = request.entity

        # Formats the string for the parser to understand the phone number
        number = ""
        if phone.countrycode:
            number += "+" + phone.countrycode + " "

        if phone.citycode:
            number += citycode

        if phone.areacode:
            number += phone.areacode

        number += phone.lastnumbers

        try:
            parsed = phonenumbers.parse (number)
        except phonenumbers.NumberParseException as e:
            # The phone number couldn't be parsed
            return response

        # Gets the country from the country code (if any)
        country_code = phonenumbers.region_code_for_number (parsed)

        # It may be the country, city, or any string that defines a geographical area
        location_str = str (description_for_number (parsed, "en"))

        phone_type = self.phonetype_lookup [phonenumbers.number_type (parsed)]
        # Returns the result in english (we don't care, as it's just the carrier's name)
        carrier_name = carrier.name_for_number (parsed, "en")

        valid_number = phonenumbers.is_valid_number (parsed)


        # Creates the entities to be added to the graph
        if not valid_number:
            # Adds a phrase warning about the invalid phone
            response += ents.Phrase (
                    text = "Possibly invalid number"
                    , link_color = LinkColor.Red
                    , link_thickness = 3
            )

        # Phrase with the carrier info
        if carrier_name:
            response += ents.Phrase ("Carrier: " + carrier_name)

        # Phrase with the phone type
        if phone_type and phone_type.lower () != "unknown":
            response += ents.Phrase ("Phone type: " + phone_type)

        # Location
        if location_str or country_code:
            response += self.extract_location (location_str, country_code)


        return response
