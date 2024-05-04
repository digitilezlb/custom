from odoo import http, fields
from odoo.http import request
from odoo.http import Response
import json
from datetime import datetime, timedelta
import pytz
from odoo.addons.das_publicfunction.controller.main import ProductInfo


class TimeSlot(http.Controller):

    def format_time_from_float(self, float_time):
        # hours = int(float_time)
        # minutes = round((float_time - hours) * 60)
        # seconds = round(((float_time - hours) * 60 - minutes) * 60)
        # formatted_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        # return formatted_time
        hours = int(float_time)
        minutes = round((float_time - hours) * 60)
        formatted_time = "{:02d}:{:02d}".format(hours, minutes)
        return formatted_time

    @http.route('/api/time-slot-http', type='http', auth='public', methods=['Get'], cors="*")
    def get_time_slot(self):
        # delivery_time in hours

        try:
            company_id = int(request.params.get('company_id'))
        except:
            company_id = -1

        calendar = request.env['resource.calendar'].sudo().search(
            [('company_id', '=', company_id), ('is_working_day', '=', True), ('active', '=', True)])

        try:
            dayofweek = int(request.params.get('dayofweek'))
        except:
            dayofweek = 0
        try:
            is_tomorrow_str = request.params.get('is_tomorrow')
            if (is_tomorrow_str =='0' or is_tomorrow_str == 'False' or is_tomorrow_str == 'false' or is_tomorrow_str == '') :
                is_tomorrow =False
            else:
                is_tomorrow = True
        except:
            is_tomorrow = False

        # try:
        #     list_products = request.params.get('list_products')
        # except:
        #     list_products = []

        try:
            # Assuming 'list_products' is a comma-separated string like "product1,product2,product3"
            list_products_str = request.params.get('list_products', '')
            list_products = list_products_str.split(',')
        except Exception as e:
            # Handle the exception appropriately (e.g., log the error)

            list_products = []

        try:
            is_delivery = bool(request.params.get('is_delivery'))
        except:
            is_delivery = False


        now_utc = datetime.now(pytz.UTC)

        current_time = now_utc.astimezone(ProductInfo.beirut_timezone)

        time_str = current_time.strftime('%H:%M')
        
        if is_delivery:
            delivery_time = 30 / 60
            detail = ProductInfo()
            # try:
    
            zone_id = req.get('zone_id')
    
            delivery_time = detail.get_delivery_time(company_id, zone_id)
            delivery_time = delivery_time / 60
        else:
            delivery_time = 0
        # except:
        #     pass

        decimal_time = self.time_to_decimal(time_str)

        if dayofweek > 6:
            Response.status = '404'
            response = {'status': 404, 'message': 'No Time Slot!'}
            return response

        if is_tomorrow:
            dayofweek = dayofweek + 1 if dayofweek <= 5 else 0
        company_schedule_time = []
        company_full_schedule_time = []

        if calendar:
            calendar_attendance = request.env['resource.calendar.attendance'].sudo().search(
                [('calendar_id', '=', calendar[0].id), ('dayofweek', '=', str(dayofweek))], order='hour_from ASC')

            order_ok = False
            
            for cal in calendar_attendance:

                if decimal_time <= cal.hour_to:
                    order_ok = True
                    break

            if order_ok == False:
                Response.status = '404'
                response = {'status': 404,
                            'schedule_time': [],
                           'estimated_time':"" ,
                            'message': 'Order out of time!'}
                return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])

            list_products_int=[]
            for the_id_str in list_products:
                the_id = int(the_id_str)
                list_products_int.append(the_id)

            max_preparation_time = self.get_max_preparation_time(list_products_int)

            from_time = decimal_time + max_preparation_time + delivery_time

            estimated_time = False
            if calendar_attendance:
                _index = 0
                for att in calendar_attendance:
                    _index = _index + 1

                    if is_tomorrow == False:

                        if from_time<=att.hour_from:

                            from_time = att.hour_from + max_preparation_time + delivery_time
                            integer_part = int(from_time)
                            decimal_part = from_time - integer_part
                            if estimated_time==False:
                                estimated_time = str(self.format_time_from_float(from_time))

                            if decimal_part > 0.5:
                                from_time = integer_part + 1
                            elif decimal_part > 0 and decimal_part < 0.5:
                                from_time = integer_part + 0.5
                            company_schedule_time.append(
                                self.create_time_slots(str(self.format_time_from_float(from_time)),
                                                       str(self.format_time_from_float(
                                                           att.hour_to)), 30))
                            continue
                        elif (from_time > att.hour_from and from_time <= att.hour_to):

                            if decimal_time <= att.hour_from:
                                from_time = att.hour_from + max_preparation_time + delivery_time
                            integer_part = int(from_time)
                            decimal_part = from_time - integer_part
                            initial_from_time = from_time

                            if estimated_time == False:
                                estimated_time = str(self.format_time_from_float(from_time))


                            if decimal_part > 0.5:
                                from_time = integer_part + 1
                            elif decimal_part > 0 and decimal_part < 0.5:
                                from_time = integer_part + 0.5

                            if from_time>att.hour_to:
                                from_time = initial_from_time

                            if from_time != initial_from_time:
                                company_schedule_time.append(
                                    self.create_time_slots(str(self.format_time_from_float(from_time)),
                                                           str(self.format_time_from_float(
                                                               att.hour_to)), 30))
                            continue
                        else:

                            if from_time > att.hour_to:

                                if decimal_time <= att.hour_to:

                                    company_schedule_time.append(
                                        self.create_time_slots(str(self.format_time_from_float(from_time)),
                                                               str(self.format_time_from_float(att.hour_to)), 30,True,str(self.format_time_from_float(from_time))))

                                    if estimated_time == False:
                                        estimated_time = str(self.format_time_from_float(from_time))
                                    continue

                                else:

                                    continue

                    else:
                        from_time = att.hour_from + delivery_time + max_preparation_time
                        integer_part = int(from_time)
                        decimal_part = from_time - integer_part

                        if estimated_time == False:
                            estimated_time = str(self.format_time_from_float(from_time))
                        if decimal_part > 0.5:
                            from_time = integer_part + 1
                        elif decimal_part > 0 and decimal_part < 0.5:
                            from_time = integer_part + 0.5
                        company_schedule_time.append(self.create_time_slots(str(self.format_time_from_float(from_time)),
                                                                            str(self.format_time_from_float(
                                                                                att.hour_to)), 30))

                        continue

            for sch in company_schedule_time:

                for item in sch:
                    company_full_schedule_time.append(item)

            values = {
                'schedule_time': company_full_schedule_time,
                'estimated_time':estimated_time
            }

            Response.status = '200'
            response = {'status': 200, 'response': values, 'message': 'Success'}
            return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])

        else:
            Response.status = '404'
            response = {'status': 404, 'message': 'No TIme Slot!'}
            return Response(json.dumps(response), content_type='application/json;charset=utf-8', status=response['status'])


    def time_to_decimal(self, time_str):
        # hours, minutes, seconds = map(int, time_str.split(':'))
        # decimal_time = hours + (minutes / 60) + (seconds / 3600)
        # return decimal_time

        hours, minutes = map(int, time_str.split(':'))
        decimal_time = hours + (minutes / 60)
        return decimal_time

    def get_max_preparation_time(self, list_products):
        products = request.env['product.product'].sudo().search([('id', 'in', list_products)])
        max_preparation_time = 0
        if products:
            for product in products:
                if product.preparing_time:
                    if max_preparation_time < int(product.preparing_time):
                        max_preparation_time = int(product.preparing_time)
        max_preparation_time = max_preparation_time / 60

        return max_preparation_time

    def create_time_slots(self, opening_time, closing_time, slot_duration_minutes,as_soon_as_possible=None,soon_possible_time=None):


        opening_time = datetime.strptime(opening_time, "%H:%M")
        closing_time = datetime.strptime(closing_time, "%H:%M")
        # Initialize a list to store time slots
        time_slots = []

        current_time = opening_time

        # Define the time duration for each slot
        slot_duration = timedelta(minutes=slot_duration_minutes)
        if as_soon_as_possible:
            values = {

                # "from": current_time.strftime("%H:%M:%S"),
                # "to": to_time.strftime("%H:%M:%S")
                "from": soon_possible_time,
                "to": soon_possible_time
            }
            time_slots.append(values)
            return time_slots

        if current_time == closing_time:
            values = {

                # "from": current_time.strftime("%H:%M:%S"),
                # "to": to_time.strftime("%H:%M:%S")
                "from": closing_time.strftime("%H:%M"),
                "to": closing_time.strftime("%H:%M")
            }
            time_slots.append(values)
            return time_slots


        while current_time < closing_time:

            to_time = current_time
            to_time += slot_duration
            if to_time > closing_time:
                to_time = closing_time
            values = {

                # "from": current_time.strftime("%H:%M:%S"),
                # "to": to_time.strftime("%H:%M:%S")
                "from": current_time.strftime("%H:%M"),
                "to": to_time.strftime("%H:%M")
            }
            time_slots.append(values)
            current_time += slot_duration

        return time_slots
