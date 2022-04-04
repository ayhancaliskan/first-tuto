from odoo import http

class Academy(http.Controller):

    @http.route(['/eezee', '/eezee/<name>'], auth='public')
    def index(self, name="", **kw):
        print(kw)
        firstname = kw.get('name', "Ayhan")
        firstname = name
        return f'Hello, world {firstname}'