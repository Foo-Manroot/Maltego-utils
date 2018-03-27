
from canari.maltego.transform import Transform

import canari.maltego.entities as ents
from common.entities import WHOISregister

import phonenumbers \
    , pycountry

from fuzzywuzzy import process
from geopy.geocoders import Photon as Geocoder
from geopy.exc import GeocoderTimedOut

from time import sleep

__author__ = 'foo-manroot'
__copyright__ = 'Copyright 2018, utils Project'
__credits__ = []

__license__ = 'GPLv3'
__version__ = '0.1'
__maintainer__ = 'foo-manroot'
__email__ = 'foo@oi.m8'
__status__ = 'Development'


class ExtractWhoisInfo (Transform):
    """Extracts all the information available on the input WHOIS register, creating all relevant entities from it (phone, location, persons...)"""

    # The transform input entity type.
    input_type = WHOISregister

    def extract_location (self, country, state, city, street, postal_code):
        """
        Creates all possible location-related items with the available information.

        Args:
            register -> WHOISregister object with all the information to extract
        """
        # Doesn't even try to create a location entity if there's not at least a country
        if country:

            area = None
            area_code = None

            try:
                country_code = pycountry.countries.lookup (
                                    country.decode ("utf-8")
                ).alpha_2.decode ("utf-8")
            except:
                country_code = None

            # Geolocation
            geolocator = Geocoder (user_agent = "Maltego", timeout = 2)

            try:
                if street:
                    search += street + ", "

                if city:
                    search += country + ", "

                search += country

                location = geolocator.geocode (search, exactly_one = True)

            except:
                # Tries it again after sleeping a couple of seconds
                try:
                    sleep (2)
                    search = ""

                    if street:
                        search += street + ", "

                    if city:
                        search += country + ", "

                    search += country

                    location = geolocator.geocode (search, exactly_one = True)

                except:
                    location = None



            if country_code:
                choices = pycountry.subdivisions.get (country_code = country_code)
            else:
                choices = pycountry.subdivisions

            # State or province
            if state:
                found = process.extractOne (state, choices)

                # Discards it if the score is lower than 50
                if found and found [1] > 50:
                    state = found [0]

                    area = state.name.decode ("utf-8")
                    area_code = state.code.decode ("utf-8")

                    if not country_code:
                        # Gets the country code from the state info
                        country_code = state.country_code.decode ("utf-8")
            else:
                area = None
                area_code = None

            # Sanitizes all values before creating the XML
            country = country.decode ("utf-8")
            street = street.decode ("utf-8") if street else None
            city = city.decode ("utf-8") if city else None

            return ents.Location (
                name = (city + ", " + country) if city else country
                , city = city
                , country = country
                , streetaddress = street
                , area = area
                , areacode = area_code
                , countrycode = country_code
                , longitude = location.longitude if location else 0
                , latitude = location.latitude if location else 0
            )

        return None


    def extract_phone (self, field_value):
        """
        Parses the input string to create a PhoneNumber entity with all the possible
        values.

        Args:
            field_value -> The value of the field where the information will be
                collected from
        """
        try:
            parsed = phonenumbers.parse (field_value)
        except phonenumbers.NumberParseException as e:
            # The phone number couldn't be parsed
            return None

        # Checks if it could be a phone number, but not if it could be real
        if phonenumbers.is_possible_number (parsed):

            nsn = str (phonenumbers.national_significant_number (parsed))
            ndc_len = phonenumbers.length_of_national_destination_code (parsed)

            if ndc_len > 0:
                area_code = nsn [:ndc_len]
                lastnumbers = nsn [ndc_len:]
            else:
                area_code = None
                lastnumbers = nsn

            return ents.PhoneNumber (
                phonenumber = field_value
                , countrycode = parsed.country_code
                , areacode = area_code if area_code else None
                , lastnumbers = lastnumbers
            )


        return None


    def do_transform (self, request, response, config):
        """
        Main method called when the transformation has to be done
        """

        register = request.entity

        # Domain
        if register.properties_domain:
            response += ents.Domain (register.properties_domain)

        # Emails (tech, admin and registrant)
        extract_email = lambda x: ents.EmailAddress (x) if x else None

        response += extract_email (register.admin_email)
        response += extract_email (register.tech_email)
        response += extract_email (register.registrant_email)

        # Persons (tech, admin and registrant
        extract_person = lambda x: ents.Person (fullname = x) if x else None

        response += extract_person (register.admin_name)
        response += extract_person (register.tech_name)
        response += extract_person (register.registrant_name)

        # Phone numbers
        response += self.extract_phone (register.admin_phone)
        response += self.extract_phone (register.tech_phone)
        response += self.extract_phone (register.registrant_phone)

        # Locations
        response += self.extract_location (register.registrant_country
                                        , register.registrant_state
                                        , register.registrant_city
                                        , register.registrant_street
                                        , register.registrant_postal_code
        )
        response += self.extract_location (register.admin_country
                                        , register.admin_state
                                        , register.admin_city
                                        , register.admin_street
                                        , register.admin_postal_code
        )
        response += self.extract_location (register.tech_country
                                        , register.tech_state
                                        , register.tech_city
                                        , register.tech_street
                                        , register.tech_postal_code
        )

        return response
