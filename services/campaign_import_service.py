from __future__ import annotations

import pandas as pd

from models.campaign_location import CampaignLocation


class CampaignImportService:

    @staticmethod
    def create_locations(
        df: pd.DataFrame,
        version_id: int | None = None,
    ) -> list[CampaignLocation]:
        """
        Convert validated campaign Excel rows into
        CampaignLocation objects.

        version_id is optional because CampaignService
        assigns the CampaignVersion relationship during
        the atomic campaign creation transaction.
        """

        locations: list[CampaignLocation] = []

        for _, row in df.iterrows():

            width = float(
                row["Wall Width (ft)"]
            )

            height = float(
                row["Wall Height (ft)"]
            )

            qty = int(
                row["Qty"]
            )

            wall_sqft = width * height

            total_sqft = wall_sqft * qty

            locations.append(
                CampaignLocation(
                    campaign_version_id=version_id,

                    state=row["State"],
                    district=row["District"],
                    town=row["Town"],

                    pincode=row.get("Pincode"),

                    wall_width_ft=width,
                    wall_height_ft=height,

                    wall_sqft=wall_sqft,
                    quantity=qty,
                    total_sqft=total_sqft,

                    wall_type=row.get("Wall Type"),

                    latitude=row.get("Latitude"),
                    longitude=row.get("Longitude"),

                    remarks=row.get("Remarks"),
                )
            )

        return locations