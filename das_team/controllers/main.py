import json
from odoo import http, _, fields
from odoo.http import request
from odoo.http import Response



class TeamController(http.Controller):

    @http.route('/api/team', type='json', auth='public', methods=['Post'], cors="*")
    def get_team(self):
        x_localization = request.httprequest.headers.get('x-localization')
        lang = "en"
        if x_localization:
            if x_localization == 'ar':
                lang = "ar"
        
        try:
            req = json.loads(request.httprequest.data)
            company_id = req.get('company_id')
        except:
            pass

        if lang == "ar":
            if company_id:
                team = request.env['team'].with_context(lang='ar_001').sudo().search(
                    [('company_id', '=', company_id)],limit=1)
            else:
                team = request.env['team'].with_context(lang='ar_001').sudo().search([],limit=1)
        else:

            if company_id:
                team = request.env['team'].sudo().search([('company_id', '=', company_id)],limit=1)
            else:
                team = request.env['team'].sudo().search([],limit=1)
                
        

        member_list = []

        if team:

            for member in team.team_member:

                if lang == "ar":
                    themember = request.env['res.partner'].with_context(
                            lang='ar_001').sudo().search(
                            [('id', '=', member.id)])
                else:
                    themember = request.env['res.partner'].sudo().search(
                            [('id', '=', member.id)])

                if themember.is_member == True :
                    member_list.append({"member_id": themember.id,
                                     "member_name": themember.name,
                                     "member_image": "/web/content/" + str(themember.team_member_image_attachment.id) if themember.team_member_image_attachment.id else "",
                                     "member_position": themember.position if themember.position else "",
                                     })

            values = {
                    "team_id": team.id,
                    "team_name": team.name,
                    "team_image": "/web/content/" + str(team.team_image_attachment.id) if team.team_image_attachment.id else "",
                    "member_ids": member_list,
                }
            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'List Of Team Found'}
        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No Products Found!'}
        return response
