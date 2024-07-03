import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="TB Dashboard", layout="wide")

def load_data():
    df = pd.read_excel('afr_data.xlsx')
    return df

df = load_data()

if pd.api.types.is_datetime64_any_dtype(df['year']):
    df['year'] = df['year'].dt.year

st.title('Tuberculosis Statistics in Africa')

st.sidebar.header('INFORMATION')
st.sidebar.write('Tuberculosis (TB) is an infectious disease caused by the bacterium Mycobacterium tuberculosis. It primarily affects the lungs but can also impact other parts of the body. TB spreads through the air when a person with the active disease cough, sneezes, or talks.')
st.sidebar.write('Africa bears a significant burden of TB, with many countries in sub-Saharan Africa experiencing extremely high infection rates. Co-infection with HIV is a major issue, as individuals with HIV are more susceptible to TB due to their weakened immune system.')
st.sidebar.write('Diagnostic and treatment challenges are prevalent across the continent. Late diagnosis often occurs due to limited access to healthcare services and diagnostic facilities. Treatment is complicated by issues such as drug-resistant TB (MDR-TB) and the more severe extensively drug-resistant TB (XDR-TB) add complexity and cost to treatment protocols.')
st.sidebar.write('Through the combined effort of governments, international organizations, and communities, there is hope for reducing the TB burden in Africa and improving overall public health.')

col1, col2 = st.columns(2)

with col1:
    map_option = st.selectbox(
        'Choose the map you want to display',
        ('Total Population Map', 'Estimated TB Prevalence Map')
    )

with col2:
    selected_year = st.selectbox('Choose year', sorted(df['year_only'].unique()))

filtered_data_year = df[df['year_only'] == selected_year]

left_column, right_column = st.columns([3, 1])

def plot_map(column, title):
    fig = px.choropleth(
        filtered_data_year,
        locations='country',
        locationmode='country names',
        color=column,
        hover_name='country',
        color_continuous_scale='Blues',
        title=f'{title} in Africa ({selected_year})',
        range_color=(filtered_data_year[column].min(), filtered_data_year[column].max())
    )
    fig.update_geos(scope='africa', bgcolor='rgba(0,0,0,0)')
    fig.update_layout(
        title_font_size=18,
        title_font_color='blue',
        height=800,
        width=1200
    )
    return fig

with left_column:
    if map_option == 'Total Population Map':
        fig_pop = plot_map('estimated_population', 'Estimated Total of  Population')
        st.plotly_chart(fig_pop)
    elif map_option == 'Estimated TB Prevalence Map':
        fig_tb = plot_map('tb_prevalence', 'Estimated Prevalence')
        st.plotly_chart(fig_tb)

def display_total_tb_incidents(year):
    total_tb_incidents = df[df['year_only'] == year]['tb_incident'].sum()
    previous_year = year - 1
    percentage_increase = None
    
    if previous_year in df['year_only'].values:
        previous_tb_incidents = df[df['year_only'] == previous_year]['tb_incident'].sum()
        if previous_tb_incidents > 0:
            percentage_increase = ((total_tb_incidents - previous_tb_incidents) / previous_tb_incidents) * 100

    return total_tb_incidents, percentage_increase

def display_tb_prevalence(year):
    tb_prevalence = df[df['year_only'] == year]['tb_prevalence'].sum()
    previous_year = year - 1
    percentage_increase = None
    
    if previous_year in df['year_only'].values:
        previous_tb_prevalence = df[df['year_only'] == previous_year]['tb_prevalence'].sum()
        if previous_tb_prevalence > 0:
            percentage_increase = ((tb_prevalence - previous_tb_prevalence) / previous_tb_prevalence) * 100

    return tb_prevalence, percentage_increase

def format_percentage_change(percentage):
    if percentage is not None:
        if percentage > 0:
            return f"<span style='color:green'>↑ {percentage:.2f}%</span>"
        elif percentage < 0:
            return f"<span style='color:red'>↓ {abs(percentage):.2f}%</span>"
    return "No data found from previous year."

with right_column:
    total_tb_incidents, tb_incidents_increase = display_total_tb_incidents(selected_year)
    with st.expander(f'Total of TB Cases in {selected_year}', expanded=True):
        st.markdown(f"<span style='font-size:24px; font-weight:bold;'>{total_tb_incidents:,}</span>", unsafe_allow_html=True)
        st.write(format_percentage_change(tb_incidents_increase), unsafe_allow_html=True)
    
    tb_prevalence, tb_prevalence_increase = display_tb_prevalence(selected_year)
    with st.expander(f'Total of Prevalence in {selected_year}', expanded=True):
        st.markdown(f"<span style='font-size:24px; font-weight:bold;'>{tb_prevalence:,}</span>", unsafe_allow_html=True)
        st.write(format_percentage_change(tb_prevalence_increase), unsafe_allow_html=True)

    st.subheader(f'Top 5 Country with The Most Cases in {selected_year}')
    top_countries_tb_incidents = filtered_data_year.sort_values(by='tb_incident', ascending=False).head(5)[['country', 'tb_incident']]
    top_countries_tb_incidents.columns = ['country', 'total of cases']
    st.table(top_countries_tb_incidents.set_index('country').style.format("{:,}"))

selected_country = st.selectbox('Choose Country', df['country'].unique())
selected_year_range = st.slider('Choose Year Range', min_value=int(df['year'].min()), max_value=int(df['year'].max()), value=(int(df['year'].min()), int(df['year'].max())))

filtered_data = df[(df['country'] == selected_country) & (df['year'].between(*selected_year_range))]

col1, col2, col3 = st.columns(3)

with col1:
    fig_line = px.line(filtered_data, x='year', y='tb_prevalence', color='country',
                       labels={'tb_prevalence': 'TB Prevalence'},
                       color_discrete_sequence=px.colors.qualitative.Pastel)
    with st.expander('Line Chart of TB Prevalence', expanded=True):
        st.plotly_chart(fig_line)

with col2:
    pie_data_year_range = filtered_data[['year', 'tb_deaths', 'tb_hiv_deaths']]
    pie_data_year_range = pie_data_year_range.melt(id_vars=['year'], value_vars=['tb_deaths', 'tb_hiv_deaths'],
                                                   var_name='Category', value_name='Count')
    pie_data_year_range['Category'] = pie_data_year_range['Category'].replace({
        'tb_deaths': 'Without HIV',
        'tb_hiv_deaths': 'With HIV'
    })
    pie_fig_year_range = px.pie(pie_data_year_range, values='Count', names='Category',
                                color_discrete_sequence=px.colors.qualitative.Pastel)
    with st.expander('Distribution of TB Number of Deaths.', expanded=True):
        st.plotly_chart(pie_fig_year_range)

# Display TB and TB-HIV Mortality by Country over selected year range in the right column
with col3:
    bar_fig = px.bar(filtered_data, x='year', y=['tb_mortality', 'tb_hiv_mortality'],
                     barmode='group', labels={'value':'Mortality', 'variable':'Type'},
                     color_discrete_sequence=px.colors.qualitative.Pastel)  # Using pastel colors
    # Update the layout to move the legend
    bar_fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )
    with st.expander('TB and TB-HIV Mortality', expanded=True):
        st.plotly_chart(bar_fig)