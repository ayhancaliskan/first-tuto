from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    # private attribute
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"  #décroissant
    _sql_constraints = [        #secu sql
        ('check_price', 'CHECK(price >= 0)', "Le prix de l'offre doit être positif"),
    ]

    # fields basic
    price = fields.Float("Price", required=True)

    # special
    state = fields.Selection(
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        string="Status",
        copy=False,
        default=False,
    )

    # relation
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True, ondelete="cascade")

    # Computed
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    # button/logique STAT:
        # se modifie automatiquement quand une type_id sera ajouté à notre estate (via le related)
    property_type_id = fields.Many2one(
        "estate.property.type", related="property_id.property_type_id", string="Property Type", store=True
    )


    # ---------------------------------------- Compute methods ------------------------------------
    # date et validation à faire  -> chapitre 9
    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.date_deadline = date + relativedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.validity = (offer.date_deadline - date).days
    # ------------------------------------------ CRUD Methods -------------------------------------
    # au moment de la creation
    @api.model
    def create(self, vals):
        print(vals)
        # if self.price < vals["price"]:
                            # methode search avec un DOMAIN pour filter
        result = self.search([ ("property_id", "=", vals.get('property_id') ) ])
        for record in result:
            if vals.get('price') < record.price:
                raise UserError('no')
                                    # convert l'id (le nombre) en object reel
        self.env['estate.property'].browse(vals['property_id']).state = "offer_received"
        return super().create(vals)

    # ---------------------------------------- Action Methods -------------------------------------
    def action_accept(self):
        if "accepted" in self.mapped("property_id.offer_ids.state"):
            raise UserError("Une offre a déjà été acceptée.")
        self.write(
            {
                "state": "accepted",
            }
        )
        return self.mapped("property_id").write(
            {
                "state": "offer_accepted",
                "selling_price": self.price,
                "buyer_id": self.partner_id.id,
            }
        )

    def action_refuse(self):
        self.write(
            {
                "state": "refused",
            }
        )
        return self.mapped("property_id").write(
            {
                "state": "new",
                "selling_price": 0,
                "buyer_id": False
            }
        )

