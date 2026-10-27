import shutil
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from .config import AI_MODEL_OPTIONS, SIMILARITY_THRESHOLD
from .organizer import scan_and_organize
from .file_utils import (
    copy_folder_to_location,
    get_desktop_folder,
    resolve_user_path,
)
from .planning import (
    CleanupPlan,
    create_cleanup_plan,
    validate_cleanup_plan,
    verify_cleanup_output,
)
from .styles import apply_styles



def render_app():
    apply_styles()

    with st.sidebar:

        st.markdown("## 🧹 Digital Mess Cleanup")

        st.caption("An AI-assisted cleanup planning agent")

        st.divider()



        st.markdown("### Features")

        st.markdown(

            """

            - 🧭 Goal-based cleanup plan

            - ✅ Review and approve before running

            - 📁 Automatic file sorting

            - 🔎 Exact duplicate detection

            - 🖼️ Similar image detection

            - 🤖 AI image classification

            - 📊 Cleanup report

            - 🛡️ Original files preserved

            """

        )



        st.divider()

        st.markdown("### About")

        st.caption(

            "Built with Python, Streamlit, Pillow, ImageHash, "

            "Pandas, and CLIP."

        )





    # --------------------------------------------------

    # MAIN UI

    # --------------------------------------------------



    st.markdown(

        '<div class="main-title">🧹 Digital Mess Cleanup</div>',

        unsafe_allow_html=True,

    )

    st.markdown(

        '<div class="subtitle">'

        "Set a goal, review the agent's plan, then approve a safe cleanup."

        "</div>",

        unsafe_allow_html=True,

    )



    st.info(

        "Your original files are not deleted or moved. Choose where the "

        "organized copy should be saved below."

    )



    with st.container(border=True):

        st.subheader("1. Choose your folder")



        source_text = st.text_input(

            "Full path to the folder you want to clean",

            placeholder=r"C:\Users\YourName\Downloads",

            help="Enter a folder path that exists on the computer running Streamlit.",

        )



        # Default to Desktop, including the common OneDrive Desktop location.
        default_desktop = get_desktop_folder()

        destination_text = st.text_input(
            "Where should the organized folder be downloaded?",
            value=str(default_desktop / "Organized_Files"),
            help=(
                r"Enter the folder path, for example "
                r"C:\Users\YourName\Desktop\Organized_Files. The folder is "
                "created only when you click Download. If it already exists, "
                "the app adds _1, _2, etc."
            ),
        )

        st.caption(
            "The path is used only when you click Download. Existing folder "
            "names are preserved; a numbered folder is created instead."
        )

        st.subheader("2. Choose cleanup options")



        use_ai = st.checkbox(

            "Enable AI image classification",

            value=True,

            help=(
                "Uses CLIP to classify unique images. The first run downloads the "
                "selected model."
            ),

        )

        selected_ai_model = st.selectbox(
            "AI model",
            options=list(AI_MODEL_OPTIONS),
            index=0,
            disabled=not use_ai,
            help=(
                "The fast model is recommended for CPU-only computers. "
                "Balanced and higher-accuracy models take longer."
            ),
        )

        cleanup_goal = st.text_input(
            "Cleanup goal",
            value="Organize all files safely",
            help=(
                "The local planner recognizes file types such as photos, "
                "documents, videos, audio, code, or all files. Unknown goals "
                "safely default to all file types."
            ),
        )



        ai_threshold = st.slider(

            "AI review threshold",

            min_value=0.05,

            max_value=0.80,

            value=0.20,

            step=0.05,

            disabled=not use_ai,

            help=(

                "Images with a relative score below this value go to "

                "Images_Review. This score is not a calibrated probability."

            ),

        )



        st.caption(

            "Similar-image threshold: "

            f"{SIMILARITY_THRESHOLD} pHash distance. Lower values are stricter."

        )



        create_plan = st.button(
            "1. Analyze folder and create plan",
            type="primary",
            use_container_width=True,
        )

    if create_plan:
        st.session_state.pop("cleanup_plan", None)
        if not source_text.strip():
            st.error("Please enter the path of the folder you want to clean.")
        elif not destination_text.strip():
            st.error("Please enter a destination folder.")
        else:
            try:
                with st.spinner("Inspecting files and preparing a cleanup plan..."):
                    cleanup_plan = create_cleanup_plan(
                        source_folder=Path(source_text.strip().strip('"')),
                        output_folder=Path(destination_text.strip().strip('"')),
                        goal=cleanup_goal,
                        use_ai=use_ai,
                        model_name=AI_MODEL_OPTIONS[selected_ai_model],
                        ai_threshold=ai_threshold,
                    )
                st.session_state["cleanup_plan"] = cleanup_plan
            except Exception as error:
                st.error(f"Could not create a cleanup plan: {error}")

    plan: CleanupPlan | None = st.session_state.get("cleanup_plan")
    if plan is not None:
        st.divider()
        st.subheader("Agent plan — review before approval")
        st.write(f"**Goal:** {plan['goal']}")
        st.caption(f"**Interpreted scope:** {plan['scope_summary']}")
        st.caption(
            "Download destination (created only after you click Download):"
        )
        st.code(plan["output_folder"], language=None)

        current_source = resolve_user_path(
            Path(source_text.strip().strip('"'))
        )
        current_output = resolve_user_path(
            Path(destination_text.strip().strip('"'))
        )
        plan_matches = (
            current_source == resolve_user_path(Path(plan["source_folder"]))
            and current_output == resolve_user_path(Path(plan["output_folder"]))
            and cleanup_goal.strip() == plan["goal"]
            and use_ai == plan["use_ai"]
            and AI_MODEL_OPTIONS[selected_ai_model] == plan["model_name"]
            and ai_threshold == plan["ai_threshold"]
        )
        if not plan_matches:
            st.warning("Your settings changed. Create a fresh plan before approving.")

        metric_columns = st.columns(2)
        metric_columns[0].metric("Files in scope", plan["file_count"])
        metric_columns[1].metric("Images", plan["image_count"])
        if plan["category_counts"]:
            st.dataframe(
                pd.DataFrame(
                    [
                        {"File type": category, "Files": count}
                        for category, count in sorted(
                            plan["category_counts"].items()
                        )
                    ]
                ),
                hide_index=True,
                use_container_width=True,
            )
        for action in plan["actions"]:
            st.markdown(f"- {action}")

        with st.expander("Files included in this plan"):
            for item in plan["files"][:20]:
                st.code(item["path"], language=None)
            if plan["file_count"] > 20:
                st.caption(
                    f"Showing 20 of {plan['file_count']} planned files."
                )

        approve_plan = st.button(
            "2. Approve plan and organize files",
            type="primary",
            use_container_width=True,
            disabled=not plan_matches or plan["file_count"] == 0,
        )
        if plan["file_count"] == 0:
            st.info("No files matched this goal, so there is nothing to run.")

        if approve_plan:
            staging_root: Path | None = None
            try:
                with st.spinner(
                    "Checking the plan and preparing the organized folder..."
                ):
                    planned_files = validate_cleanup_plan(plan)
                    staging_root = Path(
                        tempfile.mkdtemp(prefix="digital_mess_cleanup_")
                    )
                    staging_folder = staging_root / "organized"
                    output_path, rows = scan_and_organize(
                        source_folder=Path(plan["source_folder"]),
                        output_folder=staging_folder,
                        use_ai=plan["use_ai"],
                        ai_threshold=plan["ai_threshold"],
                        ai_model_name=plan["model_name"],
                        planned_files=planned_files,
                    )
                    verification = verify_cleanup_output(
                        Path(plan["source_folder"]), output_path, rows
                    )

                st.session_state["cleanup_rows"] = rows
                st.session_state["cleanup_staged_output"] = str(output_path)
                st.session_state["cleanup_staging_root"] = str(staging_root)
                st.session_state["cleanup_download_target"] = plan["output_folder"]
                st.session_state["cleanup_source"] = plan["source_folder"]
                st.session_state["cleanup_verification"] = verification
                st.session_state.pop("cleanup_output", None)
                st.session_state.pop("cleanup_plan", None)
                st.success(
                    "Your organized folder is ready. Click Download to create "
                    "it at the selected location."
                )
                st.info(
                    f"Download location: {plan['output_folder']} "
                    "(a numbered name will be used if it already exists)."
                )
                if verification["file_errors"]:
                    st.warning(
                        f"{verification['file_errors']} file(s) could not be "
                        "copied. See the report for details."
                    )
            except Exception as error:
                if staging_root is not None and staging_root.exists():
                    shutil.rmtree(staging_root)
                st.error(f"Could not execute or verify the cleanup plan: {error}")





    # --------------------------------------------------

    # RESULTS DASHBOARD

    # --------------------------------------------------



    if "cleanup_rows" in st.session_state:

        rows = st.session_state["cleanup_rows"]

        output_path = st.session_state.get("cleanup_output")



        df = pd.DataFrame(rows)



        st.divider()

        st.header("📊 Cleanup Dashboard")



        total_files = len(df)



        if total_files:

            exact_duplicates = int(

                (df["Status"] == "Exact Duplicate").sum()

            )

            similar_images = int(

                (df["Status"] == "Similar Image").sum()

            )

            ai_classified = int(

                (df["Status"] == "AI Classified").sum()

            )

            review_required = int(

                df["Status"].isin(

                    [

                        "AI Review Required",

                        "AI Classification Failed",

                    ]

                ).sum()

            )

            errors = int((df["Status"] == "Error").sum())

        else:

            exact_duplicates = 0

            similar_images = 0

            ai_classified = 0

            review_required = 0

            errors = 0



        col1, col2, col3 = st.columns(3)

        col1.metric("Files Scanned", total_files)

        col2.metric("Exact Duplicates", exact_duplicates)

        col3.metric("Similar Images", similar_images)



        col4, col5, col6 = st.columns(3)

        col4.metric("AI Classified", ai_classified)

        col5.metric("Needs Review", review_required)

        col6.metric("Errors", errors)



        st.markdown("### 📂 Download organized folder")
        if output_path is None:
            staged_output = Path(
                st.session_state["cleanup_staged_output"]
            )
            requested_path = Path(
                st.session_state["cleanup_download_target"]
            )
            st.info(
                "The organized folder is prepared. It has not been created at "
                "the download location yet."
            )
            st.caption("Selected download location:")
            st.code(str(requested_path), language=None)
            if st.button(
                "⬇️ Download folder",
                type="primary",
                use_container_width=True,
                key="download_organized_folder",
            ):
                try:
                    downloaded_folder = copy_folder_to_location(
                        staged_output, requested_path
                    )
                    staging_root = Path(
                        st.session_state["cleanup_staging_root"]
                    )
                    st.session_state["cleanup_output"] = str(downloaded_folder)
                    st.session_state.pop("cleanup_staged_output", None)
                    st.session_state.pop("cleanup_staging_root", None)
                    shutil.rmtree(staging_root)
                    output_path = str(downloaded_folder)
                    st.success(
                        "Folder downloaded successfully to: "
                        f"{downloaded_folder}"
                    )
                except Exception as download_error:
                    st.error(
                        f"Could not download the folder: {download_error}"
                    )

        if output_path is not None:
            output_dir = Path(output_path)
            if output_dir.is_dir():
                st.success("Folder created at:")
                st.code(str(output_dir.resolve()), language=None)
            else:
                st.error(f"The downloaded folder is missing: {output_dir}")
        st.caption(
            "The download path is asked once above. If that folder name "
            "already exists, the app creates a sibling ending in _1, _2, etc."
        )



        if not df.empty:

            st.markdown("### Files by final category")



            category_counts = (

                df["Final Category"]

                .value_counts()

                .rename_axis("Category")

                .reset_index(name="Files")

            )



            st.bar_chart(

                category_counts.set_index("Category"),

                y="Files",

            )



            st.markdown("### 🔍 Search and filter the report")



            filter_options = ["All"] + sorted(

                df["Status"].dropna().unique().tolist()

            )



            selected_status = st.selectbox(

                "Filter by status",

                filter_options,

            )



            search_term = st.text_input(

                "Search file names or paths",

                placeholder="Type to search...",

            )



            filtered_df = df.copy()



            if selected_status != "All":

                filtered_df = filtered_df[

                    filtered_df["Status"] == selected_status

                ]



            if search_term.strip():

                search_lower = search_term.strip().lower()



                matches = (

                    filtered_df["File Name"].fillna("").str.lower().str.contains(

                        search_lower, regex=False

                    )

                    |

                    filtered_df["Original Path"].fillna("").str.lower().str.contains(

                        search_lower, regex=False

                    )

                )



                filtered_df = filtered_df[matches]



            st.dataframe(

                filtered_df,

                use_container_width=True,

                hide_index=True,

            )



            csv_data = df.to_csv(index=False).encode("utf-8-sig")



            st.download_button(

                "⬇️ Download Full Report (CSV)",

                data=csv_data,

                file_name="digital_mess_cleanup_report.csv",

                mime="text/csv",

                use_container_width=True,

            )



        st.caption(

            "Important: similar-image detection is heuristic. Review files in "

            "Duplicate_Review, Similar_Images_Review, and Images_Review before "

            "taking any further action. This app does not delete original files."

        )





    # --------------------------------------------------

    # FOOTER

    # --------------------------------------------------



    st.divider()

    st.markdown(

        """

        <div class="main-title">🧹 Digital Mess Cleanup</div>

        <div class="subtitle">

            A smarter way to organize files, detect duplicates,

            and classify images using AI.

        </div>

        """,

        unsafe_allow_html=True,

    )
