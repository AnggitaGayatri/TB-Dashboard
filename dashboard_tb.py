import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="TB Dashboard", layout="wide")

# Function to load data from dataset
def load_data():
    df = pd.read_excel('afr_data.xlsx')  # Adjust filename as per your dataset
    return df

# Load data
df = load_data()

# Convert 'year' column to int if it's in Timestamp format
if pd.api.types.is_datetime64_any_dtype(df['year']):
    df['year'] = df['year'].dt.year

# Streamlit application title
st.title('Potret Statistik TB di Benua Afrika')

# Sidebar for informational text
st.sidebar.header('INFORMATION')
st.sidebar.write('Tuberculosis (TB) is an infectious disease caused by the bacterium Mycobacterium tuberculosis. It primarily affects the lungs but can also impact other parts of the body. TB spreads through the air when a person with the active disease cough, sneezes, or talks.')
st.sidebar.write('Africa bears a significant burden of TB, with many countries in sub-Saharan Africa experiencing extremely high infection rates. Co-infection with HIV is a major issue, as individuals with HIV are more susceptible to TB due to their weakened immune system.')
st.sidebar.write('Diagnostic and treatment challenges are prevalent across the continent. Late diagnosis often occurs due to limited access to healthcare services and diagnostic facilities. Treatment is complicated by issues such as drug-resistant TB (MDR-TB) and the more severe extensively drug-resistant TB (XDR-TB) add complexity and cost to treatment protocols.')
st.sidebar.write('Through the combined effort of governments, international organizations, and communities, there is hope for reducing the TB burden in Africa and improving overall public health.')

# Filters at the top of the app
col1, col2 = st.columns(2)

with col1:
    # Dropdown for selecting maps
    map_option = st.selectbox(
        'Pilih peta yang ingin ditampilkan',
        ('Total Population Map', 'Estimated TB Prevalence Map')
    )

with col2:
    # Dropdown for selecting year
    selected_year = st.selectbox('Pilih Tahun', sorted(df['year_only'].unique()))

# Filter data by selected year
filtered_data_year = df[df['year_only'] == selected_year]

# Layout with columns
left_column, right_column = st.columns([3, 1])

# Plotting the maps with consistent color scheme
def plot_map(column, title):
    fig = px.choropleth(
        filtered_data_year,
        locations='country',
        locationmode='country names',
        color=column,
        hover_name='country',
        color_continuous_scale='Blues',  # Changed to a pastel-like palette
        title=f'{title} di Afrika ({selected_year})',
        range_color=(filtered_data_year[column].min(), filtered_data_year[column].max())
    )
    fig.update_geos(scope='africa', bgcolor='rgba(0,0,0,0)')
    fig.update_layout(
        title_font_size=18,
        title_font_color='blue',
        height=800,  # Adjust height as needed
        width=1200    # Adjust width as needed
    )
    return fig

# Display maps in the left column
with left_column:
    if map_option == 'Total Population Map':
        fig_pop = plot_map('estimated_population', 'Estimasi Total Populasi')
        st.plotly_chart(fig_pop)
    elif map_option == 'Estimated TB Prevalence Map':
        fig_tb = plot_map('tb_prevalence', 'Prevalensi TB yang Diperkirakan')
        st.plotly_chart(fig_tb)

# Display total TB incidents for the selected year as text
def display_total_tb_incidents(year):
    total_tb_incidents = df[df['year_only'] == year]['tb_incident'].sum()
    previous_year = year - 1
    percentage_increase = None
    
    if previous_year in df['year_only'].values:
        previous_tb_incidents = df[df['year_only'] == previous_year]['tb_incident'].sum()
        if previous_tb_incidents > 0:
            percentage_increase = ((total_tb_incidents - previous_tb_incidents) / previous_tb_incidents) * 100

    return total_tb_incidents, percentage_increase

# Display TB prevalence for the selected year as text
def display_tb_prevalence(year):
    tb_prevalence = df[df['year_only'] == year]['tb_prevalence'].sum()
    previous_year = year - 1
    percentage_increase = None
    
    if previous_year in df['year_only'].values:
        previous_tb_prevalence = df[df['year_only'] == previous_year]['tb_prevalence'].sum()
        if previous_tb_prevalence > 0:
            percentage_increase = ((tb_prevalence - previous_tb_prevalence) / previous_tb_prevalence) * 100

    return tb_prevalence, percentage_increase

# Function to format percentage change with arrows and color
def format_percentage_change(percentage):
    if percentage is not None:
        if percentage > 0:
            return f"<span style='color:green'>↑ {percentage:.2f}%</span>"
        elif percentage < 0:
            return f"<span style='color:red'>↓ {abs(percentage):.2f}%</span>"
    return "Data tahun sebelumnya tidak tersedia."

# Create layout for TB incidents and TB prevalence
with right_column:
    # Display Total Kejadian TB
    total_tb_incidents, tb_incidents_increase = display_total_tb_incidents(selected_year)
    with st.expander(f'Total Kejadian TB pada {selected_year}', expanded=True):
        st.markdown(f"<span style='font-size:24px; font-weight:bold;'>{total_tb_incidents:,}</span>", unsafe_allow_html=True)
        st.write(format_percentage_change(tb_incidents_increase), unsafe_allow_html=True)
    
    # Display TB Prevalence
    tb_prevalence, tb_prevalence_increase = display_tb_prevalence(selected_year)
    with st.expander(f'Total Prevalensi TB pada {selected_year}', expanded=True):
        st.markdown(f"<span style='font-size:24px; font-weight:bold;'>{tb_prevalence:,}</span>", unsafe_allow_html=True)
        st.write(format_percentage_change(tb_prevalence_increase), unsafe_allow_html=True)

    # Display top 5 countries with highest TB incidents based on selected year
    st.subheader(f'Top 5 Negara dengan TB Terbanyak pada {selected_year}')
    top_countries_tb_incidents = filtered_data_year.sort_values(by='tb_incident', ascending=False).head(5)[['country', 'tb_incident']]
    top_countries_tb_incidents.columns = ['negara', 'jumlah insiden']  # Rename columns
    st.table(top_countries_tb_incidents.set_index('negara').style.format("{:,}"))

    # Filter data based on selection
selected_country = st.selectbox('Pilih Negara', df['country'].unique())
selected_year_range = st.slider('Pilih Rentang Tahun', min_value=int(df['year'].min()), max_value=int(df['year'].max()), value=(int(df['year'].min()), int(df['year'].max())))

# Filter data based on selection
filtered_data = df[(df['country'] == selected_country) & (df['year'].between(*selected_year_range))]

# Display Line Chart of TB Prevalence and Bar Plot of TB Deaths in columns
col1, col2, col3 = st.columns(3)

with col1:
    fig_line = px.line(filtered_data, x='year', y='tb_prevalence', color='country',
                       labels={'tb_prevalence': 'TB Prevalence'},
                       color_discrete_sequence=px.colors.qualitative.Pastel)  # Using pastel colors
    with st.expander('Line Chart of TB Prevalence', expanded=True):
        st.plotly_chart(fig_line)
