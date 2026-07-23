import pandas as pd

from models.campaign_location import CampaignLocation


class CampaignImportService:

    @staticmethod
    def prepare_locations(df: pd.DataFrame):

        rows = []

        for _, row in df.iterrows():

            width = float(row["Wall Width (ft)"])
            height = float(row["Wall Height (ft)"])
            qty = int(row["Qty"])

            sqft = width * height

            rows.append(

                CampaignLocation(

                    state=row["State"],

                    district=row["District"],

                    town=row["Town"],

                    pincode=row.get("Pincode"),

                    wall_width_ft=width,

                    wall_height_ft=height,

                    wall_sqft=sqft,

                    quantity=qty,

                    total_sqft=sqft * qty,

                    wall_type=row.get("Wall Type"),

                    latitude=row.get("Latitude"),

                    longitude=row.get("Longitude"),

                    remarks=row.get("Remarks")

                )

            )

        return rows
