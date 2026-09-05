from __future__ import annotations

from collections import defaultdict

import streamlit as st

from database import get_session

from constants.status import MediaRollStatus

from models.campaign_artwork import CampaignArtwork
from models.media_roll import MediaRoll
from models.production_allocation import ProductionAllocation

from repositories.media_roll_repository import MediaRollRepository


class StepRolls:
    """
    Step 5 of the Production Batch Wizard.

    Responsibilities:
        - Load usable media rolls.
        - Show required quantity for every selected artwork.
        - Allow one artwork to use multiple rolls.
        - Prevent allocation beyond available roll balance.
        - Prevent the same roll from being selected twice
          for the same artwork.
        - Store only an allocation plan in session state.

    Important:
        This step DOES NOT create ProductionAllocation rows.
        Actual database allocation is performed during batch
        creation in the later production-batch service.

    Printer rule:
        A production batch has exactly one assigned printer.
        This step does not introduce any multi-printer logic.
    """

    @staticmethod
    def _get_selected_artworks(db):
        selected = st.session_state.get(
            "selected_artworks",
            {},
        )

        if not selected:
            return []

        artwork_ids = [
            int(artwork_id)
            for artwork_id in selected.keys()
        ]

        if not artwork_ids:
            return []

        artworks = (
            db.query(CampaignArtwork)
            .filter(
                CampaignArtwork.id.in_(artwork_ids)
            )
            .all()
        )

        artwork_map = {
            artwork.id: artwork
            for artwork in artworks
        }

        return [
            artwork_map[artwork_id]
            for artwork_id in artwork_ids
            if artwork_id in artwork_map
        ]

    @staticmethod
    def _planned_quantity(artwork_id: int) -> float:
        selected = st.session_state.get(
            "selected_artworks",
            {},
        )

        artwork_data = selected.get(
            artwork_id,
            {},
        )

        return float(
            artwork_data.get(
                "planned_sqft",
                0.0,
            )
        )

    @staticmethod
    def _normalise_plan() -> dict:
        """
        Ensure the session-state allocation plan has a
        predictable structure.

        Structure:

        {
            artwork_id: [
                {
                    "roll_id": int | None,
                    "allocated_sqft": float,
                }
            ]
        }
        """

        plan = st.session_state.get(
            "roll_allocations",
            {},
        )

        if not isinstance(plan, dict):
            plan = {}

        normalised = {}

        for artwork_id, rows in plan.items():

            try:
                artwork_id = int(artwork_id)
            except (TypeError, ValueError):
                continue

            if not isinstance(rows, list):
                rows = []

            clean_rows = []

            for row in rows:

                if not isinstance(row, dict):
                    continue

                roll_id = row.get("roll_id")

                try:
                    roll_id = (
                        int(roll_id)
                        if roll_id is not None
                        else None
                    )
                except (TypeError, ValueError):
                    roll_id = None

                try:
                    allocated_sqft = float(
                        row.get(
                            "allocated_sqft",
                            0.0,
                        )
                    )
                except (TypeError, ValueError):
                    allocated_sqft = 0.0

                clean_rows.append(
                    {
                        "roll_id": roll_id,
                        "allocated_sqft": max(
                            allocated_sqft,
                            0.0,
                        ),
                    }
                )

            normalised[artwork_id] = clean_rows

        return normalised

    @staticmethod
    def _existing_reserved_by_roll(db) -> dict[int, float]:
        """
        Calculate quantities already committed against rolls
        by existing production allocations.

        Completed allocations are intentionally excluded because
        they represent production that has already finished.

        The current wizard itself has not created DB allocations,
        so its quantities are handled separately.
        """

        reserved_statuses = {
            "ALLOCATED",
            "RESERVED",
            "PARTIALLY_PRINTED",
            "PRINTING",
        }

        allocations = (
            db.query(ProductionAllocation)
            .filter(
                ProductionAllocation.status.in_(
                    reserved_statuses
                )
            )
            .all()
        )

        result = defaultdict(float)

        for allocation in allocations:

            if allocation.media_roll_id is None:
                continue

            result[
                allocation.media_roll_id
            ] += float(
                allocation.allocated_sqft or 0.0
            )

        return dict(result)

    @staticmethod
    def _roll_available_balance(
        roll: MediaRoll,
        existing_reserved: float,
        wizard_reserved: float,
    ) -> float:
        """
        Calculate the amount that can safely be allocated.

        MediaRoll.available_sqft represents physical inventory
        balance.

        Existing allocations and current wizard allocations are
        treated as reservations against that balance.
        """

        physical_balance = float(
            roll.available_sqft or 0.0
        )

        available = (
            physical_balance
            - existing_reserved
            - wizard_reserved
        )

        return max(
            available,
            0.0,
        )

    @staticmethod
    def _validate_plan(
        db,
        artworks,
        rolls,
    ):
        plan = StepRolls._normalise_plan()

        roll_map = {
            roll.id: roll
            for roll in rolls
        }

        existing_reserved = (
            StepRolls._existing_reserved_by_roll(db)
        )

        errors = []
        total_allocated = 0.0

        wizard_by_roll = defaultdict(float)

        # -----------------------------------------------------
        # Validate every artwork
        # -----------------------------------------------------

        for artwork in artworks:

            artwork_id = artwork.id

            planned_sqft = (
                StepRolls._planned_quantity(
                    artwork_id
                )
            )

            rows = plan.get(
                artwork_id,
                [],
            )

            artwork_total = 0.0
            artwork_rolls = set()

            for row_index, row in enumerate(rows):

                roll_id = row.get("roll_id")
                quantity = float(
                    row.get(
                        "allocated_sqft",
                        0.0,
                    )
                    or 0.0
                )

                if roll_id is None:

                    if quantity > 0:
                        errors.append(
                            (
                                f"{artwork.artwork_code}: "
                                f"Roll must be selected for "
                                f"allocation row {row_index + 1}."
                            )
                        )

                    continue

                if roll_id not in roll_map:

                    errors.append(
                        (
                            f"{artwork.artwork_code}: "
                            f"Selected media roll is no longer "
                            f"available."
                        )
                    )

                    continue

                if quantity <= 0:

                    errors.append(
                        (
                            f"{artwork.artwork_code}: "
                            f"Allocation quantity must be greater "
                            f"than zero."
                        )
                    )

                    continue

                if roll_id in artwork_rolls:

                    errors.append(
                        (
                            f"{artwork.artwork_code}: "
                            f"The same media roll cannot be "
                            f"allocated twice to the same artwork."
                        )
                    )

                artwork_rolls.add(roll_id)

                artwork_total += quantity
                wizard_by_roll[roll_id] += quantity

            if artwork_total > planned_sqft + 0.0001:

                errors.append(
                    (
                        f"{artwork.artwork_code}: allocated quantity "
                        f"{artwork_total:,.2f} Sq Ft exceeds planned "
                        f"quantity {planned_sqft:,.2f} Sq Ft."
                    )
                )

            total_allocated += artwork_total

            if artwork_total < planned_sqft - 0.0001:

                errors.append(
                    (
                        f"{artwork.artwork_code}: "
                        f"{planned_sqft - artwork_total:,.2f} Sq Ft "
                        f"still needs roll allocation."
                    )
                )

        # -----------------------------------------------------
        # Validate roll balances across the entire wizard
        # -----------------------------------------------------

        for roll_id, wizard_quantity in wizard_by_roll.items():

            roll = roll_map.get(roll_id)

            if roll is None:
                continue

            already_reserved = existing_reserved.get(
                roll_id,
                0.0,
            )

            physical_balance = float(
                roll.available_sqft or 0.0
            )

            remaining = (
                physical_balance
                - already_reserved
                - wizard_quantity
            )

            if remaining < -0.0001:

                errors.append(
                    (
                        f"Roll {roll.roll_number}: allocation "
                        f"exceeds available balance by "
                        f"{abs(remaining):,.2f} Sq Ft."
                    )
                )

        return errors, total_allocated

    @staticmethod
    def _roll_label(
        roll: MediaRoll,
        available_sqft: float,
    ) -> str:

        return (
            f"{roll.roll_number} "
            f"— {available_sqft:,.2f} Sq Ft available"
        )

    @staticmethod
    def render():

        db = get_session()

        try:

            st.subheader(
                "Step 5 : Allocate Media Rolls"
            )

            artworks = (
                StepRolls._get_selected_artworks(db)
            )

            if not artworks:

                st.error(
                    (
                        "No artwork quantities have been selected. "
                        "Please go back to Step 3."
                    )
                )

                if st.button("⬅ Back"):

                    st.session_state.wizard_step = 3
                    st.rerun()

                return

            # -------------------------------------------------
            # Load usable rolls
            # -------------------------------------------------

            rolls = (
                MediaRollRepository.available_for_allocation(
                    db
                )
            )

            if not rolls:

                st.error(
                    (
                        "No media rolls are currently available "
                        "for production allocation."
                    )
                )

                if st.button("⬅ Back"):

                    st.session_state.wizard_step = 4
                    st.rerun()

                return

            existing_reserved = (
                StepRolls._existing_reserved_by_roll(db)
            )

            # -------------------------------------------------
            # Initialise plan
            # -------------------------------------------------

            plan = StepRolls._normalise_plan()

            for artwork in artworks:

                if artwork.id not in plan:

                    plan[artwork.id] = [
                        {
                            "roll_id": None,
                            "allocated_sqft": 0.0,
                        }
                    ]

            st.session_state.roll_allocations = plan

            # -------------------------------------------------
            # Header summary
            # -------------------------------------------------

            total_planned = float(
                st.session_state.get(
                    "total_planned_sqft",
                    0.0,
                )
            )

            current_allocated = sum(
                float(row.get("allocated_sqft", 0.0) or 0.0)
                for rows in plan.values()
                for row in rows
            )

            remaining_total = max(
                total_planned - current_allocated,
                0.0,
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric(
                    "Planned",
                    f"{total_planned:,.2f} Sq Ft",
                )

            with c2:
                st.metric(
                    "Allocated",
                    f"{current_allocated:,.2f} Sq Ft",
                )

            with c3:
                st.metric(
                    "Remaining",
                    f"{remaining_total:,.2f} Sq Ft",
                )

            st.divider()

            # -------------------------------------------------
            # Artwork allocation sections
            # -------------------------------------------------

            roll_map = {
                roll.id: roll
                for roll in rolls
            }

            for artwork in artworks:

                artwork_id = artwork.id

                planned_sqft = (
                    StepRolls._planned_quantity(
                        artwork_id
                    )
                )

                rows = plan[artwork_id]

                st.markdown(
                    f"### 🎨 {artwork.artwork_code}"
                )

                st.caption(
                    (
                        f"{artwork.artwork_name} · "
                        f"Required: {planned_sqft:,.2f} Sq Ft"
                    )
                )

                artwork_allocated = sum(
                    float(
                        row.get(
                            "allocated_sqft",
                            0.0,
                        )
                        or 0.0
                    )
                    for row in rows
                )

                artwork_remaining = max(
                    planned_sqft - artwork_allocated,
                    0.0,
                )

                st.progress(
                    min(
                        artwork_allocated
                        / planned_sqft
                        if planned_sqft > 0
                        else 0.0,
                        1.0,
                    )
                )

                st.caption(
                    (
                        f"Allocated: "
                        f"{artwork_allocated:,.2f} Sq Ft · "
                        f"Remaining: "
                        f"{artwork_remaining:,.2f} Sq Ft"
                    )
                )

                for row_index, row in enumerate(rows):

                    current_roll_id = row.get(
                        "roll_id"
                    )

                    # Calculate roll availability after
                    # allocations from other rows in this wizard.
                    wizard_other_roll_usage = defaultdict(float)

                    for other_artwork_id, other_rows in plan.items():

                        for other_index, other_row in enumerate(
                            other_rows
                        ):

                            if (
                                other_artwork_id == artwork_id
                                and other_index == row_index
                            ):
                                continue

                            other_roll_id = other_row.get(
                                "roll_id"
                            )

                            if other_roll_id is not None:

                                wizard_other_roll_usage[
                                    other_roll_id
                                ] += float(
                                    other_row.get(
                                        "allocated_sqft",
                                        0.0,
                                    )
                                    or 0.0
                                )

                    options = {
                        "Select media roll": None
                    }

                    for roll in rolls:

                        available = (
                            StepRolls._roll_available_balance(
                                roll,
                                existing_reserved.get(
                                    roll.id,
                                    0.0,
                                ),
                                wizard_other_roll_usage.get(
                                    roll.id,
                                    0.0,
                                ),
                            )
                        )

                        if available <= 0:
                            continue

                        # Same roll cannot be repeated for the
                        # same artwork.
                        already_used_for_artwork = any(
                            other_row.get("roll_id") == roll.id
                            for other_index, other_row in enumerate(rows)
                            if other_index != row_index
                        )

                        if already_used_for_artwork:
                            continue

                        options[
                            StepRolls._roll_label(
                                roll,
                                available,
                            )
                        ] = roll.id

                    option_labels = list(
                        options.keys()
                    )

                    current_index = 0

                    if current_roll_id is not None:

                        for index, label in enumerate(
                            option_labels
                        ):

                            if options[label] == current_roll_id:

                                current_index = index
                                break

                    col1, col2, col3 = st.columns(
                        [2.5, 1.5, 0.7]
                    )

                    with col1:

                        selected_label = st.selectbox(
                            "Media Roll",
                            option_labels,
                            index=current_index,
                            key=(
                                f"roll_select_"
                                f"{artwork_id}_"
                                f"{row_index}"
                            ),
                        )

                        selected_roll_id = (
                            options[selected_label]
                        )

                    with col2:

                        current_quantity = float(
                            row.get(
                                "allocated_sqft",
                                0.0,
                            )
                            or 0.0
                        )

                        max_for_row = artwork_remaining

                        if selected_roll_id is not None:

                            other_usage = (
                                wizard_other_roll_usage.get(
                                    selected_roll_id,
                                    0.0,
                                )
                            )

                            roll = roll_map.get(
                                selected_roll_id
                            )

                            if roll is not None:

                                max_for_row = min(
                                    max(
                                        float(
                                            roll.available_sqft
                                            or 0.0
                                        )
                                        - existing_reserved.get(
                                            selected_roll_id,
                                            0.0,
                                        )
                                        - other_usage,
                                        0.0,
                                    ),
                                    artwork_remaining
                                    + current_quantity,
                                )

                        if max_for_row <= 0:

                            max_for_row = max(
                                current_quantity,
                                0.0,
                            )

                        quantity = st.number_input(
                            "Sq Ft",
                            min_value=0.0,
                            max_value=max(
                                max_for_row,
                                0.01,
                            ),
                            value=min(
                                max(
                                    current_quantity,
                                    0.0,
                                ),
                                max_for_row,
                            ),
                            step=1.0,
                            key=(
                                f"roll_qty_"
                                f"{artwork_id}_"
                                f"{row_index}"
                            ),
                        )

                    with col3:

                        st.write("")

                        if len(rows) > 1:

                            if st.button(
                                "🗑️",
                                key=(
                                    f"remove_roll_"
                                    f"{artwork_id}_"
                                    f"{row_index}"
                                ),
                            ):

                                rows.pop(row_index)

                                if not rows:

                                    rows.append(
                                        {
                                            "roll_id": None,
                                            "allocated_sqft": 0.0,
                                        }
                                    )

                                st.session_state.roll_allocations = (
                                    plan
                                )

                                st.rerun()

                    # Capture current widget values.
                    row["roll_id"] = selected_roll_id
                    row["allocated_sqft"] = float(
                        quantity
                    )

                if st.button(
                    "➕ Add Another Roll",
                    key=f"add_roll_{artwork_id}",
                ):

                    rows.append(
                        {
                            "roll_id": None,
                            "allocated_sqft": 0.0,
                        }
                    )

                    st.session_state.roll_allocations = plan
                    st.rerun()

                st.divider()

            # -------------------------------------------------
            # Final validation
            # -------------------------------------------------

            errors, total_allocated = (
                StepRolls._validate_plan(
                    db,
                    artworks,
                    rolls,
                )
            )

            st.session_state.roll_allocations = plan

            if errors:

                st.warning(
                    "Roll allocation requires attention."
                )

                for error in errors:

                    st.error(error)

            else:

                st.success(
                    (
                        f"All {total_allocated:,.2f} Sq Ft "
                        "has been allocated successfully."
                    )
                )

            # -------------------------------------------------
            # Navigation
            # -------------------------------------------------

            c1, c2 = st.columns(2)

            with c1:

                if st.button("⬅ Back"):

                    st.session_state.wizard_step = 4
                    st.rerun()

            with c2:

                can_continue = (
                    len(errors) == 0
                    and total_allocated > 0
                )

                if st.button(
                    "Next ➜",
                    type="primary",
                    disabled=not can_continue,
                ):

                    st.session_state.wizard_step = 6
                    st.rerun()

        finally:

            db.close()