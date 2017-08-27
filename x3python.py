'''
@file:		x3python.py
@author: 	Gareth Hellmann
@date:		14 Jan 2014
'''

import SOAPpy
from lxml import objectify
from lxml import etree

class x3pyconnection(object):
	'''
	py connection client to X3 web service
	'''
	def __init__(self, username, password):
		self.url = "http://x3server:28980/adxwsvc/services/CAdxWebServiceXmlCC?wsdl"
		self.codeLang = "ENG"
		self.poolAlias = "X3"
		self.requestConfig = "adxwss.trace.on=off&amp;adonix.trace.on=off"
		self.username = username
		self.password = password
		self.result = None
		self.client = SOAPpy.SOAPProxy(self.url)
		self.context = {"codeLang" : self.codeLang, \
						"codeUser" : self.username, \
						"password" : self.password, \
						"poolAlias" : self.poolAlias, \
						"requestConfig" : self.requestConfig}
	
	def __repr__(self):
		return "< class x3python.x3pyconnection() >"
	
	def __str__(self):
		return "< class x3python.x3pyconnection() >"
	
class x3pyapi(object):
	'''
	py api client to X3 web service
	'''
	def __init__(self, x3pyconnection):
		self.connection = x3pyconnection

	def __repr__(self):
		return "< class x3python.x3pyapi() >"
	
	def __str__(self):
		return "< class x3python.x3pyapi() >"
	
	def getDescription(self, ws):
		'''
		get web service description
		
		ws: web service name
		'''
		self.connection.result = self.connection.client.getDescription(self.connection.context, ws)
	
	def run(self, ws, xml):
		'''
		run subprogram
		
		ws: 	web service name
		xml:	xml in correct structure
		'''
		if type(xml) is str:
			xml = objectify.fromstring(xml)
		
		xml.tag = "PARAM"
		self.connection.result = self.connection.client.run(self.connection.context, ws, etree.tostring(xml))
		
	def query(self, ws, key = ["*"], limit = 16383):
		'''
		query object list
		
		ws: 	web service name
		key: 	array of key string values - default all
		limit:	result row limit - default max
		'''
		limit = SOAPpy.Types.intType(limit)
		self.connection.result = self.connection.client.query(self.connection.context, ws, self.key(key), limit)
		
	def read(self, ws, key):
		'''
		read object
		
		ws:		web service name
		key:	array of key string value
		'''
		self.connection.result = self.connection.client.read(self.connection.context, ws, self.key(key))

	def save(self, ws, xml):
		'''
		save object
		
		ws:		web service name
		xml:	xml to be saved in objectified structure
		'''
		if type(xml) is str:
			xml = objectify.fromstring(xml)
		
		xml = self.stripEmptyTags(xml)
		xml.tag = "PARAM"
		self.connection.result = self.connection.client.save(self.connection.context, ws, etree.tostring(xml))

	def modify(self, ws, key, xml):
		'''
		modify object
		
		ws:		web service name
		key:	array of key string value
		xml:	xml to be modified in correct structure
		'''
		if type(xml) is str:
			xml = objectify.fromstring(xml)
		
		xml = self.stripSpecificTag(xml, "ADXTEC")
		xml.tag = "PARAM"
		self.connection.result = self.connection.client.modify(self.connection.context, ws, self.key(key), etree.tostring(xml))
		
	def delete(self, ws, key):
		'''
		delete object
		
		ws:		web service name
		key:	array of key string value
		'''
		self.connection.result = self.connection.client.delete(self.connection.context, ws, self.key(key))
	
	def actionObject(self, ws, action, key):
		'''
		action object
		
		ws:		web service name
		action:	action code to execute
		key:	array of key string value
		'''
		self.connection.result = self.connection.client.actionObject(self.connection.context, ws, action, self.key(key))
	
	def insertLines(self, ws, key, linekey, xml):
		'''
		insert lines object
		
		ws:			web service name
		key:		array of key string value
		linekey:	line id within the table
		xml:		xml to be inserted in correct structure
		'''
		if type(xml) is str:
			xml = objectify.fromstring(xml)
		
		xml.tag = "PARAM"
		xml = self.stripEmptyTags(xml)
		self.modify(ws, key, xml)
		
	def deleteLines(self, ws, key, subkey, linekey):
		'''
		delete lines object
		
		ws:			web service name
		key:		array of key string value
		subkey:		key of the xml table that contains the lines
		linekey:	line id within the table
		'''
		self.connection.result = self.connection.client.deleteLines(self.connection.context, ws, self.key(key), subkey, linekey)
	
	def key(self, key):
		'''
		build key array
		'''
		if type(key) is str:
			key = [key]
			
		keys = []
		
		for cnt, item in enumerate(key):
			keys.append(dict([('value', str(item)), ('key', str(cnt))]))
		
		return keys
	
	def getResultXML(self, objectified=False, pretty_xml=False):
		'''
		get web service xml result from x3
		
		objectified:	get xml objectified
		pretty_xml:		get xml in readable layout
		'''
		if objectified:
			return objectify.fromstring(self.connection.result.resultXml.encode("utf-8"))
		else:
			return etree.tostring(objectify.fromstring(self.connection.result.resultXml.encode("utf-8")), pretty_print=pretty_xml)
	
	def getResultXMLStructured(self, save=False, saveline=False, table="", lineCount=1, lineStart=1):
		'''
		get web service xml structure for save, save line, and run from x3 objectified
		
		save: 		get structured xml for save
		saveline:	get structured xml for line save
		table:		specific table for line save
		lineCount:  number of lines within a table to be created
		lineStart:	start at line number for adding
		'''
		param = ""
		description = self.getResultXML(objectified=True)
		
		for grp in description.ADXDATA.GRP:
			if "TYB" in grp.attrib:
				if grp.attrib["TYB"] == "Table":
					if save:
						if grp.attrib["NAM"] == table:
							tab = objectify.SubElement(description.ADXDATA, "TAB", ID = grp.attrib["NAM"])
							lin = objectify.SubElement(tab, "LIN")
							
							for fld in grp.FLD:
								objectify.SubElement(lin, "FLD", NAME = fld.attrib["NAM"])
					
					if saveline and grp.attrib["NAM"] == table:
						param = objectify.Element("PARAM")
						tab = objectify.SubElement(param, "TAB", ID = grp.attrib["NAM"])
						
						for i in range (lineStart-1, lineCount):
							lin = objectify.SubElement(tab, "LIN", NUM = str(i+1))
							
							for fld in grp.FLD:
								objectify.SubElement(lin, "FLD", NAME = fld.attrib["NAM"])
			
			if "DIM" in grp.attrib:
				if int(grp.attrib["DIM"]) > 1:
					description.ADXDATA.remove(grp)
				else:
					grp.set("ID", grp.attrib["NAM"])
					
					for fld in grp.FLD:
						fld.set("NAME", fld.attrib["NAM"])
			
			else:
				grp.set("ID", grp.attrib["NAM"])
				
				for fld in grp.FLD:
					fld.set("NAME", fld.attrib["NAM"])
		
		if not saveline:
			param = description.ADXDATA
			
		objectify.deannotate(param, pytype=True, cleanup_namespaces=True)
		
		return param
	
	def addToResultXMLStructured(self, xml, parentTagName, tagName, newTagType, subTagType="", subTagName=""):
		'''
		add extra tags to the structured xml
		
		xml:			xml in objectified format
		parentTagName:	parent tag name
		tagName:		tag name to be replaced
		newTagType:		tag type to be addeed
		subTagType:		sub tag type to be addeed
		subTagName:		sub tag name to be addeed
		'''
		for grp in xml.GRP:
			if grp.attrib["ID"] == parentTagName:
				for fld in grp.FLD:
					if fld.attrib["NAME"] == tagName:
						grp.remove(fld)
						newTag = objectify.SubElement(grp, newTagType, NAME = tagName)
						
						if len(subTagType) > 0:
							if len(subTagName) > 0:
								subTag = objectify.SubElement(newTag, subTagType, NAME = subTagName)
							else:
								subTag = objectify.SubElement(newTag, subTagType)
						
		return xml
	
	def getLocalMenus(self):
		'''
		get web service local menus as dictionary
		'''
		menus = {}
		menu = self.getResultXML(objectified=True)
		
		for mnu in menu.ADXMEN.MNU:
			menuItem = {}
			
			for val in mnu.VAL:
				menuItem[val.attrib["IND"]] = val.attrib["C_" + self.connection.codeLang]
			
			menus[mnu.attrib["NO"]] = menuItem
			
		return menus
		
	def getResultStatus(self):
		'''
		get web service status result from x3
		'''
		return self.connection.result.status
	
	def getResultMessages(self):
		'''
		get web service array of messages from x3
		'''
		return self.connection.result.messages
	
	def getResultMessageString(self):
		'''
		get web service messages as string from x3
		'''
		messageString = ""
		
		for message in self.connection.result.messages:
			if len(messageString) > 0:
				messageString += "\r\n"
			
			messageString += "(" + str(message["type"]) + "): " + str(message["message"])
			
		return messageString
	
	def getValue(self, xml, group="", table="", line="", field=""):
		'''
		get web service text values from x3
		
		xml:	xml to be inserted in correct structure
		group:	group ID
		table:	table ID
		line:	line number
		field:	field name
		'''
		if type(xml) is str:
			xml = objectify.fromstring(xml)
		
		xpathStr = ""
		
		if len(group) > 0:
			xpathStr += "GRP[@ID='" + group + "']/"
		
		if len(table) > 0:
			xpathStr += "TAB[@ID='" + table + "']/"
		
		if len(line) > 0:
			xpathStr += "LIN[@NUM='" + line + "']/"
		
		if len(field) > 0:
			xpathStr += "FLD[@NAME='" + field + "']"
		
		if len(xpathStr) > 0:
			xml = xml.xpath("//" + xpathStr)[0]
		
		return xml
	
	def stripEmptyTags(self, xml):
		'''
		strip empty tags from xml
		
		xml:	xml to be stripped in objectified format
		'''
		if xml.find("GRP") is not None:
			for grp in xml.GRP:
				for fld in grp.FLD:
					if fld == "":
						grp.remove(fld)
		
		if xml.find("TAB") is not None:
			for tab in xml.TAB:
				for lin in tab.LIN:
					for fld in lin.FLD:
						if fld == "":
							lin.remove(fld)
		
		return xml
	
	def stripSpecificTag(self, xml, tag):
		'''
		strip specific tag from xml
		
		xml:	xml to be stripped in objectified format
		tag:	tag to be removed
		'''
		if xml.find("GRP") is not None:
			for grp in xml.GRP:
				if grp.attrib["ID"] == tag:
					xml.remove(grp)
		
		if xml.find("TAB") is not None:
			for tab in xml.TAB:
				if tab.attrib["ID"] == tag:
					xml.remove(tab)
		
		return xml