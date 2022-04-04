from odoo import fields, models

class EstatePropertyType(models.Model):
    # private attribute
    _name = "estate.property.tags"
    _description = "Real Estate Property Tag"
    _order = "name"
    _sql_constraints = [  #secu sql
        ("check_name", "UNIQUE(name)", "Ce nom doit être unique"),
    ]

    # fields basic
    name = fields.Char("Name", required=True)
    color = fields.Integer("Color")   #stock la couleur du tags garce au widget

