// Copyright (c) 2024, Vivek.kumbhar@erpdata.in and contributors
// For license information, please see license.txt
/* eslint-disable */

// frappe.query_reports["What To Order For MFG"] = {
// 	"filters": [

// 	]
// };

// Copyright (c) 2023, Abhishek Chougule and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["What To Order For MFG"] = {
	"filters": [

		{
			"fieldname": "sales_order",
			"fieldtype": "MultiSelectList",
			"label": "Sales Order",
			get_data: function(txt) {
				return frappe.db.get_link_options('Sales Order', txt,);
			}
		},
		{
			"fieldname": "production_plan",
			"fieldtype": "MultiSelectList",
			"label": "Production Plan",
			get_data: function(txt) {
				return frappe.db.get_link_options('Production Plan', txt,);
			}
		
		},
	

	]
};
