from pymongo import MongoClient
from pprint import pprint
import time

def timed(label, func):
    t = time.time()
    result = list(func())
    print(f"{label:35s} {(time.time() - t) * 1000:7.1f} ms")
    return result

client = MongoClient("mongodb://localhost:27017")

db = client["shop_lab"]

# --------------------------------------------------
# Q1 — Monthly revenue trend
# --------------------------------------------------

q1_rows = timed(
    "Q1 Monthly revenue",
    lambda: db.orders.aggregate([
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$order_date"},
                    "month": {"$month": "$order_date"}
                },
                "orders": {"$sum": 1},
                "revenue": {"$sum": "$total"}
            }
        },
        {
            "$sort": {
                "_id.year": 1,
                "_id.month": 1
            }
        }
    ])
)

# --------------------------------------------------
# Q2 — Top 10 products by revenue
# --------------------------------------------------

q2_rows = timed(
    "Q2 Top products",
    lambda: db.orders_embedded.aggregate([

        {
            "$unwind": "$items"
        },

        {
            "$group": {
                "_id": "$items.product_id",

                "total_qty": {
                    "$sum": "$items.quantity"
                },

                "revenue": {
                    "$sum": {
                        "$multiply": [
                            "$items.quantity",
                            "$items.unit_price_at_sale"
                        ]
                    }
                }
            }
        },

        {
            "$lookup": {
                "from": "product",
                "localField": "_id",
                "foreignField": "product_id",
                "as": "product_info"
            }
        },

        {
            "$unwind": "$product_info"
        },

        {
            "$project": {
                "_id": 0,
                "product_name": "$product_info.name",
                "total_qty": 1,
                "revenue": 1
            }
        },

        {
            "$sort": {
                "revenue": -1
            }
        },

        {
            "$limit": 10
        }

    ])
)

# --------------------------------------------------
# Q3 — Order count + avg + median by status
# --------------------------------------------------

q3_rows = timed(
    "Q3 Avg + Median",
    lambda: db.orders.aggregate([

        {
            "$group": {
                "_id": "$status",

                "number_of_orders": {
                    "$sum": 1
                },

                "average_total": {
                    "$avg": "$total"
                },

                "median_total": {
                    "$median": {
                        "input": "$total",
                        "method": "approximate"
                    }
                }
            }
        },

        {
            "$project": {
                "_id": 1,
                "number_of_orders": 1,

                "average_total": {
                    "$round": ["$average_total", 2]
                },

                "median_total": {
                    "$round": ["$median_total", 2]
                }
            }
        },

        {
            "$sort": {
                "_id": 1
            }
        }

    ])
)


# --------------------------------------------------
# Q4 — Dormant customers
# --------------------------------------------------

q4_rows = timed(
    "Q4 Dormant customers",
    lambda: db.orders.aggregate([

        {
            "$group": {
                "_id": "$customer_id",
                "last_order_date": {
                    "$max": "$order_date"
                }
            }
        },

        {
            "$addFields": {
                "days_dormant": {
                    "$dateDiff": {
                        "startDate": "$last_order_date",
                        "endDate": "$$NOW",
                        "unit": "day"
                    }
                }
            }
        },

        {
            "$match": {
                "days_dormant": {
                    "$gt": 90
                }
            }
        },

        {
            "$lookup": {
                "from": "customer",
                "localField": "_id",
                "foreignField": "customer_id",
                "as": "customer_info"
            }
        },

        {
            "$unwind": "$customer_info"
        },

        {
            "$project": {
                "_id": 0,
                "email": "$customer_info.email",

                "last_order_date": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$last_order_date"
                    }
                },

                "days_dormant": 1
            }
        },

        {
            "$sort": {
                "days_dormant": -1
            }
        }

    ])
)


# --------------------------------------------------
# Q5 — Top 20 customers by lifetime spend
# --------------------------------------------------

q5_rows = timed(
    "Q5 Customer ranking",
    lambda: db.orders.aggregate([

        {
            "$group": {
                "_id": "$customer_id",
                "lifetime_spend": {
                    "$sum": "$total"
                }
            }
        },

        {
            "$setWindowFields": {
                "sortBy": {
                    "lifetime_spend": -1
                },

                "output": {

                    "rank": {
                        "$rank": {}
                    },

                    "previous_spend": {
                        "$shift": {
                            "output": "$lifetime_spend",
                            "by": -1
                        }
                    }
                }
            }
        },

        {
            "$lookup": {
                "from": "customer",
                "localField": "_id",
                "foreignField": "customer_id",
                "as": "customer_info"
            }
        },

        {
            "$unwind": "$customer_info"
        },

        {
            "$addFields": {
                "gap_to_previous": {
                    "$subtract": [
                        "$previous_spend",
                        "$lifetime_spend"
                    ]
                }
            }
        },

        {
            "$project": {
                "_id": 0,
                "rank": 1,
                "email": "$customer_info.email",

                "lifetime_spend": {
                    "$round": [
                        "$lifetime_spend",
                        2
                    ]
                },

                "gap_to_previous": {
                    "$round": [
                        "$gap_to_previous",
                        2
                    ]
                }
            }
        },

        {
            "$sort": {
                "lifetime_spend": -1
            }
        },

        {
            "$limit": 20
        }

    ])
)