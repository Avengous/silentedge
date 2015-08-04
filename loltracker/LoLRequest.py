#- Makes calls to the Riot API.

import LoL
from riotwatcher import RiotWatcher
from time import sleep

class Request():
	
	def __init__(self):
		self.riot = RiotWatcher(LoL.API_KEY)
		self.champions = self._getChampions()
	
	def _getChampions(self):
		champion_list = {}
		champions = self.riot.static_get_champion_list()
		for champion in champions['data']:
			champion_list[champions['data'][champion]['id']] = champion
		return champion_list
			
	def _checkRequestStatus(self):
		return self.riot.can_make_request()
		
	def retrievePlayerData(self, playerId):
		while not self._checkRequestStatus():
			sleep(2.6)
		else:
			player = {}
			player['id'] = playerId
			player['summoner'] = self.riot.get_summoner(name=playerId)
			player['match_history'] = self.riot.get_match_history(player['summoner']['id'])
			return player