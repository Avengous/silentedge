import sqlite3
import time
import sys
import LoL
from LoLRequest import Request

class Database():
	
	def __init__(self):
		self.connection = sqlite3.connect(sys.path[0]+'\loltracker.db')
		self.db = self.connection.cursor()
	
	def _commit(self):
		self.connection.commit()
	
	def _close(self):
		self.connection.close()
	
	def _createTable(self, table, fields):
		query = "CREATE TABLE `{0}` (`tid` INTEGER NOT NULL UNIQUE,{1}, PRIMARY KEY(tid))".format(table, fields)
		self.db.execute(query)
		self._commit()
		
	def _insert(self, table, data):
		fields = []
		values = []
		for key in data:
			fields.append(key['field'])
			if key['value'] is True:
				values.append(str(1))
			elif key['value'] is False:
				values.append(str(0))
			elif self._returnCompatField(type(key['value'])) == 'text':
				values.append("'{}'".format(key['value']))
			else:
				values.append(str(key['value']))
		query = "INSERT OR REPLACE INTO {0}({1}) VALUES({2})".format(table, ','.join(fields), ','.join(values))
		self.db.execute(query)
		self._commit()
	
	def _select(self, table, field, value):
		return self.db.execute("SELECT * FROM {0} WHERE {1}=?".format(table, field), (value,))
		
	def _update(self, table, field, value, key):
			query = "UPDATE {0} SET {1}={2} WHERE {3}=?".format(table, field, value, key.keys()[0])
			self.db.execute(query, (key['name'],))
			self._commit()
			
	def _returnCompatField(self, type):
		if type in [str, unicode]:
			return 'text'
		elif type in [int, long, bool]:
			return 'int'
		elif type in [float]:
			return 'real'
		else:
			print 'Untracked Type:', type
			return None
	
	#Should I hard-code each variable to make it look cleaner and more readable? - I should create a script for this later.
	def createDatabase(self):
		player = Request().retrievePlayerData(LoL.PLAYERIDS[0])
		fields = ['lastUpdated int']
		#Create table for players
		for item in player['summoner']:
			fields.append('{} {}'.format(item, self._returnCompatField(type(player['summoner'][item]))))
		self._createTable('players', ','.join(fields))
		#Create table for matches
		fields = []
		skip_next = False
		matchData = player['match_history']['matches'][0]
		for item in matchData:
			if type(matchData[item]) is not list:
				fields.append('{} {}'.format(item, self._returnCompatField(type(matchData[item]))))
			else:
				for subitem in matchData[item][0]:
					if type(matchData[item][0][subitem]) is not list and type(matchData[item][0][subitem]) is not dict:
						#Skips the duplicate participantId field returned from Riot API.
						if subitem == 'participantId':
							if not skip_next:
								fields.append('{} {}'.format(subitem, self._returnCompatField(type(matchData[item][0][subitem]))))
								skip_next = True
						else:
							fields.append('{} {}'.format(subitem, self._returnCompatField(type(matchData[item][0][subitem]))))
					elif type(matchData[item][0][subitem]) is list:
						#This adds fields for runes and masteries.
						fields.append('{} {}'.format(subitem, 'text'))
					elif type(matchData[item][0][subitem]) is dict:
						#This adds fields for match stats and deltas.
						for dictitem in matchData[item][0][subitem]:
							if type(matchData[item][0][subitem][dictitem]) is not dict:
								fields.append('{} {}'.format(dictitem, self._returnCompatField(type(matchData[item][0][subitem][dictitem]))))
							elif type(matchData[item][0][subitem][dictitem]) is dict:
								fields.append('{}_zeroToTen real'.format(dictitem.replace('Deltas', '')))
								fields.append('{}_tenToTwenty real'.format(dictitem.replace('Deltas', '')))
								fields.append('{}_twentyToThirty real'.format(dictitem.replace('Deltas', '')))
								fields.append('{}_thirtyToEnd real'.format(dictitem.replace('Deltas', '')))
		self._createTable('matches', ','.join(fields))

	def addMatchHistory(self, playerId, newRecord=False):
		player = Request().retrievePlayerData(playerId)
		if newRecord:
			data = [{'field':'lastUpdated', 'value':int(time.time())}]
			for item in player['summoner']:
				data.append({'field': item, 'value': player['summoner'][item]})
			self._insert('players', data) 
		else:
			self._update('players', 'lastUpdated', str(int(time.time())), {'name':playerId})
		#------------------------
		matches = player['match_history']['matches']
		total_matches_added = 0
		for matchData in matches:
			skip_next = False
			if self.hasMatchRecord(matchData['matchId'], matchData['participantIdentities'][0]['player']['summonerName']):
				pass
			else:
				data = []
				total_matches_added += 1
				for item in matchData:
					if type(matchData[item]) is not list:
						data.append({'field': item, 'value': matchData[item]})
					else:
						for subitem in matchData[item][0]:
							if type(matchData[item][0][subitem]) is not list and type(matchData[item][0][subitem]) is not dict:
								if subitem == 'participantId':
									if not skip_next:
										data.append({'field': subitem, 'value': matchData[item][0][subitem]})
										skip_next = True
								else:
									data.append({'field': subitem, 'value': matchData[item][0][subitem]})
							elif type(matchData[item][0][subitem]) is list:
								#Placeholder for runes and masteries.
								#data.append({'field': subitem, 'value': ''})
								pass
							elif type(matchData[item][0][subitem]) is dict:
								#This adds match stats and deltas.
								for dictitem in matchData[item][0][subitem]:
									if type(matchData[item][0][subitem][dictitem]) is not dict:
										data.append({'field': dictitem, 'value': matchData[item][0][subitem][dictitem]})
									elif type(matchData[item][0][subitem][dictitem]) is dict:
										for subdictitem in matchData[item][0][subitem][dictitem]:
											data.append({'field': '{}_{}'.format(dictitem.replace('Deltas', ''),subdictitem), 'value': matchData[item][0][subitem][dictitem][subdictitem]})
				self._insert('matches', data)
						
		return total_matches_added
		
	def getPlayerLastUpdated(self, playerId):
		return self.db.execute("SELECT lastUpdated FROM players WHERE name=?", (playerId,))
	
	def hasMatchRecord(self, matchId, playerName):
		query = "SELECT matchId, summonerName FROM matches WHERE (matchId=? AND summonerName=?)"
		record = self.db.execute(query, (matchId, playerName)).fetchone()
		if record == None:
			return False
		else:
			return True
			
	def getSummonerId(self, playerId):
		query = "SELECT id FROM players WHERE name=?"
		return self.db.execute(query, [playerId]).fetchone()[0]
		
	def getMatches(self, summonerId, hours=0):
		matches = []
		if hours == 0:
			query = "SELECT * FROM matches WHERE summonerId=?"
			matchesData = self.db.execute(query, [summonerId]).fetchall()
		else:
			timeMax = ((int(time.time())/60/60)-hours)*60*60*1000
			query = "SELECT * FROM matches WHERE (summonerId=? AND matchCreation >=?)"
			matchesData = self.db.execute(query, [summonerId, timeMax]).fetchall()
		
		for matchData in matchesData:
			matchKey = {}
			for i, field in enumerate(self.db.execute("PRAGMA table_info('matches')").fetchall()):
				matchKey[field[1]] = matchData[i]
			matches.append(matchKey)
			
		return matches
		
