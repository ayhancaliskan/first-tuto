from odoo import fields, models

class ResUsers(models.Model):

    # ---------------------------------------- Private Attributes ---------------------------------
    #hertige classique d'un model déja existant
    _inherit = "res.users"

    # --------------------------------------- Fields Declaration ----------------------------------

    # Relational
    property_ids = fields.One2many(
        "estate.property", "user_id", string="Properties", domain=[("state", "in", ["new", "offer_received"])]
    )
