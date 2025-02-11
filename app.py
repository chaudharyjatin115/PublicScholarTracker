import streamlit as st
import pandas as pd
from database import get_all_servants, get_all_politicians, add_servant, add_politician, seed_database, delete_politician, delete_servant, add_children_to_politician, check_politician_exists, add_children_to_officer
from utils import (
    create_education_distribution_chart,
    create_yearly_trends,
    create_department_education_heatmap,
    get_western_education_stats
)
from data_integration import DataIntegrator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Indian Public Service Education Tracker",
    page_icon="🎓",
    layout="wide"
)

# Initialize database with seed data
seed_database()

# Title and introduction
st.title("🎓 Indian Public Service Education Tracker")
st.markdown("""
This dashboard provides insights into the educational background of Indian public servants
and politicians, with a focus on tracking international education patterns.
""")

# Data Collection Section
st.sidebar.markdown("---")
st.sidebar.header("🔄 Data Collection")

if st.sidebar.button("Collect New Data"):
    try:
        with st.spinner("Collecting data from government websites..."):
            integrator = DataIntegrator()
            politicians_count = integrator.import_politicians()
            servants_count = integrator.import_civil_servants()

        st.sidebar.success(f"""
        Data collection completed:
        - {politicians_count} politicians added
        - {servants_count} civil servants added
        """)

        # Clear the cache to reflect new data
        st.cache_data.clear()

        # Reload the data
        servants_df, officer_family_df, politicians_df, family_df = load_data()
    except Exception as e:
        st.sidebar.error(f"Error collecting data: {str(e)}")
        logger.error(f"Data collection error: {str(e)}")


# Load data
@st.cache_data
def load_data():
    servants, officer_family = get_all_servants()
    politicians, family = get_all_politicians()
    return servants, officer_family, politicians, family

servants_df, officer_family_df, politicians_df, family_df = load_data()

# Data selection
data_view = st.radio(
    "Select Data View",
    ["Public Servants", "Politicians & Family Members"]
)

if data_view == "Public Servants":
    st.header("📊 Public Servants Analysis")

    # Sidebar filters
    st.sidebar.header("Filters")

    if not servants_df.empty:
        selected_departments = st.sidebar.multiselect(
            "Select Departments",
            options=servants_df['department'].unique(),
            default=servants_df['department'].unique()
        )

        selected_education = st.sidebar.multiselect(
            "Select Education Locations",
            options=servants_df['education_location'].unique(),
            default=servants_df['education_location'].unique()
        )

        # Filter data
        filtered_df = servants_df[
            (servants_df['department'].isin(selected_departments)) &
            (servants_df['education_location'].isin(selected_education))
        ].copy()
    else:
        st.warning("No public servant data available.")
        filtered_df = pd.DataFrame(columns=['id', 'name', 'department', 'joining_year', 
                                          'education_location', 'university', 'degree_level'])

    # Display officer information and family members
    if not filtered_df.empty:
        st.subheader("👥 Officers List")
        for _, servant in filtered_df.iterrows():
            with st.expander(f"👤 {servant['name']} ({servant['department']})"):
                # Create three columns for better layout
                info_col1, info_col2, info_col3 = st.columns(3)

                with info_col1:
                    st.markdown("**🏢 Department**")
                    st.info(servant['department'])

                with info_col2:
                    st.markdown("**🎓 Education**")
                    st.info(f"{servant['degree_level']} from {servant['university']}")

                with info_col3:
                    st.markdown("**🌍 Location**")
                    st.info(servant['education_location'])

                # Family members
                family_members = officer_family_df[officer_family_df['officer_id'] == servant['id']]
                if not family_members.empty:
                    st.markdown("---")
                    st.markdown("### 👨‍👩‍👧‍👦 Family Members")
                    for _, member in family_members.iterrows():
                        st.markdown(f"""
                        <div style='margin-left: 20px; border-left: 2px solid #f63366; padding-left: 20px;'>
                            <h4 style='color: #f63366;'>├─ {member['name']} ({member['relation_type']})</h4>
                            <p style='margin-left: 20px;'>
                                📚 Education: {member['degree_level']}<br>
                                🏛️ University: {member['university']}<br>
                                🌍 Location: {member['education_location']}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No family members recorded")

                # Delete button
                if st.button("🗑️ Delete", key=f"del_servant_{servant['id']}"):
                    if delete_servant(servant['id']):
                        st.success(f"Deleted {servant['name']}")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Failed to delete public servant")

                st.markdown("---")

else:
    # Politicians and family members view
    st.header("🏛️ Politicians & Family Analysis")

    # Sidebar filters
    st.sidebar.header("Filters")

    if not politicians_df.empty:
        selected_parties = st.sidebar.multiselect(
            "Select Parties",
            options=politicians_df['party'].unique(),
            default=politicians_df['party'].unique()
        )

        # Filter data
        filtered_politicians = politicians_df[politicians_df['party'].isin(selected_parties)]
        filtered_family = family_df[family_df['politician_name'].isin(filtered_politicians['name'])]

        # Display hierarchical view with enhanced styling
        st.subheader("👨‍👩‍👧‍👦 Family Tree View")

        for _, politician in filtered_politicians.iterrows():
            with st.expander(f"🏛️ {politician['name']} ({politician['party']})"):
                # Create three columns for better layout
                info_col1, info_col2, info_col3 = st.columns(3)

                with info_col1:
                    st.markdown("**🎭 Position**")
                    st.info(politician['position'])

                with info_col2:
                    st.markdown("**🎓 Education**")
                    st.info(f"{politician['degree_level']} from {politician['university']}")

                with info_col3:
                    st.markdown("**🌍 Location**")
                    st.info(politician['education_location'])

                # Family members with enhanced tree structure
                family_members = filtered_family[filtered_family['politician_name'] == politician['name']]
                if not family_members.empty:
                    st.markdown("---")
                    st.markdown("### 👨‍👩‍👧‍👦 Family Members")
                    for _, member in family_members.iterrows():
                        st.markdown(f"""
                        <div style='margin-left: 20px; border-left: 2px solid #f63366; padding-left: 20px;'>
                            <h4 style='color: #f63366;'>├─ {member['name']} ({member['relation_type']})</h4>
                            <p style='margin-left: 20px;'>
                                📚 Education: {member['degree_level']}<br>
                                🏛️ University: {member['university']}<br>
                                🌍 Location: {member['education_location']}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No family members recorded")

                st.markdown("---")

        # Add delete buttons for each politician
        for _, politician in filtered_politicians.iterrows():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"🏛️ {politician['name']} ({politician['party']})")
            with col2:
                if st.button("🗑️ Delete", key=f"del_{politician['id']}"):
                    if delete_politician(politician['id']):
                        st.success(f"Deleted {politician['name']} and associated family members")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Failed to delete politician")


        # Statistics in columns
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Politicians", len(filtered_politicians))
            western_edu_politicians = filtered_politicians[
                filtered_politicians['education_location'].isin(['USA', 'UK', 'Canada', 'Australia'])
            ]
            st.metric("Western Educated Politicians",
                     f"{len(western_edu_politicians)} ({len(western_edu_politicians)/len(filtered_politicians)*100:.1f}%)")

        with col2:
            st.metric("Total Family Members", len(filtered_family))
            if not filtered_family.empty:
                western_edu_family = filtered_family[
                    filtered_family['education_location'].isin(['USA', 'UK', 'Canada', 'Australia'])
                ]
                st.metric("Western Educated Family Members",
                         f"{len(western_edu_family)} ({len(western_edu_family)/len(filtered_family)*100:.1f}%)")

        # Education distribution charts
        st.subheader("📊 Education Distribution")
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(
                create_education_distribution_chart(filtered_politicians),
                use_container_width=True
            )
            st.caption("Politicians' Education Distribution")

        with col2:
            if not filtered_family.empty:
                st.plotly_chart(
                    create_education_distribution_chart(filtered_family),
                    use_container_width=True
                )
                st.caption("Family Members' Education Distribution")

    else:
        st.warning("No politician data available.")
        filtered_politicians = pd.DataFrame()
        filtered_family = pd.DataFrame()

# Add new entry forms
if data_view == "Public Servants":
    st.header("📝 Add New Officer")

    # Option to add to existing officer
    add_to_existing = st.checkbox("Add children to existing officer")

    with st.form("new_officer_form"):
        if add_to_existing:
            # Get list of existing officers
            existing_officers = servants_df[['id', 'name', 'department']].drop_duplicates()
            selected_officer = st.selectbox(
                "Select Officer",
                options=existing_officers['id'].tolist(),
                format_func=lambda x: f"{existing_officers[existing_officers['id']==x]['name'].iloc[0]} ({existing_officers[existing_officers['id']==x]['department'].iloc[0]})"
            )

            # Only show children inputs
            num_children = st.number_input("Number of Children", min_value=1, max_value=10, value=1)
            family_data = []
            for i in range(num_children):
                st.markdown(f"### Child {i+1}")
                child_name = st.text_input(f"Child {i+1} Name", key=f"child_name_{i}")
                relation_type = st.selectbox("Relation Type", ['Son', 'Daughter'], key=f"relation_{i}")
                child_edu_location = st.selectbox(
                    "Education Location",
                    ['India', 'USA', 'UK', 'Canada', 'Australia'],
                    key=f"edu_loc_{i}"
                )
                child_university = st.text_input("University", key=f"university_{i}")
                child_degree = st.selectbox(
                    "Degree Level",
                    ['Studying', 'Bachelors', 'Masters', 'PhD'],
                    key=f"degree_{i}"
                )

                if child_name:  # Only add if name is provided
                    family_data.append({
                        'name': child_name,
                        'relation_type': relation_type,
                        'education_location': child_edu_location,
                        'university': child_university,
                        'degree_level': child_degree
                    })

            if st.form_submit_button("Add Children"):
                try:
                    add_children_to_officer(selected_officer, family_data)
                    st.success("Children added successfully!")
                    st.cache_data.clear()
                except ValueError as e:
                    st.error(str(e))
        else:
            # Original new officer form
            name = st.text_input("Officer Name")
            department = st.selectbox("Department", servants_df['department'].unique() if not servants_df.empty else ['IAS', 'IPS', 'IFS', 'IRS'])
            joining_year = st.number_input("Joining Year", min_value=2000, max_value=2024, value=2024)
            education_location = st.selectbox("Education Location", ['India', 'USA', 'UK', 'Canada', 'Australia'])
            university = st.text_input("University")
            degree_level = st.selectbox("Degree Level", ['Bachelors', 'Masters', 'PhD'])

            # Add family members section
            num_children = st.number_input("Number of Children", min_value=0, max_value=10, value=0)
            family_data = []
            if num_children > 0:
                for i in range(num_children):
                    st.markdown(f"### Child {i+1}")
                    child_name = st.text_input(f"Child {i+1} Name", key=f"child_name_{i}")
                    relation_type = st.selectbox("Relation Type", ['Son', 'Daughter'], key=f"relation_{i}")
                    child_edu_location = st.selectbox(
                        "Education Location",
                        ['India', 'USA', 'UK', 'Canada', 'Australia'],
                        key=f"edu_loc_{i}"
                    )
                    child_university = st.text_input("University", key=f"university_{i}")
                    child_degree = st.selectbox(
                        "Degree Level",
                        ['Studying', 'Bachelors', 'Masters', 'PhD'],
                        key=f"degree_{i}"
                    )

                    if child_name:  # Only add if name is provided
                        family_data.append({
                            'name': child_name,
                            'relation_type': relation_type,
                            'education_location': child_edu_location,
                            'university': child_university,
                            'degree_level': child_degree
                        })

            if st.form_submit_button("Add Officer"):
                if name:  # Basic validation
                    officer_data = {
                        'name': name,
                        'department': department,
                        'joining_year': joining_year,
                        'education_location': education_location,
                        'university': university,
                        'degree_level': degree_level
                    }
                    add_servant(officer_data, family_data)
                    st.success("Officer and family members added successfully!")
                    st.cache_data.clear()
                else:
                    st.error("Please fill in at least the officer's name.")

else:
    st.header("📝 Add New Politician or Children")

    # Option to add to existing politician
    add_to_existing = st.checkbox("Add children to existing politician")

    with st.form("new_politician_form"):
        if add_to_existing:
            # Get list of existing politicians
            existing_politicians = politicians_df[['id', 'name', 'party']].drop_duplicates()
            selected_politician = st.selectbox(
                "Select Politician",
                options=existing_politicians['id'].tolist(),
                format_func=lambda x: f"{existing_politicians[existing_politicians['id']==x]['name'].iloc[0]} ({existing_politicians[existing_politicians['id']==x]['party'].iloc[0]})"
            )

            # Only show children inputs
            num_children = st.number_input("Number of Children", min_value=1, max_value=10, value=1)
            family_data = []
            for i in range(num_children):
                st.markdown(f"### Child {i+1}")
                child_name = st.text_input(f"Child {i+1} Name", key=f"child_name_{i}")
                relation_type = st.selectbox("Relation Type", ['Son', 'Daughter'], key=f"relation_{i}")
                child_edu_location = st.selectbox(
                    "Education Location",
                    ['India', 'USA', 'UK', 'Canada', 'Australia'],
                    key=f"edu_loc_{i}"
                )
                child_university = st.text_input("University", key=f"university_{i}")
                child_degree = st.selectbox(
                    "Degree Level",
                    ['Studying', 'Bachelors', 'Masters', 'PhD'],
                    key=f"degree_{i}"
                )

                if child_name:  # Only add if name is provided
                    family_data.append({
                        'name': child_name,
                        'relation_type': relation_type,
                        'education_location': child_edu_location,
                        'university': child_university,
                        'degree_level': child_degree
                    })

            if st.form_submit_button("Add Children"):
                try:
                    add_children_to_politician(selected_politician, family_data)
                    st.success("Children added successfully!")
                    st.cache_data.clear()
                except ValueError as e:
                    st.error(str(e))
        else:
            # Original new politician form
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Politician Name")
                party = st.text_input("Party")
                position = st.selectbox("Position", ['MP', 'MLA', 'Minister', 'Chief Minister', 'Party President'])
                education_location = st.selectbox("Education Location", ['India', 'USA', 'UK', 'Canada', 'Australia'])
                university = st.text_input("University")
                degree_level = st.selectbox("Degree Level", ['High School', 'Bachelors', 'Masters', 'PhD'])

            with col2:
                num_children = st.number_input("Number of Children", min_value=0, max_value=10, value=1)

                family_data = []
                for i in range(num_children):
                    st.markdown(f"### Child {i+1}")
                    child_name = st.text_input(f"Child {i+1} Name", key=f"child_name_{i}")
                    relation_type = st.selectbox("Relation Type", ['Son', 'Daughter'], key=f"relation_{i}")
                    child_edu_location = st.selectbox(
                        "Education Location",
                        ['India', 'USA', 'UK', 'Canada', 'Australia'],
                        key=f"edu_loc_{i}"
                    )
                    child_university = st.text_input("University", key=f"university_{i}")
                    child_degree = st.selectbox(
                        "Degree Level",
                        ['Studying', 'Bachelors', 'Masters', 'PhD'],
                        key=f"degree_{i}"
                    )

                    if child_name:  # Only add if name is provided
                        family_data.append({
                            'name': child_name,
                            'relation_type': relation_type,
                            'education_location': child_edu_location,
                            'university': child_university,
                            'degree_level': child_degree
                        })

            if st.form_submit_button("Add Politician"):
                if name and party:  # Basic validation
                    # Check if politician already exists
                    existing_politician = check_politician_exists(name, party)
                    if existing_politician:
                        st.error(f"Politician {name} from {party} already exists!")
                    else:
                        politician_data = {
                            'name': name,
                            'party': party,
                            'position': position,
                            'education_location': education_location,
                            'university': university,
                            'degree_level': degree_level
                        }
                        add_politician(politician_data, family_data)
                        st.success("Politician and family members added successfully!")
                        st.cache_data.clear()
                else:
                    st.error("Please fill in at least the politician's name and party.")

# Footer
st.markdown("""
---
*Data is stored in a PostgreSQL database*
""")