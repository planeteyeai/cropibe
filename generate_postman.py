import json
from datetime import datetime

postman_collection = {
    "info": {
        "name": "Farm Management API",
        "_postman_id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
        "description": "Postman collection for interacting with the Farm Management API.",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "Get All Farms",
            "request": {
                "method": "GET",
                "header": [{"key": "Authorization", "value": "Token <your_token_here>", "type": "text"}],
                "url": {"raw": "{{base_url}}/farms/", "host": ["{{base_url}}"], "path": ["farms"]}
            }
        },
        {
            "name": "Create Farm",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Authorization", "value": "Token <your_token_here>", "type": "text"},
                    {"key": "Content-Type", "value": "application/json", "type": "text"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "plot_id": 1,
                        "address": "Plot 42, Springfield",
                        "area_size": 1.5,
                        "soil_type_id": 1,
                        "crop_type_id": 2,
                        "farm_document": None
                    })
                },
                "url": {"raw": "{{base_url}}/farms/", "host": ["{{base_url}}"], "path": ["farms"]}
            }
        },
        {
            "name": "Get Plot GeoJSON",
            "request": {
                "method": "GET",
                "header": [{"key": "Authorization", "value": "Token <your_token_here>", "type": "text"}],
                "url": {"raw": "{{base_url}}/plots/geojson/", "host": ["{{base_url}}"], "path": ["plots", "geojson"]}
            }
        },
        {
            "name": "Get Farms Nearby",
            "request": {
                "method": "GET",
                "header": [{"key": "Authorization", "value": "Token <your_token_here>", "type": "text"}],
                "url": {
                    "raw": "{{base_url}}/farms/?lat=19.456&lng=75.123&radius=5",
                    "host": ["{{base_url}}"],
                    "path": ["farms"],
                    "query": [
                        {"key": "lat", "value": "19.456"},
                        {"key": "lng", "value": "75.123"},
                        {"key": "radius", "value": "5"}
                    ]
                }
            }
        }
    ],
    "variable": [{"key": "base_url", "value": "http://localhost:8000"}]
}

filename = f"farm_management_postman_collection_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
with open(filename, "w") as f:
    json.dump(postman_collection, f, indent=2)

print(f"Postman collection saved as {filename}")
