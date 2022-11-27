# -*- coding: utf-8 -*-
#
# PartMgr - Category descriptor
#
# Copyright 2014-2022 Michael Buesch <m@bues.ch>
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

from partmgr.core.entity import *
from partmgr.core.util import *
from partmgr.core.xmlfactory import XmlFactory
from partmgr.core.stockitem import StockItem_XmlFactory

class Category_XmlFactory(XmlFactory):
	def __init__(self, **kwargs):
		self.entity = None
		self.__childCategoriesParser = None
		self.__childStockItemsParser = None
		super().__init__(**kwargs)

	def parser_open(self, tag=None, parentFactory=None):
		super().parser_open(tag, parentFactory)
		assert tag is not None and tag.name == "entity"
		assert tag.getAttr("entityType") == "category"
		assert isinstance(self.entity, Category)

		# Parse the Category specific <entity> tag attributes.
		self.entity.parent = tag.getAttrInt("parent")

		# These lists are filled with the parsed child entities.
		self.entity.childCategories = []
		self.entity.childStockItems = []

	def parser_beginTag(self, tag):
		if tag.name == "categories":
			self.__childCategoriesParser = EntityList_XmlFactory()
			self.parser_switchTo(self.__childCategoriesParser)
			return
		if tag.name == "stockitems":
			self.__childStockItemsParser = EntityList_XmlFactory()
			self.parser_switchTo(self.__childStockItemsParser)
			return
		super().parser_beginTag(tag)

	def parser_endTag(self, tag):
		if tag.name == "entity":
			# The whole category has been parsed.
			# Fetch the parsed child entities.
			if self.__childCategoriesParser is not None:
				self.entity.childCategories =\
					self.__childCategoriesParser.entities
			if self.__childStockItemsParser is not None:
				self.entity.childStockItems =\
					self.__childStockItemsParser.entities
			self.parser_finish()
			return
		super().parser_endTag(tag)

	def composer_getTags(self):
		category = self.entity
		tags = Entity_XmlFactory(entity=category).composer_getTags()
		assert len(tags) == 1

		tags[0].attrs["parent"] = str(category.parent)

		subTags = []

		childCategories = category.getChildCategories()
		if childCategories:
			catSubTags = []
			for childCat in childCategories:
				catSubTags.extend(
					Category_XmlFactory(
						entity=childCat).composer_getTags())
			subTags.append(self.Tag(
				name="categories",
				tags=catSubTags,
			))

		childStockItems = category.getChildStockItems()
		if childStockItems:
			stockSubTags = []
			for childStock in childStockItems:
				stockSubTags.extend(
					StockItem_XmlFactory(
						entity=childStock).composer_getTags())
			subTags.append(self.Tag(
				name="stockitems",
				tags=stockSubTags,
			))

		tags[0].tags = subTags
		return tags

class Category(Entity):
	"Category descriptor."

	XmlFactory = Category_XmlFactory

	def __init__(self, name,
		     parent=None,
		     **kwds):
		Entity.__init__(self,
				name = name,
				entityType = "Category",
				**kwds)
		self.parent = Entity.toId(parent)

	def syncDatabase(self):
		if self.db:
			self.db.modifyCategory(self)

	def getParent(self):
		if not Entity.isValidId(self.parent):
			return None
		return self.db.getCategory(self.parent)

	def setParent(self, parentCategory):
		self.parent = Entity.toId(parentCategory)
		self.syncDatabase()

	def getChildCategories(self):
		return self.db.getChildCategories(self)

	def countChildCategories(self):
		return self.db.countChildCategories(self)

	def getChildStockItems(self):
		return self.db.getStockItemsByCategory(self)

	def countChildStockItems(self):
		return self.db.countStockItemsByCategory(self)

	def delete(self):
		self.db.delCategory(self)
		Entity.delete(self)

	def __eq__(self, other):
		return Entity.__eq__(self, other) and\
		       self.parent == other.parent

	def __hash__(self):
		return (super().__hash__() ^
			hash(self.parent))

	def __repr__(self):
		args = []
		args.append(str(self.name))
		args.append(str(self.description))
		args.append(str(self.flags))
		args.append(str(self.parent))
		args.append(str(self.id))
		args.append(str(self.db))
		return "Category(" + ", ".join(args) + ")"
