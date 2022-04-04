from odoo import api, models, fields
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class EstateProperty(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------
    _name = 'estate.property'
    _description = 'Real Estate Property'
    _order = "id desc"   #croissant
    # SQL securité
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >= 0)','Le prix attendu doit être positif'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'Le prix de vente doit être positif'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------
    # METHODE DEFAUT
    def _date_availability(self):
        # return fields.Date.context_today(self) + relativedelta(months=3)
        return fields.Date.add(fields.Date.today()+relativedelta(months=+3))

    # Champs Basic
    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Available From", copy=False, default=lambda self: self._date_availability())
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", copy=False, readonly=True)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[
            ("N", "North"),
            ("S", "South"),
            ("E", "East"),
            ("W", "West"),
        ],
        string="Garden Orientation",
    )

    # Champs réservés
    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        string="Status",
        required=True,
        copy=False,
        default="new",
    )

    # Champs relations
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    user_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string="Buyer", readonly=True, copy=False)
    tag_ids = fields.Many2many("estate.property.tags", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    # Champs computed (calculer par une méthod comptude)
    total_area = fields.Integer(
        string="Total area (sqm)",
        compute="_compute_total_area",
    )
    best_price = fields.Float("Best Offer", compute="_compute_best_price", help="Best offer received")

    # ---------------------------------------- Compute methods ------------------------------------
    # attend un changement dans les depends pour mettre à jour ce qu'on demande
    @api.depends("living_area", 'garden_area')
    def _compute_total_area(self):
        for prop in self:
            prop.total_area = prop.living_area + prop.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for prop in self:
            prop.best_price = max(prop.offer_ids.mapped("price")) if prop.offer_ids else 0.0

    # ----------------------------------- Onchanges & constrains(secu pyhton) --------------------------------
    # se passe uniquement sur l'interface de l'utilisateur
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "N"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    @api.constrains("selling_price")   #(les champs impliqué dans la sécu)
    def _check_price_difference(self):
        for record in self:
            if record.selling_price:
                pourcent = (90 * record.expected_price / 100)
                if record.selling_price < pourcent:
                    raise ValidationError("Le prix de vente doit être au moins égal à 90 % du prix attendu ")


    # ---------------------------------------- Action Methods -------------------------------------
    # se lance par des btn via l'interface de l'utilisateur
    def action_sold(self):
        if "canceled" in self.mapped("state"):
            raise UserError("Les propriétés annulées ne peuvent pas être vendues.")
        self.state = "sold"
        return True
        # return self.write({"state": "sold"})

    def action_cancel(self):
        if "sold" in self.mapped("state"):
            raise UserError("Les propriétés vendues ne peuvent pas être annulées.")
        self.state = "canceled"
        return True
        # return self.write({"state": "canceled"})