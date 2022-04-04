from odoo import models, fields

class EstatePropertyType(models.Model):
    # private attribute
    _name = "estate.property.type"
    _description = "Real Estate Property Type"
    _order = "sequence, name"
    _sql_constraints = [  #secu sql
        ("check_name", "UNIQUE(name)", "Le nom doit être unique"),
    ]
    # field basic
    name = fields.Char("Name", required=True)
    sequence = fields.Integer("Sequence")  #afficher dans la view type pour faire un order manuel pour l'user
    # relation
    property_ids = fields.One2many("estate.property", "property_type_id")


# CHAPITRE 12 TOUT CE QUI SUIT -> LOGIQUE STATISTIQUE SUR LES OFFRES
    # Computed (for stat button)
    offer_ids = fields.Many2many("estate.property.offer", string="Offers", compute="_compute_offer")
    offer_count = fields.Integer(string="Offers Count", compute="_compute_offer")

    # ---------------------------------------- compute -------------------------------------
    # logique pour stocker les offer et un count sur les estates
    def _compute_offer(self):
        data = self.env["estate.property.offer"].read_group(
            [("property_id.state", "!=", "canceled"), ("property_type_id", "!=", False)],
            ["ids:array_agg(id)", "property_type_id"],
            ["property_type_id"],
        )
        print(data)
        mapped_count = {d["property_type_id"][0]: d["property_type_id_count"] for d in data}
        mapped_ids = {d["property_type_id"][0]: d["ids"] for d in data}
        for prop_type in self:
            prop_type.offer_count = mapped_count.get(prop_type.id, 0)
            prop_type.offer_ids = mapped_ids.get(prop_type.id, [])

    # ---------------------------------------- Action Methods -------------------------------------
    # btn de la view type pointe cette méthode
    def action_view_offers(self):
        res = self.env.ref("estate.estate_property_offer_action").read()[0]
        res["domain"] = [("id", "in", self.offer_ids.ids)]
        return res
