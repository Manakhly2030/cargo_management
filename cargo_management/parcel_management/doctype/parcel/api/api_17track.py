from types import SimpleNamespace

import requests

import frappe


class _17TrackAPIError(Exception):
	""" Child Class to personalize API Error """
	# https://api.17track.net/en/doc?anchor=list-of-error-codes&version=v2
	pass


class API17Track:
	""" 17Track methods to control class API and parse data. """
	api_base = "https://api.17track.net/track/v2/"

	# The Dict Keys are the actual String representation for Users, and the Dict Values are the carrier code for the API
	# See More at: https://res.17track.net/asset/carrier/info/apicarrier.all.json
	carrier_codes = {
		'Amazon': 100143,  # Swiship it works
		'FedEx': 100003,
		'LaserShip': 100052,
		'Cainiao': 190271,
		'Yanwen': 190012,
		'YunExpress': 190008
	}

	def __init__(self):
		self.data = {}
		self.api_key = frappe.conf['17track_api_key']

	def _build_request(self, endpoint, payload):
		self.data = requests.request('POST', url=self.api_base + endpoint, json=payload, headers={
			"content-type": "application/json",
			"17token": self.api_key
		}).json(object_hook=lambda d: SimpleNamespace(**d)).data

		if self.data.rejected:
			if self.data.rejected[0].error.code == -18019901:
				raise _17TrackAPIError(self.data.rejected[0]['error']['message'])

	def register_package(self, tracking_number, carrier):
		""" Create a Tracking on 17Track """
		response = self._build_request('register', payload=[{
			"number": tracking_number,
			"carrier": carrier,
			"auto_detection": True,  # So we avoid sending the carrier?
		}])

		response = response.json()  # IMPROVE THIS

		if response['data']['accepted']:
			return response['data']['accepted'][0]
		elif response['data']['rejected']:
			raise Exception(response['data']['rejected'][0]['error'])

	def retrieve_package_data(self, tracking_number):
		""" Retrieve data from 17Track """
		response = self._build_request('gettrackinfo', payload=[{
			"number": tracking_number
		}])

		response = response.json()  # IMPROVE THIS

		if response['data']['accepted']:
			return response['data']['accepted'][0]
		elif response['data']['rejected']:
			raise Exception(response['data']['rejected'][0]['error'])

		return response