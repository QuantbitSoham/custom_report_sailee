# Copyright (c) 2023, Vivek.kumbhar@erpdata.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
# import pandas as pd
from itertools import groupby
import csv
# from frappe.utils.xlsxutils import make_xlsx
# from frappe.utils.csvutils import get_csv

class WhattoOrdersReportforMFG(Document):
	@frappe.whitelist()
	def get_report(self):
		if self.sales_order and (not self.production_plan):
			
			sales_order_data_list = [d.sales_order for d in self.sales_order]
			sales_order_parent_list = set()
			
			production_plan_sales_order = doc=frappe.get_all('Production Plan Sales Order',filters={"sales_order": ['in',sales_order_data_list], "docstatus": 1},fields=['parent'])
			if production_plan_sales_order:
				for vsk in production_plan_sales_order:
					sales_order_parent_list.add(str(vsk.parent))
				sales_order_parent_list = list(sales_order_parent_list)
			else:
				frappe.throw(f'There is not any Production plane against {sales_order_data_list} sales order ')

			# frappe.throw(str(sales_order_parent_list))
			variable_for_names_in_sales_order_parent_list = sales_order_parent_list


			
			all_bom_in_production_plane = frappe.get_all('Production Plan Item',filters={"parent": ["in",sales_order_parent_list], "docstatus": 1},fields=['bom_no'])
			list_bom_in_production_plane = sorted(set(item['bom_no'] for item in all_bom_in_production_plane))
			all_bom_exploded_items_filter =  {'parent': ['in',list_bom_in_production_plane] ,"docstatus": 1}
   
			all_bom_exploded_items =frappe.get_all('BOM Explosion Item',filters= all_bom_exploded_items_filter,fields=['item_code','parent'] )  
			total_items = {}
			for item in all_bom_exploded_items:
				item_code = item['item_code']
				parent = item['parent']
				if item_code in total_items:
					total_items[item_code]['parent'].append(parent)
				else:
					total_items[item_code] = {'parent': [parent] }

			bom_exploded_items = [{'item_code': item_code, 'parent': values['parent']} for item_code, values in total_items.items()]

			for row in bom_exploded_items:
				variable_for_names_in_gogogog=[]
				xoxoxo = frappe.get_all("Production Plan Item", filters={"bom_no": ["in", row['parent']],"docstatus": 1}, fields=['parent'],distinct="parent")
				if (not self.production_plan) and (not variable_for_names_in_sales_order_parent_list):
					
					filtered_plans =[]
					for plan in xoxoxo:
						filtered_plans.append(plan.parent)
					gogogog = frappe.get_all("Production Plan", filters={"name": ["in", filtered_plans],'status' : ["not in", ['Closed','Cancelled','Completed','Draft']],"docstatus": 1}, fields=['name'])
					variable_for_names_in_gogogog = list(set(item['name'] for item in gogogog))

				variable_for_names_of_production_plane = variable_for_names_in_sales_order_parent_list if variable_for_names_in_sales_order_parent_list else variable_for_names_in_gogogog

				production_plane_names = ([str(self.production_plan )]) if self.production_plan else variable_for_names_of_production_plane
				
				unique_valuex = set(frappe.get_value("Production Plan", x.parent, "for_warehouse") for x in xoxoxo if frappe.get_value("Production Plan", x.parent, "for_warehouse") is not None)
				if production_plane_names:
					stock_qty=0
					total_material_to_request=0
					total_materialrequestedqty =0
					total_materialorderedqty =0
					total_materialreceivedqty=0
					material_request_list =[]
					production_plane_list = production_plane_names
					

					bom_for_each_pp = frappe.get_all("Production Plan Item", filters={"parent": ['in',production_plane_list],"docstatus": 1}, fields=['bom_no','planned_qty'] )
					for vd in bom_for_each_pp:
						items_req_qty = frappe.get_all("BOM Explosion Item", filters={"parent": vd.bom_no , 'item_code': row['item_code']  }, fields=['stock_qty'] )
						for vk in items_req_qty:
							stock_qty += round((vk.stock_qty * vd.planned_qty),2)


					material_request_plan_item =frappe.get_all("Material Request Plan Item",filters={"parent": ['in',production_plane_list] ,"docstatus": 1, 'item_code' : row['item_code']},fields=['quantity'])
					if 	material_request_plan_item:
						total_material_to_request = sum(dp['quantity'] for dp in material_request_plan_item)

					material_request_item = frappe.get_all("Material Request Item",filters={"production_plan": ['in',production_plane_list] ,"docstatus": 1, 'item_code' : row['item_code']},fields=['qty','parent'])
					if 	material_request_item:
						total_materialrequestedqty = sum(dk['qty'] for dk in material_request_item)
						material_request_list = list(set(dm['parent'] for dm in material_request_item))

						purchase_order_item = frappe.get_all("Purchase Order Item",filters={"material_request": ['in',material_request_list] ,"docstatus": 1, 'item_code' : row['item_code']},fields=['qty'])
						if 	purchase_order_item:
								total_materialorderedqty = sum(pk['qty'] for pk in purchase_order_item)


						purchase_receipt_item = frappe.get_all("Purchase Receipt Item",filters={"material_request": ['in',material_request_list] ,"docstatus": 1, 'item_code' : row['item_code']},fields=['qty'])
						if 	purchase_receipt_item:
								total_materialreceivedqty = sum(rc['qty'] for rc in purchase_receipt_item)


							
						
					sana = (total_material_to_request -total_materialrequestedqty)
					vivek = (total_material_to_request - total_materialorderedqty)
					tejal = (total_materialorderedqty - total_materialreceivedqty)
					if sana != 0 and  vivek != 0 and  tejal != 0:
						self.append("table", {
							"itemcode": row['item_code'],
							"itemname": frappe.get_value("Item",row['item_code'],'item_name'),
							"item_brand":frappe.get_value("Item",row['item_code'],'brand'),
							"requiredbomqty" : stock_qty,
							"actualqty": qty ,
							"productionplan": str(result_list),
							"prodplanwarehouse": str(unique_valuex),
							"material_to_request" : sana,
							"materialrequestedqty" : total_materialrequestedqty,
							"materialorderedqty" : total_materialorderedqty,
							"materialreceivedqty" : total_materialreceivedqty ,
							"material_ordered_but_pending_to_receive_qty": tejal,
							"material_to_order" : vivek,
							"material_request_list" : str(material_request_list)
						})

   
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
		if self.production_plan and (not self.sales_order) :
			

			doc=frappe.get_all('Production Plan Sales Order',filters={"parent": self.production_plan, "docstatus": 1},fields=['sales_order'])
			for d in doc:
				self.append('sales_order', {'sales_order': d.sales_order})

			all_bom_in_production_plane = frappe.get_all('Production Plan Item',filters={"parent": self.production_plan, "docstatus": 1},fields=['bom_no'])
			list_bom_in_production_plane = sorted(set(item['bom_no'] for item in all_bom_in_production_plane))
			all_bom_exploded_items_filter =  {'parent': ['in',list_bom_in_production_plane] ,"docstatus": 1}
   
   
			all_bom_exploded_items =frappe.get_all('BOM Explosion Item',filters= all_bom_exploded_items_filter,fields=['item_code','parent'] )  
			total_items = {}
			for item in all_bom_exploded_items:
				item_code = item['item_code']
				parent = item['parent']
				if item_code in total_items:
					total_items[item_code]['parent'].append(parent)
				else:
					total_items[item_code] = {'parent': [parent] }

			bom_exploded_items = [{'item_code': item_code, 'parent': values['parent']} for item_code, values in total_items.items()]

			for row in bom_exploded_items:
				variable_for_names_in_gogogog=[]
				xoxoxo = frappe.get_all("Production Plan Item", filters={"bom_no": ["in", row['parent']],"docstatus": 1}, fields=['parent'],distinct="parent")
				if (not self.production_plan):
					
					filtered_plans =[]
					for plan in xoxoxo:
						filtered_plans.append(plan.parent)
					gogogog = frappe.get_all("Production Plan", filters={"name": ["in", filtered_plans],'status' : ["not in", ['Closed','Cancelled','Completed','Draft']],"docstatus": 1}, fields=['name'])
					variable_for_names_in_gogogog = list(set(item['name'] for item in gogogog))

				variable_for_names_of_production_plane = variable_for_names_in_gogogog

				production_plane_names = ([str(self.production_plan )]) if self.production_plan else variable_for_names_of_production_plane
				
				unique_valuex = set(frappe.get_value("Production Plan", x.parent, "for_warehouse") for x in xoxoxo if frappe.get_value("Production Plan", x.parent, "for_warehouse") is not None)
				if production_plane_names:
					stock_qty=0
					total_material_to_request=0
					total_materialrequestedqty =0
					total_materialorderedqty =0
					total_materialreceivedqty=0
					material_request_list =[]
					production_plane_list = production_plane_names
					

					bom_for_each_pp = frappe.get_all("Production Plan Item", filters={"parent": ['in',production_plane_list]}, fields=['bom_no','planned_qty'] )
					for vd in bom_for_each_pp:
						items_req_qty = frappe.get_all("BOM Explosion Item", filters={"parent": vd.bom_no , 'item_code': row['item_code']  }, fields=['stock_qty'] )
						for vk in items_req_qty:
							stock_qty += round((vk.stock_qty * vd.planned_qty),2)


					material_request_plan_item =frappe.get_all("Material Request Plan Item",filters={"parent": ['in',production_plane_list] ,"docstatus": 1, 'item_code' : row['item_code']},fields=['quantity'])
					if 	material_request_plan_item:
						total_material_to_request = sum(dp['quantity'] for dp in material_request_plan_item)

					material_request_item = frappe.get_all("Material Request Item",filters={"production_plan": ['in',production_plane_list] ,"docstatus": 1, 'item_code' : row['item_code']},fields=['qty','parent'])
					if 	material_request_item:
						total_materialrequestedqty = sum(dk['qty'] for dk in material_request_item)
						material_request_list = list(set(dm['parent'] for dm in material_request_item))

						purchase_order_item = frappe.get_all("Purchase Order Item",filters={"material_request": ['in',material_request_list] ,"docstatus": 1, 'item_code' : row['item_code']},fields=['qty'])
						if 	purchase_order_item:
								total_materialorderedqty = sum(pk['qty'] for pk in purchase_order_item)


						purchase_receipt_item = frappe.get_all("Purchase Receipt Item",filters={"material_request": ['in',material_request_list] ,"docstatus": 1, 'item_code' : row['item_code']},fields=['qty'])
						if 	purchase_receipt_item:
								total_materialreceivedqty = sum(rc['qty'] for rc in purchase_receipt_item)


							
						
					sana = (total_material_to_request -total_materialrequestedqty)
					vivek = (total_material_to_request - total_materialorderedqty)
					tejal = (total_materialorderedqty - total_materialreceivedqty)
					if sana != 0 and  vivek != 0 and  tejal != 0:
						self.append("table", {
							"itemcode": row['item_code'],
							"itemname": frappe.get_value("Item",row['item_code'],'item_name'),
							"item_brand":frappe.get_value("Item",row['item_code'],'brand'),
							"requiredbomqty" : stock_qty,
							"actualqty": qty ,
							"productionplan": str(result_list),
							"prodplanwarehouse": str(unique_valuex),
							"material_to_request" : sana,
							"materialrequestedqty" : total_materialrequestedqty,
							"materialorderedqty" : total_materialorderedqty,
							"materialreceivedqty" : total_materialreceivedqty ,
							"material_ordered_but_pending_to_receive_qty": tejal,
							"material_to_order" : vivek,
							"material_request_list" : str(material_request_list)
						})

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
			# variable_for_names_in_sales_order_parent_list=None
		if (not self.production_plan) and (not self.sales_order):
			bom_exploded_items = frappe.get_all(
				'BOM Explosion Item',
				filters={'docstatus': 1},
				fields=['item_code', 'GROUP_CONCAT(parent) AS parent'],
				group_by='item_code',
				order_by='item_code',
				distinct="item_code",
				)
			for item in bom_exploded_items:
				item['parent'] = item['parent'].split(',')	
			for row in bom_exploded_items:
				placeholders =', '.join(['%s'] * len(row.parent))
				sql_query_filtered=f"""
					SELECT  distinct t1.name
					FROM `tabProduction Plan` t1
					LEFT JOIN `tabProduction Plan Item` t2 ON t1.name = t2.parent
					WHERE t1.docstatus = 1
					AND t1.status NOT IN ('Closed', 'Cancelled', 'Completed', 'Draft')
					AND t2.bom_no IN ({placeholders})
					"""
				filtered_pp_list = frappe.db.sql(sql_query_filtered,tuple(row.parent), as_dict=True)
				result_list=[]
				result_list.extend([record['name'] for record in filtered_pp_list])
				if result_list:
					stock_qty=0
					total_material_to_request=0
					total_materialrequestedqty =0
					total_materialorderedqty =0
					total_materialreceivedqty=0
					material_request_list =[]
					production_plane_list = result_list
					

					bom_for_each_pp = frappe.get_all("Production Plan Item", filters={"parent": ['in',production_plane_list]}, fields=['bom_no','planned_qty'] )
					for vd in bom_for_each_pp:
						items_req_qty = frappe.get_all("BOM Explosion Item", filters={"parent": vd.bom_no , 'item_code': row['item_code']  }, fields=['stock_qty'] )
						for vk in items_req_qty:
							stock_qty += round((vk.stock_qty * vd.planned_qty),2)


					material_request_plan_item =frappe.get_all("Material Request Plan Item",filters={"parent": ['in',production_plane_list] ,"docstatus": 1, 'item_code' : row['item_code']},fields=['quantity'])
					if 	material_request_plan_item:
						total_material_to_request = sum(dp['quantity'] for dp in material_request_plan_item)

					material_request_item = frappe.get_all("Material Request Item",filters={"production_plan": ['in',production_plane_list] ,"docstatus": 1, 'item_code' : row['item_code']},fields=['qty','parent'])
					if 	material_request_item:
						total_materialrequestedqty = sum(dk['qty'] for dk in material_request_item)
						material_request_list = list(set(dm['parent'] for dm in material_request_item))

						purchase_order_item = frappe.get_all("Purchase Order Item",filters={"material_request": ['in',material_request_list] ,"docstatus": 1, 'item_code' : row['item_code']},fields=['qty'])
						if 	purchase_order_item:
								total_materialorderedqty = sum(pk['qty'] for pk in purchase_order_item)


						purchase_receipt_item = frappe.get_all("Purchase Receipt Item",filters={"material_request": ['in',material_request_list] ,"docstatus": 1, 'item_code' : row['item_code']},fields=['qty'])
						if 	purchase_receipt_item:
								total_materialreceivedqty = sum(rc['qty'] for rc in purchase_receipt_item)
					risk = frappe.get_all('Bin', filters={'item_code': row['item_code'], 'warehouse': 'Store-MFG - SEP'}, fields=['actual_qty'])
					if risk:
						qty = (frappe.get_all('Bin', filters={'item_code': row['item_code'], 'warehouse': 'Store-MFG - SEP'}, fields=['actual_qty']))[0]['actual_qty']

					unique_valuex = set(frappe.get_value("Production Plan", str(x), "for_warehouse") for x in result_list if frappe.get_value("Production Plan", str(x), "for_warehouse") is not None)

					sana = (total_material_to_request -total_materialrequestedqty)
					vivek = (total_material_to_request - total_materialorderedqty)
					tejal = (total_materialorderedqty - total_materialreceivedqty)
					if sana != 0 and  vivek != 0 and  tejal != 0:
						self.append("table", {
							"itemcode": row['item_code'],
							"itemname": frappe.get_value("Item",row['item_code'],'item_name'),
							"item_brand":frappe.get_value("Item",row['item_code'],'brand'),
							"requiredbomqty" : stock_qty,
							"actualqty": qty ,
							"productionplan": str(result_list),
							"prodplanwarehouse": str(unique_valuex),
							"material_to_request" : sana,
							"materialrequestedqty" : total_materialrequestedqty,
							"materialorderedqty" : total_materialorderedqty,
							"materialreceivedqty" : total_materialreceivedqty ,
							"material_ordered_but_pending_to_receive_qty": tejal,
							"material_to_order" : vivek,
							"material_request_list" : str(material_request_list)
						})

		self.save()

	@frappe.whitelist()
	def download_file(self):
		data = frappe.get_all('Child MRP for Multi Assembly', 	
									filters={'parent': self.name}, 
									fields=['itemcode', 'itemname',"item_brand","requiredbomqty","actualqty","productionplan",
											"prodplanwarehouse","material_to_request","materialrequestedqty","materialorderedqty","materialreceivedqty",
											"material_ordered_but_pending_to_receive_qty","material_to_order",	"material_request_list"])

		file_path = frappe.get_site_path('public', 'files', 'output.csv')
		with open(file_path, 'w', newline='') as csvfile:
			fieldnames = ['itemcode', 'itemname',"item_brand","requiredbomqty","actualqty","productionplan",
											"prodplanwarehouse","material_to_request","materialrequestedqty","materialorderedqty","materialreceivedqty",
											"material_ordered_but_pending_to_receive_qty","material_to_order",	"material_request_list"]  # Replace with your actual field names
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			writer.writeheader()
			for row in data:
				writer.writerow(row)
		return file_path