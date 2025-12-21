# Grist Tables Schema

Schema obtained from Grist's "code view" page.

```python
import grist
from functions import *       # global uppercase functions
import datetime, math, re     # modules commonly needed in formulas


@grist.UserTable
class Items:
  ItemID = grist.Text()
  Name = grist.Text()
  Type = grist.Choice()
  Subtype = grist.Choice()

  def _default_isDup(rec, table, value, user):
    return len(Items.lookupRecords(ItemID=rec.ItemID)) > 1
  isDup = grist.Bool()


@grist.UserTable
class Player_Plays:
  Play = grist.Reference('Plays')
  Player = grist.Reference('Players')
  StartPosition = grist.Text()
  Color = grist.Text()
  Score = grist.Int()
  Rating = grist.Int()
  New = grist.Bool()
  Win = grist.Bool()


@grist.UserTable
class Players:
  UserID = grist.Text()
  Username = grist.Text()
  Name = grist.Text()


@grist.UserTable
class Plays:
  PlayID = grist.Text()
  Date = grist.Date()
  Quantity = grist.Int()
  Length_Minutes = grist.Int()
  Location = grist.Text()
  Comment = grist.Text()
  Item = grist.Reference('Items')

  def _default_isDup(rec, table, value, user):
    return len(Plays.lookupRecords(PlayID=rec.PlayID)) > 1
  isDup = grist.Bool()

  class _Summary:

    @grist.formulaType(grist.ReferenceList('Plays'))
    def group(rec, table):
      return table.getSummarySourceGroup(rec)

    @grist.formulaType(grist.Int())
    def count(rec, table):
      return len(rec.group)

    def gristHelper_Display(rec, table):
      return rec.Item.Name

    def Type(rec, table):
      return rec.Item.Subtype

```
