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
