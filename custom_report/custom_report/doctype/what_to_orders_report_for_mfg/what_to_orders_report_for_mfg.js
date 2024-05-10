frappe.ui.form.on('What to Orders Report for MFG', {
    refresh: function(frm) {
        $('.layout-side-section').hide();
        $('.layout-main-section-wrapper').css('margin-left', '0');
    }
});

frappe.ui.form.on('What to Orders Report for MFG', {
	// refresh: function(frm) {

	// }
});


frappe.ui.form.on('What to Orders Report for MFG', {
	
	show_report: function(frm) {

        frm.clear_table("table");
        frm.refresh_field('table');

        if (frm.doc.sales_order && frm.doc.sales_order.length > 0 && frm.doc.production_plan && frm.doc.production_plan.length > 0) {
            frm.clear_table("sales_order");
            frm.refresh_field('sales_order');
        }


		frm.call({
			method: 'get_report',//function name defined in python
			doc: frm.doc, //current document
		});

	}

});



// frappe.ui.form.on("What to Orders Report for MFG", {
//     refresh: function(frm) {
//         frm.fields_dict['sales_order'].get_query = function(doc, cdt, cdn) {
//             return {
//                 filters: [
//                     ["Sales Order", "docstatus", '=', 1]
//                 ]
//             };
//         };
//     }
// });

// frappe.ui.form.on("What to Orders Report for MFG", {
//     refresh: function(frm) {
//             frm.set_query("production_plan", function() { // Replace with the name of the link field
//                 return {
//                     filters: [
//                         ["Production Plan", "status", 'in', ["Submitted", "Material Requested", "In Process"]] // Replace with your actual filter criteria
//                     ]
//                 };localStorage
//             });
//         }
//     });

    frappe.ui.form.on('What to Orders Report for MFG', {
        export_report: function(frm) {
            frappe.call({
                method: 'download_file',
                doc: frm.doc,
                callback: function(r) {
                    if(r.message) {
                        var file_path = "http://192.168.10.21/files/output.csv";
                        window.open(file_path);
                    }
                }
            });
        }
    });
    

    // frappe.ui.form.on('What to Orders Report for MFG', {
    //     export_report: function(frm) {
    //         frappe.call({
    //             method: 'download_file',
    //             doc: frm.doc,
    //             callback: function(r) {
    //                 if(r.message) {
    //                     var file_path = r.message;
    //                     fetch(file_path)
    //                         .then(response => response.blob())
    //                         .then(blob => {
    //                             var link = document.createElement('a');
    //                             link.href = window.URL.createObjectURL(blob);
    //                             link.download = "report.csv";
    //                             document.body.appendChild(link);
    //                             link.click();
    //                             document.body.removeChild(link);
    //                         });
    //                 }
    //             }
    //         });
    //     }
    // });
    

    // frappe.ui.form.on('What to Orders Report for MFG', {
    //     export_report: function(frm) {
    //         frappe.call({
    //             method: 'download_file',
    //             doc: frm.doc,
    //             callback: function(r) {
    //                 if(r.message) {
    //                     var data = r.message;
    //                     var blob = new Blob([data], { type: "csv" });
    //                     var link = document.createElement('a');
    //                     link.href = window.URL.createObjectURL(blob);
    //                     link.download = "report.csv";
    //                     document.body.appendChild(link);
    //                     link.click();
    //                     document.body.removeChild(link);
    //                 }
    //             }
    //         });
    //     }
    // });


    // frappe.ui.form.on('What to Orders Report for MFG', {
    //     export_report(frm) {
    //         frappe.run_serially([
    //             () => {
    //                 // Temporarily bypass permissions
    //                 frm.bypass_doctype_permissions = true;
    //             },
    //             () => {
    //                 // Your export logic here
    //                 frappe.require("data_import_tools.bundle.js", () => {
    //                     frm.data_exporter = new frappe.data_import.DataExporter(
    //                         'Child MRP for Multi Assembly',
    //                         "Insert New Records"
    //                     );
    //                 });
    //             },
    //             () => {
    //                 // Reset bypass permissions flag after export
    //                 frm.bypass_doctype_permissions = false;
    //             }
    //         ]);
    //     },
    // });

    // frappe.ui.form.on('What to Order Report for MFG', {
    //     export_report(frm) {
    //         frappe.run_serially([
    //             () => {
    //                 // Temporarily bypass permissions
    //                 frm.bypass_doctype_permissions = true;
    //             },
    //             () => {
    //                 // Your export logic here
    //                 frappe.require("data_import_tools.bundle.js", () => {
    //                     frm.data_exporter = new frappe.data_import.DataExporter(
    //                         'Child What to Order Report for MFG',
    //                         "Insert New Records"
    //                     );
    //                     frm.data_exporter.run();
    //                 });
    //             },
    //             () => {
    //                 // Reset bypass permissions flag after export
    //                 frm.bypass_doctype_permissions = false; // Change to false to reset
    //             }
    //         ]);
    //     },
    // });
    