def _create_campaign(db, suffix=""):
    """
    Create a valid Campaign fixture for Pack 9B tests.

    suffix is used to keep campaign records unique when
    multiple fixtures are created in the same test/database.
    """

    from datetime import date

    from models.campaign import Campaign

    suffix = str(suffix)

    campaign_code = (
        "PACK9B-TEST-CAMPAIGN"
        if not suffix
        else f"PACK9B-TEST-CAMPAIGN-{suffix}"
    )

    campaign_name = (
        "PACK9B TEST CAMPAIGN"
        if not suffix
        else f"PACK9B TEST CAMPAIGN {suffix}"
    )

    campaign = Campaign(
        campaign_code=campaign_code,
        client_name="PACK9B TEST CLIENT",
        brand_name="PACK9B TEST BRAND",
        campaign_name=campaign_name,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
    )

    db.add(campaign)
    db.flush()

    return campaign
