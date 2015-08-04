from time import sleep
from LoLDB import Database as DB
from LoLMatch import Match

class Player():
	
	def __init__(self, playerId):
		self.db = DB()
		self.playerId = playerId
	
	def _getSummonerId(self):
		return self.db.getSummonerId(self.playerId)
	
	def hasRecord(self):
		try:
			self.db._select('players', 'name', self.playerId).fetchall()[0]
			return True
		except:
			return False
		
	def lastUpdated(self):
		return self.db.getPlayerLastUpdated(self.playerId).fetchone()[0]
		
	def retrieveMatches(self, newPlayer=False):
		return self.db.addMatchHistory(self.playerId, newRecord=newPlayer)
	
	def getMatches(self, hours=0, days=0):
		if days > 0:
			hours = days*24+hours
		matches = []
		for match in self.db.getMatches(self._getSummonerId(), hours):
			matches.append(Match(match))
		return matches
	
	def getRecentMatches(self):
		return self.getMatches(days=1)
		
	def getWeeksMatches(self):
		return self.getMatches(days=7)
		
	def getMonthsMatches(self):
		return self.getMatches(days=30)
