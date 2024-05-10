# Copyright (c) 2024, Vivek.kumbhar@erpdata.in and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	if not filters: filters={}

	columns, data = [], []

	columns = get_columns()
	data = get_data(filters)

	if not data:
		frappe.msgprint('🙄😵 NO RECORD FOUND 😵🙄')
		return columns, data

	return columns, data


def get_columns():
	return [
     	{
			"fieldname": "sales_order",
			"fieldtype": "data",
			"label": "Sales Order",
			
		},
		{
			"fieldname": "production_plan",
			"fieldtype": "data",
			"label": "Production Plan",
		},
		{
			"fieldname": "item_code",
			"fieldtype": "Link",
			"label": "Item",
			"options": "Item",
		},
		{
			"fieldname": "item_name",
			"fieldtype": "data",
			"label": "Item_name",
		},
		{
			"fieldname": "item_brand",
			"fieldtype": "Link",
			"label": "Item Brand",
			"options": "Brand",
		},
		{
			"fieldname": "required_bom_qty",
			"fieldtype": "float",
			"label": "Required BOM QTY",
		},
		{
			"fieldname": "actual_qty",
			"fieldtype": "float",
			"label": "Actual QTY",
		},
		{
			"fieldname": "prodplan_warehouse",
			"fieldtype": "data",
			"label": "Production Plan Warehouse",
		},
		{
			"fieldname": "material_to_request",
			"fieldtype": "float",
			"label": "Material To Request",
		},
		{
			"fieldname": "material_requested_qty",
			"fieldtype": "float",
			"label": "Material Requested QTY",
		},
		{
			"fieldname": "material_ordered_qty",
			"fieldtype": "float",
			"label": "Material Ordered QTY",
		},
		{
			"fieldname": "material_received_qty",
			"fieldtype": "float",
			"label": "Material Received QTY",
		},
		{
			"fieldname": "pending_to_receive_qty",
			"fieldtype": "float",
			"label": "Material Ordered But Pending To Receive QTY",
		},
		{
			"fieldname": "material_to_order",
			"fieldtype": "float",
			"label": "Material To Order",
		},
		{
			"fieldname": "material_request_list",
			"fieldtype": "data",
			"label": "Material Request List",
		},

	]

def get_data(filters):
	result_list = []
	
	items = get_item_data(filters)
	for i in items:
		production_plane_list = []
		sales_order_list = []
		production_plane_list = filters.get('production_plan')
		sales_order_list = filters.get('sales_order')
		if sales_order_list:
			production_plane_list = get_production_plan_from_sales_order(sales_order_list)
		if not production_plane_list:
			production_plane_list = get_production_plan_from_item_code(str(i.item_code))
		if not sales_order_list:
			sales_order_list = get_sales_order(production_plane_list)
  
		if production_plane_list:
			total_material_to_request = get_total_material_to_request(str(i.item_code) , production_plane_list)
			total_materialrequestedqty , material_request_list = get_total_materialrequestedqty(str(i.item_code) , production_plane_list)
			tmoq , tmrq = 0, 0
			if material_request_list:
				tmoq = get_total_materialorderedqty(str(i.item_code),material_request_list)
				tmrq = get_total_materialreceivedqty(str(i.item_code),material_request_list)
			total_materialorderedqty = tmoq
			total_materialreceivedqty = tmrq
			sana = (total_material_to_request -total_materialrequestedqty)
			vivek = (total_material_to_request - total_materialorderedqty)
			tejal = (total_materialorderedqty - total_materialreceivedqty)

      
			item_dict ={
						'sales_order':i,
						'production_plan': str(production_plane_list),
						'item_code': i.item_code,
						'item_name': frappe.get_value('Item',i.item_code,'item_name'),
						'item_brand': frappe.get_value("Item",i.item_code,'brand'),
						'required_bom_qty':get_required_bom_qty(i.item_code,production_plane_list ),
						'actual_qty': frappe.get_value('Bin',{'item_code': i.item_code , 'warehouse': 'Store-MFG - SEP'}, 'actual_qty'),
						'prodplan_warehouse': get_prodplan_warehouse(production_plane_list) ,
						'material_to_request': sana ,
						'material_requested_qty': total_materialrequestedqty ,
						'material_ordered_qty': total_materialorderedqty,
						'material_received_qty':total_materialreceivedqty ,
						'pending_to_receive_qty':tejal,
						'material_to_order': vivek ,
						'material_request_list':str(material_request_list) ,
						}
			
			result_list.append(item_dict)
	return result_list


def get_item_data(filters):
	sales_order = filters.get('sales_order')
	production_plan = filters.get('production_plan')
	if sales_order and production_plan:
		return  frappe.db.sql("""
							SELECT DISTINCT a.item_code
				 			FROM `tabBOM Explosion Item` a 
							LEFT JOIN `tabProduction Plan Item` b ON a.parent = b.bom_no
							WHERE b.parent  IN {0} AND b.sales_order IN {1} AND b.docstatus = 1
						""".format(tuple(production_plan + ['XXXXX']) ,tuple(sales_order + ['XXXXX'])),as_dict=True)
	elif sales_order and not production_plan:
		return frappe.db.sql("""
							SELECT DISTINCT a.item_code
				 			FROM `tabBOM Explosion Item` a 
							LEFT JOIN `tabProduction Plan Item` b ON a.parent = b.bom_no
							WHERE b.sales_order IN {0} AND b.docstatus = 1
						""".format(tuple(sales_order + ['XXXXX'])), as_dict =True)
	elif not sales_order and production_plan:
		return frappe.db.sql("""
							SELECT DISTINCT a.item_code
				 			FROM `tabBOM Explosion Item` a 
							LEFT JOIN `tabProduction Plan Item` b ON a.parent = b.bom_no
							WHERE b.parent  IN {0}  AND b.docstatus = 1
						""".format(tuple(production_plan + ['XXXXX'])), as_dict =True)
	else:
		return frappe.get_all("BOM Explosion Item", filters = {}, fields = ['item_code'],distinct = 'item_code')
 
 
def get_sales_order(filters):
    pass
def get_production_plan_from_item_code(item_code ):
		production_plan = frappe.db.sql("""
							SELECT DISTINCT b.parent
							FROM `tabProduction Plan` a
							LEFT JOIN `tabMaterial Request Plan Item` b ON a.name = b.parent
							WHERE a.status NOT IN ('Closed', 'Cancelled', 'Completed', 'Draft') AND b.item_code = '{0}'
							""".format(item_code) ,as_dict=True)
		return  [row['parent'] for row in production_plan]

def get_production_plan_from_sales_order(sales_order):
	if sales_order:
		production_plan = frappe.db.sql("""
							SELECT DISTINCT b.parent
							FROM `tabProduction Plan` a
							LEFT JOIN `tabProduction Plan Item` b ON a.name = b.parent
							WHERE a.status NOT IN ('Closed', 'Cancelled', 'Completed', 'Draft') AND b.sales_order IN {0}
							""".format(tuple(sales_order + ['XXXXX'])) ,as_dict=True)
		return  [row['parent'] for row in production_plan]

def get_required_bom_qty(item_code , production_plane_list ):
	required_bom_qty = frappe.db.sql("""
							SELECT SUM(b.stock_qty * a.planned_qty) AS calculated_qty
							FROM `tabProduction Plan Item` a
							LEFT JOIN `tabBOM Explosion Item` b ON a.bom_no = b.parent
							WHERE b.item_code = '{0}' AND a.parent IN {1}
							""".format(item_code , tuple(production_plane_list + ['XXXXX'])) ,as_dict=True)
	return required_bom_qty[0].calculated_qty if required_bom_qty and required_bom_qty[0].calculated_qty else 0




def get_prodplan_warehouse(production_plane_list):
	prodplan_warehouse = frappe.db.sql(""" SELECT a.for_warehouse FROM `tabProduction Plan` a WHERE a.name IN {0}""".format(tuple(production_plane_list + ['XXXXX'])),as_dict=True )
	return str(list(set(row['for_warehouse'] for row in prodplan_warehouse)))


def get_total_material_to_request(item_code ,production_plane_list):
    total_material_to_request = frappe.db.sql(""" SELECT SUM(a.quantity) quantity FROM `tabMaterial Request Plan Item` a 
                                              	  WHERE a.item_code = '{0}' AND a.parent IN {1}""".format(item_code,tuple(production_plane_list + ['XXXXX'])),as_dict=True )
    return total_material_to_request[0].quantity if total_material_to_request and total_material_to_request[0].quantity else 0

def get_total_materialrequestedqty(item_code ,production_plane_list):
	total_materialrequestedqty = frappe.db.sql(""" SELECT b.parent, SUM(b.qty) qty
											FROM `tabMaterial Request` a
											LEFT JOIN `tabMaterial Request Item` b ON a.name = b.parent
											WHERE b.item_code = '{0}' 
											AND b.production_plan IN {1}
											AND (
												(b.ordered_qty > 0 AND a.status IN ('Stopped','Pending','Partially Ordered','Ordered')) OR
												(b.ordered_qty <= 0 AND a.status IN ('Pending','Partially Ordered','Ordered'))
											)
											GROUP BY b.parent """.format(item_code,tuple(production_plane_list + ['XXXXX'])),as_dict=True )
	# frappe.msgprint(str(total_materialrequestedqty))
	# value = total_materialrequestedqty[0].qty if total_materialrequestedqty and total_materialrequestedqty[0].qty else 0

	mr_list = []
	value = 0
	for i in total_materialrequestedqty:
		if i.parent:
			mr_list.append(i.parent)
		if i.qty:
			value = value + i.qty
	return value ,mr_list



def get_total_materialorderedqty(item_code ,mr_list):
    total_materialorderedqty = frappe.db.sql(""" SELECT SUM(b.qty) qty 
												 FROM `tabPurchase Order` a 
             									 LEFT JOIN	`tabPurchase Order Item` b ON a.name = b.parent
                                                 WHERE b.item_code = '{0}' AND b.material_request IN {1} AND a.status IN ('To Bill' , 'To Receive and Bill' , 'Completed')
                                                 """.format(item_code,tuple(mr_list + ['XXXXX'])),as_dict=True )
    value =  total_materialorderedqty[0].qty if total_materialorderedqty and total_materialorderedqty[0].qty else 0
    return value


def get_total_materialreceivedqty(item_code ,mr_list):
    total_materialreceivedqty =   frappe.db.sql(""" SELECT SUM(b.qty) qty 
                                                	FROM `tabPurchase Receipt` a
                                                 	LEFT JOIN `tabPurchase Receipt Item` b ON a.name = b.parent
                                                	WHERE b.item_code = '{0}' AND b.material_request IN {1} AND a.status IN ('To Bill' , 'Completed')
                                                 	""".format(item_code,tuple(mr_list + ['XXXXX'])),as_dict=True )
    value =  total_materialreceivedqty[0].qty if total_materialreceivedqty and total_materialreceivedqty[0].qty else 0
    return value



# SELECT DISTINCT b.parent
# 							FROM `tabProduction Plan` a
# 							LEFT JOIN `tabMaterial Request Plan Item` b ON a.name = b.parent
# 							WHERE a.status NOT IN ('Closed', 'Cancelled', 'Completed', 'Draft') AND b.item_code = '{0}'

    # me = frappe.db.sql("""select milk_entry , status , supplier
	#                     from `tabPurchase Receipt` where docstatus= 1 and supplier = '{0} ' 
    #                  and posting_date BETWEEN '{1}' and '{2}' and per_billed<100 and 
    #                  milk_entry is not null		""".format(i.name,p_inv.previous_sync_date,getdate(n_days_ago)), as_dict =True)
# # Copyright (c) 2023, Abhishek Chougule and contributors
# # For license information, please see license.txt

# import frappe
# import calendar
# from datetime import datetime

# def execute(filters=None):
# 	if not filters: filters={}

# 	columns, data = [], []

# 	columns = get_columns()
# 	data = get_data(filters)

# 	if not data:
# 		frappe.msgprint('🙄😵 NO RECORD FOUND 😵🙄')
# 		return columns, data
# 	return columns, data

# def get_columns():
# 	return [
# 		{
# 			"fieldname": "item_code",
# 			"fieldtype": "Link",
# 			"label": "Item",
# 			"options": "Item",
# 		},
# 		{
# 			"fieldname": "item_name",
# 			"fieldtype": "data",
# 			"label": "Item_name",
# 		},
# 					{
# 						"fieldname": "opening_stock",
# 						"fieldtype": "float",
# 						"label": "Opening Stock",
# 					},
# 					{
# 						"fieldname": "delivery_qty",
# 						"fieldtype": "float",
# 						"label": "Delivered QTY",
# 					},
# 					{
# 						"fieldname": "sales_qty",
# 						"fieldtype": "float",
# 						"label": "Sales Qty",
# 					},
# 					{
# 						"fieldname": "scheduled_qty",
# 						"fieldtype": "float",
# 						"label": "Scheduled Qty",
# 					},
# 					{
# 						"fieldname": "scheduled_percentage",
# 						"fieldtype": "float",
# 						"label": "% Copmiance with Sch",
# 					},
# 		{
# 			"fieldname": "ok_qty",
# 			"fieldtype": "float",
# 			"label": "OK Produced Qty",
# 		},
# 		{
# 			"fieldname": "cr_qty",
# 			"fieldtype": "float",
# 			"label": "CR Qty",
# 		},
# 		{
# 			"fieldname": "cr_per",
# 			"fieldtype": "float",
# 			"label": "CR in %",
# 		},
# 		{
# 			"fieldname": "mr_qty",
# 			"fieldtype": "float",
# 			"label": "MR Qty",
# 		},
# 		{
# 			"fieldname": "mr_per",
# 			"fieldtype": "float",
# 			"label": "MR in %",
# 		},
# 		{
# 			"fieldname": "rw_qty",
# 			"fieldtype": "float",
# 			"label": "RW Qty",
# 		},
# 		{
# 			"fieldname": "rw_per",
# 			"fieldtype": "float",
# 			"label": "RW in %",
# 		},
# 		{
# 			"fieldname": "total_rejection",
# 			"fieldtype": "float",
# 			"label": "Total Rejection",
# 		},
# 		{
# 			"fieldname": "total_qty",
# 			"fieldtype": "float",
# 			"label": "Total Quantity",
# 		},

# 	]


# def get_data(filters):
	
# 	date_filter , company_filter , item_code_filter = get_conditions(filters)
# 	production_filter = {**date_filter , **company_filter}
	

# 	production_list = get_production_list(production_filter)
# 	production_id_filter = {'parent':['in',production_list]}
# 	# frappe.msgprint(str(item_code_filter))
# 	if item_code_filter:
# 		item_list = [item_code_filter['item_code']]
# 	else:
# 		item_list = get_item_list(production_id_filter)


# 	result_list = []

# 	for i in item_list:
# 		item_filter = {"item":i}
# 		qty_details_filter = {**item_filter , **production_id_filter}
# 		qty_details = frappe.get_all ("Qty Details",fields = ['ok_qty','cr_qty','mr_qty','rw_qty','total_qty'],filters = qty_details_filter,)
# 		ok_qty , cr_qty , mr_qty ,rw_qty , total_qty = 0 ,0, 0, 0, 0
# 		for j in qty_details:
# 			ok_qty = ok_qty + j.ok_qty
# 			cr_qty = cr_qty + j.cr_qty
# 			mr_qty = mr_qty + j.mr_qty
# 			rw_qty = rw_qty + j.rw_qty
# 		total_qty = ok_qty + cr_qty + mr_qty + rw_qty
# 		if total_qty != 0:
# 			cr_per = (cr_qty / total_qty) * 100
# 			mr_per = (mr_qty / total_qty) * 100
# 			rw_per = (rw_qty / total_qty) * 100

# 		total_rejection = cr_qty + mr_qty + rw_qty
# 		delivery_qty = get_delivery_qty(i,filters)
# 		scheduled_qty = get_scheduled_qty(i,filters)
# 		sales_qty = get_sales_qty(i,filters)
# 		if scheduled_qty:
# 			scheduled_percentage = round((delivery_qty/scheduled_qty)*100 , 2)
# 		item_dict ={
# 					'item_code':i,
# 					'item_name': frappe.get_value('Item', i ,'item_name'),
# 					'opening_stock': get_all_available_quantity(i),
# 					'delivery_qty': delivery_qty,
# 					'scheduled_qty': scheduled_qty,
# 					'sales_qty':sales_qty,
# 					'scheduled_percentage':scheduled_percentage,
# 					'ok_qty': ok_qty ,
# 					'cr_qty': cr_qty,
# 					'mr_qty': mr_qty ,
# 					'rw_qty': rw_qty,
# 					'cr_per': round(cr_per,2) ,
# 					'mr_per': round(mr_per,2) ,
# 					'rw_per': round(rw_per,2) ,
# 					'total_rejection':total_rejection ,
# 					'total_qty': total_qty,}
		
# 		result_list.append(item_dict)

	
# 	# frappe.msgprint(str(qty_details))
# 	return result_list 

# def get_conditions(filters):
# 	date_filter ={}
# 	company_filter = {}
# 	item_code_filter = {}

# 	from_date ,to_date= get_month_dates(int(filters.get('year')), filters.get('month'))
# 	company = filters.get('company')
# 	item_code =  filters.get('item_code')


# 	if from_date or to_date:
# 		date_filter = {'date': ['between',[ filters.get('from_date', '2001-01-01'), filters.get('to_date', '2100-01-01')]]}

# 	if company :
# 		company_filter = {'company':company}

# 	if item_code :
# 		item_code_filter = {'item_code':item_code}
		
			
# 	return date_filter , company_filter , item_code_filter

# def get_production_list(production_filters):
# 	return_list = []
# 	production = frappe.get_all ("Production",fields = ['name',],filters = production_filters,)
# 	if production:
# 		for p in production:
# 			return_list.append(p.name)

# 	return return_list

# def get_item_list(parent_filter):
# 	return_list = []
# 	items = frappe.get_all("Items Production",fields = ['item',],filters = parent_filter, distinct="item")
# 	if items:
# 		for i in items:
# 			return_list.append(i.item)

# 	return return_list


# def get_all_available_quantity(item_code):
# 	result = frappe.get_all("Bin", filters={"item_code": item_code,}, fields=["actual_qty"])
# 	return sum(r.actual_qty for r in result) if result else 0

# def get_delivery_qty(item_code ,filters):
# 	from_date ,to_date= get_month_dates(int(filters.get('year')), filters.get('month'))
# 	qty = frappe.db.sql("""
# 							SELECT b.item_code, SUM(b.qty) 'qty' 
# 							FROM `tabDelivery Note` a
# 							LEFT JOIN `tabDelivery Note Item` b ON a.name = b.parent
# 							WHERE a.posting_date BETWEEN %s AND %s AND b.item_code = %s AND b.docstatus = 1
# 						""",(from_date ,to_date ,item_code),as_dict="True")

# 	return qty[0].qty if qty[0].qty else 0

# def get_sales_qty(item_code ,filters):
# 	from_date ,to_date= get_month_dates(int(filters.get('year')), filters.get('month'))
# 	qty = frappe.db.sql("""
# 							SELECT b.item_code, SUM(b.qty) 'qty' 
# 							FROM `tabSales Invoice` a
# 							LEFT JOIN `tabSales Invoice Item` b ON a.name = b.parent
# 							WHERE a.posting_date BETWEEN %s AND %s AND b.item_code = %s AND b.docstatus = 1
# 						""",(from_date ,to_date ,item_code),as_dict="True")

# 	return qty[0].qty if qty[0].qty else 0

# def get_month_dates(year, month_name):
# 		month_number = datetime.strptime(month_name, "%B").month
# 		_, last_day = calendar.monthrange(year, month_number)

# 		start_date = datetime(year, month_number, 1)
# 		end_date = datetime(year, month_number, last_day)

# 		return start_date, end_date

# def get_scheduled_qty(item_code,filters):
# 	machining_schedule =  frappe.get_value("Machining Schedule",{'company':filters.get('company'),'month':filters.get('month'),'year':filters.get('year')},"name")
# 	if machining_schedule:
# 		qty =  frappe.get_value("Item Machining Schedule",{'parent':machining_schedule,'item_code':item_code},"schedule_quantity")
# 		return qty if qty else 0
# 	return 0