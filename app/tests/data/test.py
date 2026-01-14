# Payload for execute fnr workflow
{"workflow_id":112,
"conditions":[{"business_name":"payment_amount","operator":">","value":3000},
			  {"business_name":"points_earned","operator":">=","value":900}],
"data_volume":10}

# No data
{"workflow_id":112,
"conditions":[{"business_name":"payment_amount","operator":">","value":7000},
			  {"business_name":"points_earned","operator":">=","value":1800}]
}

# Payload for save fnr log

{
  "workflow_id": "112",
  "created_by": "john009",
  "data_records":[{"selected": false, "customer_id": 1002, "is_reserved": true, "is_selected": true, "customer_name": "Rahul Mehta"}, 
                  {"selected": false, "customer_id": 1022, "is_reserved": true, "is_selected": true, "customer_name": "Rahul Mehta"}]
}

{
  "workflow_id": "112",
  "created_by": "john009",
  "data_records":[{"customer_id": 1001, "is_reserved": true, "is_selected": true, "customer_name": "Alice Johnson"}, 
                  {"customer_id": 1021, "is_reserved": true, "is_selected": true, "customer_name": "Alice Johnson"}]
}