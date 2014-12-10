# -*- coding: utf-8 -*-
#
# PartMgr - Database
#
# Copyright 2014 Michael Buesch <m@bues.ch>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from partmgr.core.parameter import *
from partmgr.core.category import *
from partmgr.core.stockitem import *
from partmgr.core.part import *
from partmgr.core.storage import *
from partmgr.core.footprint import *
from partmgr.core.image import *
from partmgr.core.location import *
from partmgr.core.origin import *
from partmgr.core.supplier import *
from partmgr.core.util import *

import sqlite3 as sql


class Database(QObject):
	"Part database interface."

	# Database version number
	DB_VERSION	= 0

	# User editable parameters
	USER_PARAMS = {
		# "name"	: (description, default-value)
		"currency"	: ("Price currency", Param_Currency.CURR_EUR),
	}

	def __init__(self, filename, withCommitTimer=True):
		QObject.__init__(self)
		if withCommitTimer:
			self.__commitTimer = QTimer(self)
			self.__commitTimer.setSingleShot(True)
			self.__commitTimer.timeout.connect(self.__commitTimerTrig)
		else:
			self.__commitTimer = None
		self.__commitTimerSchedBlock = 0
		try:
			self.db = sql.connect(str(filename))
			self.db.text_factory = str
			if self.__sqlIsEmpty():
				# This is an empty database
				self.__initTables()
				ver = Parameter("partmgr_db_version",
						data = self.DB_VERSION)
				self.modifyParameter(ver)
			else:
				ver = self.getGlobalParameter(
					"partmgr_db_version")
				ver = ver.getDataInt() if ver else None
				if ver is None or ver != self.DB_VERSION:
					raise PartMgrError("Invalid database "
						    "version")
			self.filename = filename
			self.__setUserParameterDefaults()
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def __repr__(self):
		return "Database(%s)" % str(self.filename)

	def commit(self):
		self.__commitTimerSchedBlock += 1
		if self.__commitTimer:
			self.__commitTimer.stop()
		try:
			rev = None
			try:
				rev = self.getGlobalParameter("partmgr_db_revision")
				if not rev:
					raise ValueError
				revNr = rev.getDataInt()
			except (PartMgrError, ValueError) as e:
				try:
					if rev:
						self.delParameter(rev)
				except PartMgrError:
					pass
				rev = Parameter("partmgr_db_revision",
						data = 0)
				revNr = rev.getDataInt()
			revNr += 1
			rev.setData(revNr)
			self.modifyParameter(rev)
			print("Committing database (rev %d)..." % revNr)
			self.db.commit()
		finally:
			self.__commitTimerSchedBlock -= 1

	def __commitTimerTrig(self):
		self.commit()

	def scheduleCommit(self, seconds=5.0):
		if self.__commitTimerSchedBlock:
			return
		if not self.__commitTimer:
			return
		self.__commitTimer.start(int(round(seconds * 1000)))

	def close(self, commit=True):
		print("Closing database%s..." %\
		      ("" if commit else " (no commit)"))
		if commit:
			self.__collectGarbage()
			self.commit()
		self.db.close()
		self.filename = None

	def __collectGarbage(self):
		pass#TODO collect orphan storages, origins and all other orphan objects.
		self.db.cursor().execute("VACUUM;")

	def __databaseError(self, exception):
		if isinstance(exception, ValueError):
			msg = "Database format error: " +\
				str(exception)
		else:
			msg = "SQL error: " + str(exception)
		print(msg)
		raise PartMgrError(msg)

	def __initTables(self):
		entityColumns = "id INTEGER PRIMARY KEY AUTOINCREMENT, "\
				"name TEXT, description TEXT, "\
				"flags INTEGER, "\
				"createTimeStamp INTEGER, "\
				"modifyTimeStamp INTEGER"
		tables = (
			"parameters(" + entityColumns + ", "
				   "parentType INTEGER, parent INTEGER, "
				   "data TEXT)",
			"parts(" + entityColumns + ", "
			      "category INTEGER)",
			"categories(" + entityColumns + ", "
				   "parent INTEGER)",
			"suppliers(" + entityColumns + ", "
				  "url TEXT)",
			"locations(" + entityColumns + ")",
			"footprints(" + entityColumns + ", "
				   "image TEXT)",
			"stock(" + entityColumns + ", "
			      "part INTEGER, category INTEGER, "
			      "footprint INTEGER, "
			      "minQuantity INTEGER, "
			      "targetQuantity INTEGER, "
			      "quantityUnits INTEGER)",
			"origins(" + entityColumns + ", "
				"stockItem INTEGER, supplier INTEGER, "
				"orderCode TEXT, "
				"price FLOAT, priceTimeStamp INTEGER)",
			"storages(" + entityColumns + ", "
				 "stockItem INTEGER, location INTEGER, "
				 "quantity INTEGER)",
			#TODO add a history
		)
		c = self.db.cursor()
		for table in tables:
			c.execute("CREATE TABLE IF NOT EXISTS %s;" % table)
		self.db.commit()

	def __sqlIsEmpty(self):
		try:
			c = self.db.cursor()
			c.execute("ANALYZE;")
			c.execute("SELECT tbl FROM sqlite_stat1;")
			return not bool(c.fetchone())
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getParameterByParent(self, paramName, parentType, parent):
		try:
			c = self.db.cursor()
			c.execute("SELECT id, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "parentType, parent, data "
				  "FROM parameters "
				  "WHERE name=? AND parentType=? AND parent=?;",
				  (toBase64(paramName),
				   int(parentType),
				   Entity.toId(parent)))
			data = c.fetchone()
			if not data:
				return None
			return Parameter(name = paramName,
					 description = fromBase64(data[1]),
					 flags = int(data[2]),
					 createTimeStamp = int(data[3]),
					 modifyTimeStamp = int(data[4]),
					 parentType = int(data[5]),
					 parent = int(data[6]),
					 data = fromBase64(data[7], toBytes=True),
					 id = int(data[0]),
					 db = self)
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getAllParametersByParent(self, parentType, parent):
		parentId = Entity.toId(parent)
		try:
			c = self.db.cursor()
			c.execute("SELECT id, name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "data "
				  "FROM parameters "
				  "WHERE parentType=? AND parent=? "
				  "ORDER BY id;",
				  (parentType, parentId))
			data = c.fetchall()
			if not data:
				return []
			return [ Parameter(name = fromBase64(d[1]),
					   description = fromBase64(d[2]),
					   flags = int(d[3]),
					   createTimeStamp = int(d[4]),
					   modifyTimeStamp = int(d[5]),
					   parentType = parentType,
					   parent = parent,
					   data = fromBase64(d[6], toBytes=True),
					   id = int(d[0]),
					   db = self)
				for d in data ]
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getGlobalParameter(self, paramName):
		return self.getParameterByParent(paramName,
						 Parameter.PTYPE_GLOBAL,
						 Entity.NO_ID)

	def getUserParameters(self):
		ret = []
		for name in self.USER_PARAMS.keys():
			param = self.getGlobalParameter(name)
			if param:
				ret.append(param)
		ret.sort(key=lambda p: p.getName())
		return ret

	def __setUserParameterDefaults(self):
		for name in self.USER_PARAMS.keys():
			if self.getGlobalParameter(name):
				# Does exist. Skip it.
				continue
			param = Parameter(name,
				description = self.USER_PARAMS[name][0],
				data = self.USER_PARAMS[name][1])
			self.modifyParameter(param)

	def modifyParameter(self, parameter):
		parameter.updateModifyTimeStamp()
		try:
			c = self.db.cursor()
			if parameter.inDatabase(self):
				c.execute("UPDATE parameters "
					  "SET name=?, description=?, flags=?, "
					  "createTimeStamp=?, modifyTimeStamp=?, "
					  "parentType=?, parent=?, data=? "
					  "WHERE id=?;",
					  (toBase64(parameter.name),
					   toBase64(parameter.description),
					   int(parameter.flags),
					   int(parameter.createTimeStamp.getStampInt()),
					   int(parameter.modifyTimeStamp.getStampInt()),
					   int(parameter.parentType),
					   int(parameter.parent),
					   toBase64(parameter.data),
					   int(parameter.id)))
			else:
				c.execute("INSERT INTO "
					  "parameters(name, description, "
					  "flags, "
					  "createTimeStamp, modifyTimeStamp, "
					  "parentType, parent, data) "
					  "VALUES(?,?,?,?,?,?,?,?);",
					  (toBase64(parameter.name),
					   toBase64(parameter.description),
					   int(parameter.flags),
					   int(parameter.createTimeStamp.getStampInt()),
					   int(parameter.modifyTimeStamp.getStampInt()),
					   int(parameter.parentType),
					   int(parameter.parent),
					   toBase64(parameter.data)))
				parameter.id = c.lastrowid
				parameter.db = self
			self.scheduleCommit()
			return parameter.id
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def delParameter(self, parameter):
		id = Entity.toId(parameter)
		try:
			c = self.db.cursor()
			c.execute("DELETE FROM parameters "
				  "WHERE id=?;",
				  (int(id),))
			self.scheduleCommit()
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getPart(self, part):
		id = Entity.toId(part)
		try:
			c = self.db.cursor()
			c.execute("SELECT name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "category "
				  "FROM parts "
				  "WHERE id=?;",
				  (id,))
			data = c.fetchone()
			if not data:
				return None
			return Part(name = fromBase64(data[0]),
				    description = fromBase64(data[1]),
				    flags = int(data[2]),
				    createTimeStamp = int(data[3]),
				    modifyTimeStamp = int(data[4]),
				    category = int(data[5]),
				    id = id,
				    db = self)
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getParts(self):
		try:
			c = self.db.cursor()
			c.execute("SELECT id, name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "category "
				  "FROM parts;")
			data = c.fetchall()
			if not data:
				return []
			return [ Part(name = fromBase64(d[1]),
				      description = fromBase64(d[2]),
				      flags = int(d[3]),
				      createTimeStamp = int(d[4]),
				      modifyTimeStamp = int(d[5]),
				      category = int(d[6]),
				      id = int(d[0]),
				      db = self)
				for d in data ]
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getPartsByCategory(self, category):
		categoryId = Entity.toId(category)
		try:
			c = self.db.cursor()
			c.execute("SELECT id, name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "category "
				  "FROM parts "
				  "WHERE category=? "
				  "ORDER BY id;",
				  (categoryId,))
			data = c.fetchall()
			if not data:
				return []
			return [ Part(name = fromBase64(d[1]),
				      description = fromBase64(d[2]),
				      flags = int(d[3]),
				      createTimeStamp = int(d[4]),
				      modifyTimeStamp = int(d[5]),
				      category = int(d[6]),
				      id = int(d[0]),
				      db = self)
				for d in data ]
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def modifyPart(self, part):
		part.updateModifyTimeStamp()
		try:
			c = self.db.cursor()
			if part.inDatabase(self):
				c.execute("UPDATE parts "
					  "SET name=?, description=?, flags=?, "
					  "createTimeStamp=?, "
					  "modifyTimeStamp=?, "
					  "category=? "
					  "WHERE id=?;",
					  (toBase64(part.name),
					   toBase64(part.description),
					   int(part.flags),
					   int(part.createTimeStamp.getStampInt()),
					   int(part.modifyTimeStamp.getStampInt()),
					   int(part.category),
					   int(part.id)))
			else:
				c.execute("INSERT INTO "
					  "parts(name, description, flags, "
					  "createTimeStamp, "
					  "modifyTimeStamp, "
					  "category) "
					  "VALUES(?,?,?,?,?,?);",
					  (toBase64(part.name),
					   toBase64(part.description),
					   int(part.flags),
					   int(part.createTimeStamp.getStampInt()),
					   int(part.modifyTimeStamp.getStampInt()),
					   int(part.category)))
				part.id = c.lastrowid
				part.db = self
			self.scheduleCommit()
			return part.id
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def delPart(self, part):
		id = Entity.toId(part)
		try:
			c = self.db.cursor()
			c.execute("DELETE FROM parts WHERE id=?;",
				  (int(id),))
			self.scheduleCommit()
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getCategory(self, category):
		id = Entity.toId(category)
		try:
			c = self.db.cursor()
			c.execute("SELECT name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "parent "
				  "FROM categories "
				  "WHERE id=?;",
				  (int(id),))
			data = c.fetchone()
			if not data:
				return None
			return Category(name = fromBase64(data[0]),
					description = fromBase64(data[1]),
					flags = int(data[2]),
					createTimeStamp = int(data[3]),
					modifyTimeStamp = int(data[4]),
					parent = int(data[5]),
					id = id,
					db = self)
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getRootCategories(self):
		return self.getChildCategories(None)

	def countRootCategories(self):
		return self.countChildCategories(None)

	def getChildCategories(self, parentCategory):
		parentId = Entity.toId(parentCategory)
		try:
			c = self.db.cursor()
			c.execute("SELECT id, name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "parent "
				  "FROM categories "
				  "WHERE parent=? ORDER BY id;",
				  (int(parentId),))
			data = c.fetchall()
			if not data:
				return []
			return [ Category(name = fromBase64(d[1]),
					  description = fromBase64(d[2]),
					  flags = int(d[3]),
					  createTimeStamp = int(d[4]),
					  modifyTimeStamp = int(d[5]),
					  parent = int(d[6]),
					  id = int(d[0]),
					  db = self)
				for d in data ]
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def countChildCategories(self, parentCategory):
		parentId = Entity.toId(parentCategory)
		try:
			c = self.db.cursor()
			c.execute("SELECT COUNT(*) "
				  "FROM categories "
				  "WHERE parent=?;",
				  (int(parentId),))
			data = c.fetchone()
			if not data:
				return 0
			return int(data[0])
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def modifyCategory(self, category):
		category.updateModifyTimeStamp()
		try:
			c = self.db.cursor()
			if category.inDatabase(self):
				c.execute("UPDATE categories "
					  "SET name=?, description=?, flags=?, "
					  "createTimeStamp=?, "
					  "modifyTimeStamp=?, "
					  "parent=? "
					  "WHERE id=?;",
					  (toBase64(category.name),
					   toBase64(category.description),
					   int(category.flags),
					   int(category.createTimeStamp.getStampInt()),
					   int(category.modifyTimeStamp.getStampInt()),
					   int(category.parent),
					   int(category.id)))
			else:
				c.execute("INSERT INTO "
					  "categories(name, description, flags, "
					  "createTimeStamp, "
					  "modifyTimeStamp, "
					  "parent) "
					  "VALUES(?,?,?,?,?,?);",
					  (toBase64(category.name),
					   toBase64(category.description),
					   int(category.flags),
					   int(category.createTimeStamp.getStampInt()),
					   int(category.modifyTimeStamp.getStampInt()),
					   int(category.parent)))
				category.id = c.lastrowid
				category.db = self
			self.scheduleCommit()
			return category.id
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def delCategory(self, category):
		id = Entity.toId(category)
		try:
			c = self.db.cursor()
			c.execute("DELETE FROM categories "
				  "WHERE id=?;",
				  (int(id),))
			self.scheduleCommit()
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getSupplier(self, supplier):
		id = Entity.toId(supplier)
		try:
			c = self.db.cursor()
			c.execute("SELECT name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "url "
				  "FROM suppliers "
				  "WHERE id=?;",
				  (int(id),))
			data = c.fetchone()
			if not data:
				return None
			return Supplier(name = fromBase64(data[0]),
					description = fromBase64(data[1]),
					flags = int(data[2]),
					createTimeStamp = int(data[3]),
					modifyTimeStamp = int(data[4]),
					url = fromBase64(data[5]),
					id = id,
					db = self)
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getSuppliers(self):
		try:
			c = self.db.cursor()
			c.execute("SELECT id, name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "url "
				  "FROM suppliers;")
			data = c.fetchall()
			if not data:
				return []
			return [ Supplier(name = fromBase64(d[1]),
					  description = fromBase64(d[2]),
					  flags = int(d[3]),
					  createTimeStamp = int(d[4]),
					  modifyTimeStamp = int(d[5]),
					  url = fromBase64(d[6]),
					  id = int(d[0]),
					  db = self)
				for d in data ]
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def modifySupplier(self, supplier):
		supplier.updateModifyTimeStamp()
		try:
			c = self.db.cursor()
			if supplier.inDatabase(self):
				c.execute("UPDATE suppliers "
					  "SET name=?, description=?, flags=?, "
					  "createTimeStamp=?, "
					  "modifyTimeStamp=?, "
					  "url=? "
					  "WHERE id=?;",
					  (toBase64(supplier.name),
					   toBase64(supplier.description),
					   int(supplier.flags),
					   int(supplier.createTimeStamp.getStampInt()),
					   int(supplier.modifyTimeStamp.getStampInt()),
					   toBase64(supplier.url),
					   int(supplier.id)))
			else:
				c.execute("INSERT INTO "
					  "suppliers(name, description, flags, "
					  "createTimeStamp, "
					  "modifyTimeStamp, "
					  "url) "
					  "VALUES(?,?,?,?,?,?);",
					  (toBase64(supplier.name),
					   toBase64(supplier.description),
					   int(supplier.flags),
					   int(supplier.createTimeStamp.getStampInt()),
					   int(supplier.modifyTimeStamp.getStampInt()),
					   toBase64(supplier.url)))
				supplier.id = c.lastrowid
				supplier.db = self
			self.scheduleCommit()
			return supplier.id
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def delSupplier(self, supplier):
		id = Entity.toId(supplier)
		try:
			c = self.db.cursor()
			c.execute("DELETE FROM suppliers "
				  "WHERE id=?;",
				  (int(id),))
			self.scheduleCommit()
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getLocation(self, location):
		id = Entity.toId(location)
		try:
			c = self.db.cursor()
			c.execute("SELECT name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp "
				  "FROM locations "
				  "WHERE id=?;",
				  (int(id),))
			data = c.fetchone()
			if not data:
				return None
			return Location(name = fromBase64(data[0]),
					description = fromBase64(data[1]),
					flags = int(data[2]),
					createTimeStamp = int(data[3]),
					modifyTimeStamp = int(data[4]),
					id = id,
					db = self)
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getLocations(self):
		try:
			c = self.db.cursor()
			c.execute("SELECT id, name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp "
				  "FROM locations;")
			data = c.fetchall()
			if not data:
				return []
			return [ Location(name = fromBase64(d[1]),
					  description = fromBase64(d[2]),
					  flags = int(d[3]),
					  createTimeStamp = int(d[4]),
					  modifyTimeStamp = int(d[5]),
					  id = int(d[0]),
					  db = self)
				for d in data ]
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def modifyLocation(self, location):
		location.updateModifyTimeStamp()
		try:
			c = self.db.cursor()
			if location.inDatabase(self):
				c.execute("UPDATE locations "
					  "SET name=?, description=?, flags=? "
					  "createTimeStamp=?, "
					  "modifyTimeStamp=? "
					  "WHERE id=?;",
					  (toBase64(location.name),
					   toBase64(location.description),
					   int(location.flags),
					   int(location.createTimeStamp.getStampInt()),
					   int(location.modifyTimeStamp.getStampInt()),
					   int(location.id)))
			else:
				c.execute("INSERT INTO "
					  "locations(name, description, flags, "
					  "createTimeStamp, "
					  "modifyTimeStamp) "
					  "VALUES(?,?,?,?,?);",
					  (toBase64(location.name),
					   toBase64(location.description),
					   int(location.flags),
					   int(location.createTimeStamp.getStampInt()),
					   int(location.modifyTimeStamp.getStampInt())))
				location.id = c.lastrowid
				location.db = self
			self.scheduleCommit()
			return location.id
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def delLocation(self, location):
		id = Entity.toId(location)
		try:
			c = self.db.cursor()
			c.execute("DELETE FROM locations "
				  "WHERE id=?;",
				  (int(id),))
			self.scheduleCommit()
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getFootprint(self, footprint):
		id = Entity.toId(footprint)
		try:
			c = self.db.cursor()
			c.execute("SELECT name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "image "
				  "FROM footprints "
				  "WHERE id=?;",
				  (int(id),))
			data = c.fetchone()
			if not data:
				return None
			return Footprint(name = fromBase64(data[0]),
					 description = fromBase64(data[1]),
					 flags = int(data[2]),
					 createTimeStamp = int(data[3]),
					 modifyTimeStamp = int(data[4]),
					 image = Image(data[5]),
					 id = id,
					 db = self)
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getFootprints(self):
		try:
			c = self.db.cursor()
			c.execute("SELECT id, name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "image "
				  "FROM footprints;")
			data = c.fetchall()
			if not data:
				return []
			return [ Footprint(name = fromBase64(d[1]),
					   description = fromBase64(d[2]),
					   flags = int(d[3]),
					   createTimeStamp = int(d[4]),
					   modifyTimeStamp = int(d[5]),
					   image = Image(d[6]),
					   id = int(d[0]),
					   db = self)
				for d in data ]
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def modifyFootprint(self, footprint):
		footprint.updateModifyTimeStamp()
		try:
			c = self.db.cursor()
			if footprint.inDatabase(self):
				c.execute("UPDATE footprints "
					  "SET name=?, description=?, flags=?, "
					  "createTimeStamp=?, "
					  "modifyTimeStamp=?, "
					  "image=? "
					  "WHERE id=?;",
					  (toBase64(footprint.name),
					   toBase64(footprint.description),
					   int(footprint.flags),
					   int(footprint.createTimeStamp.getStampInt()),
					   int(footprint.modifyTimeStamp.getStampInt()),
					   footprint.image.toString(),
					   int(footprint.id)))
			else:
				c.execute("INSERT INTO "
					  "footprints(name, description, flags, "
					  "createTimeStamp, "
					  "modifyTimeStamp, "
					  "image) "
					  "VALUES(?,?,?,?,?,?);",
					  (toBase64(footprint.name),
					   toBase64(footprint.description),
					   int(footprint.flags),
					   int(footprint.createTimeStamp.getStampInt()),
					   int(footprint.modifyTimeStamp.getStampInt()),
					   footprint.image.toString()))
				footprint.id = c.lastrowid
				footprint.db = self
			self.scheduleCommit()
			return footprint.id
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def delFootprint(self, footprint):
		id = Entity.toId(footprint)
		try:
			c = self.db.cursor()
			c.execute("DELETE FROM footprints "
				  "WHERE id=?;",
				  (int(id),))
			self.scheduleCommit()
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getStockItem(self, stockItem):
		id = Entity.toId(stockItem)
		try:
			c = self.db.cursor()
			c.execute("SELECT name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "part, category, footprint, "
				  "minQuantity, targetQuantity, "
				  "quantityUnits "
				  "FROM stock "
				  "WHERE id=?;",
				  (int(id),))
			data = c.fetchone()
			if not data:
				return None
			return StockItem(name = fromBase64(data[0]),
					 description = fromBase64(data[1]),
					 flags = int(data[2]),
					 createTimeStamp = int(data[3]),
					 modifyTimeStamp = int(data[4]),
					 part = int(data[5]),
					 category = int(data[6]),
					 footprint = int(data[7]),
					 minQuantity = int(data[8]),
					 targetQuantity = int(data[9]),
					 quantityUnits = int(data[10]),
					 id = id,
					 db = self)
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getStockItemsByCategory(self, category):
		categoryId = Entity.toId(category)
		try:
			c = self.db.cursor()
			c.execute("SELECT id, name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "part, category, footprint, "
				  "minQuantity, targetQuantity, "
				  "quantityUnits "
				  "FROM stock "
				  "WHERE category=? "
				  "ORDER BY id;",
				  (categoryId,))
			data = c.fetchall()
			if not data:
				return []
			return [ StockItem(name = fromBase64(d[1]),
					   description = fromBase64(d[2]),
					   flags = int(d[3]),
					   createTimeStamp = int(d[4]),
					   modifyTimeStamp = int(d[5]),
					   part = int(d[6]),
					   category = int(d[7]),
					   footprint = int(d[8]),
					   minQuantity = int(d[9]),
					   targetQuantity = int(d[10]),
					   quantityUnits = int(d[11]),
					   id = int(d[0]),
					   db = self)
				for d in data ]
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def countStockItemsByCategory(self, category):
		categoryId = Entity.toId(category)
		try:
			c = self.db.cursor()
			c.execute("SELECT COUNT(*) "
				  "FROM stock "
				  "WHERE category=?;",
				  (int(categoryId),))
			data = c.fetchone()
			if not data:
				return 0
			return int(data[0])
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def modifyStockItem(self, stockItem):
		stockItem.updateModifyTimeStamp()
		try:
			assert(Entity.isValidId(stockItem.category))
			c = self.db.cursor()
			if stockItem.inDatabase(self):
				c.execute("UPDATE stock "
					  "SET name=?, description=?, flags=?, "
					  "createTimeStamp=?, "
					  "modifyTimeStamp=?, "
					  "part=?, "
					  "category=?, footprint=?, "
					  "minQuantity=?, targetQuantity=?, "
					  "quantityUnits=? "
					  "WHERE id=?;",
					  (toBase64(stockItem.name),
					   toBase64(stockItem.description),
					   int(stockItem.flags),
					   int(stockItem.createTimeStamp.getStampInt()),
					   int(stockItem.modifyTimeStamp.getStampInt()),
					   int(stockItem.part),
					   int(stockItem.category),
					   int(stockItem.footprint),
					   int(stockItem.minQuantity),
					   int(stockItem.targetQuantity),
					   int(stockItem.quantityUnits),
					   int(stockItem.id)))
			else:
				c.execute("INSERT INTO "
					  "stock(name, description, flags, "
					  "createTimeStamp, "
					  "modifyTimeStamp, "
					  "part, category, footprint, "
					  "minQuantity, targetQuantity, "
					  "quantityUnits) "
					  "VALUES(?,?,?,?,?,?,?,?,?,?,?);",
					  (toBase64(stockItem.name),
					   toBase64(stockItem.description),
					   int(stockItem.flags),
					   int(stockItem.createTimeStamp.getStampInt()),
					   int(stockItem.modifyTimeStamp.getStampInt()),
					   int(stockItem.part),
					   int(stockItem.category),
					   int(stockItem.footprint),
					   int(stockItem.minQuantity),
					   int(stockItem.targetQuantity),
					   int(stockItem.quantityUnits)))
				stockItem.id = c.lastrowid
				stockItem.db = self
			self.scheduleCommit()
			return stockItem.id
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def delStockItem(self, stockItem):
		id = Entity.toId(stockItem)
		try:
			c = self.db.cursor()
			c.execute("DELETE FROM stock "
				  "WHERE id=?;",
				  (int(id),))
			self.scheduleCommit()
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getOrigin(self, origin):
		id = Entity.toId(origin)
		try:
			c = self.db.cursor()
			c.execute("SELECT name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "stockItem, supplier, orderCode, "
				  "price, priceTimeStamp "
				  "FROM origins "
				  "WHERE id=?;",
				  (int(id),))
			data = c.fetchone()
			if not data:
				return None
			return Origin(name = fromBase64(data[0]),
				      description = fromBase64(data[1]),
				      flags = int(data[2]),
				      createTimeStamp = int(data[3]),
				      modifyTimeStamp = int(data[4]),
				      stockItem = int(data[5]),
				      supplier = int(data[6]),
				      orderCode = fromBase64(data[7]),
				      price = float(data[8]),
				      priceTimeStamp = int(data[9]),
				      id = id,
				      db = self)
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getOriginsByStockItem(self, stockItem):
		stockItemId = Entity.toId(stockItem)
		try:
			c = self.db.cursor()
			c.execute("SELECT id, name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "supplier, orderCode, "
				  "price, priceTimeStamp "
				  "FROM origins "
				  "WHERE stockItem=?;",
				  (int(stockItemId),))
			data = c.fetchall()
			if not data:
				return []
			return [ Origin(name = fromBase64(d[1]),
					description = fromBase64(d[2]),
					flags = int(d[3]),
					createTimeStamp = int(d[4]),
					modifyTimeStamp = int(d[5]),
					stockItem = stockItemId,
					supplier = int(d[6]),
					orderCode = fromBase64(d[7]),
					price = float(d[8]),
					priceTimeStamp = int(d[9]),
					id = int(d[0]),
					db = self)
				 for d in data ]
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def modifyOrigin(self, origin):
		origin.updateModifyTimeStamp()
		try:
			c = self.db.cursor()
			if origin.inDatabase(self):
				c.execute("UPDATE origins "
					  "SET name=?, description=?, flags=?, "
					  "createTimeStamp=?, "
					  "modifyTimeStamp=?, "
					  "stockItem=?, supplier=?, "
					  "orderCode=?, "
					  "price=?, priceTimeStamp=? "
					  "WHERE id=?;",
					  (toBase64(origin.name),
					   toBase64(origin.description),
					   int(origin.flags),
					   int(origin.createTimeStamp.getStampInt()),
					   int(origin.modifyTimeStamp.getStampInt()),
					   int(origin.stockItem),
					   int(origin.supplier),
					   toBase64(origin.orderCode),
					   float(origin.price),
					   int(origin.getPriceTimeStampInt()),
					   int(origin.id)))
			else:
				c.execute("INSERT INTO "
					  "origins(name, description, flags, "
					  "createTimeStamp, "
					  "modifyTimeStamp, "
					  "stockItem, supplier, "
					  "orderCode, "
					  "price, priceTimeStamp) "
					  "VALUES(?,?,?,?,?,?,?,?,?,?);",
					  (toBase64(origin.name),
					   toBase64(origin.description),
					   int(origin.flags),
					   int(origin.createTimeStamp.getStampInt()),
					   int(origin.modifyTimeStamp.getStampInt()),
					   int(origin.stockItem),
					   int(origin.supplier),
					   toBase64(origin.orderCode),
					   float(origin.price),
					   int(origin.getPriceTimeStampInt())))
				origin.id = c.lastrowid
				origin.db = self
			self.scheduleCommit()
			return origin.id
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def delOrigin(self, origin):
		id = Entity.toId(origin)
		try:
			c = self.db.cursor()
			c.execute("DELETE FROM origins "
				  "WHERE id=?;",
				  (int(id),))
			self.scheduleCommit()
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getStorage(self, storage):
		id = Entity.toId(storage)
		try:
			c = self.db.cursor()
			c.execute("SELECT name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "stockItem, location, quantity "
				  "FROM storages "
				  "WHERE id=?;",
				  (int(id),))
			data = c.fetchone()
			if not data:
				return None
			return Storage(name = fromBase64(data[0]),
				       description = fromBase64(data[1]),
				       flags = int(data[2]),
				       createTimeStamp = int(data[3]),
				       modifyTimeStamp = int(data[4]),
				       stockItem = int(data[5]),
				       location = int(data[6]),
				       quantity = int(data[7]),
				       id = id,
				       db = self)
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def getStoragesByStockItem(self, stockItem):
		stockItemId = Entity.toId(stockItem)
		try:
			c = self.db.cursor()
			c.execute("SELECT id, name, description, flags, "
				  "createTimeStamp, "
				  "modifyTimeStamp, "
				  "location, quantity "
				  "FROM storages "
				  "WHERE stockItem=?;",
				  (int(stockItemId),))
			data = c.fetchall()
			if not data:
				return []
			return [ Storage(name = fromBase64(d[1]),
					 description = fromBase64(d[2]),
					 flags = int(d[3]),
					 createTimeStamp = int(d[4]),
					 modifyTimeStamp = int(d[5]),
					 stockItem = stockItemId,
					 location = int(d[6]),
					 quantity = int(d[7]),
					 id = int(d[0]),
					 db = self)
				for d in data ]
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def modifyStorage(self, storage):
		storage.updateModifyTimeStamp()
		try:
			c = self.db.cursor()
			if storage.inDatabase(self):
				c.execute("UPDATE storages "
					  "SET name=?, description=?, flags=?, "
					  "createTimeStamp=?, "
					  "modifyTimeStamp=?, "
					  "stockItem=?, location=?, "
					  "quantity=? "
					  "WHERE id=?;",
					  (toBase64(storage.name),
					   toBase64(storage.description),
					   int(storage.flags),
					   int(storage.createTimeStamp.getStampInt()),
					   int(storage.modifyTimeStamp.getStampInt()),
					   int(storage.stockItem),
					   int(storage.location),
					   int(storage.quantity),
					   int(storage.id)))
			else:
				c.execute("INSERT INTO "
					  "storages(name, description, flags, "
					  "createTimeStamp, "
					  "modifyTimeStamp, "
					  "stockItem, location, quantity) "
					  "VALUES(?,?,?,?,?,?,?,?);",
					  (toBase64(storage.name),
					   toBase64(storage.description),
					   int(storage.flags),
					   int(storage.createTimeStamp.getStampInt()),
					   int(storage.modifyTimeStamp.getStampInt()),
					   int(storage.stockItem),
					   int(storage.location),
					   int(storage.quantity)))
				storage.id = c.lastrowid
				storage.db = self
			self.scheduleCommit()
			return storage.id
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)

	def delStorage(self, storage):
		id = Entity.toId(storage)
		try:
			c = self.db.cursor()
			c.execute("DELETE FROM storages "
				  "WHERE id=?;",
				  (int(id),))
			self.scheduleCommit()
		except (sql.Error, ValueError, TypeError) as e:
			self.__databaseError(e)
