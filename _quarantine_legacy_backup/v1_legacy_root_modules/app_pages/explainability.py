import streamlit as st
import pandas as pd
import plotly.express as px

def app():
    st.title("Explainability (SHAP)")
    st.markdown("Understand **WHY** the model made its prediction.")

    if 'last_prediction' not in st.session_state:
        st.info("No recent prediction found. Please go to the 'Predict Risk' page first.")
        return

    result = st.session_state['last_prediction']
    
    st.subheader("Last Prediction Summary")
    st.write(f"**Risk Tier:** {result['risk_tier']}")
    st.write(f"**Probability:** {result['probability']:.1%}")
    
    st.markdown("---")
    st.subheader("Factors Influencing this Prediction")
    st.markdown("The chart below shows how each feature pushed the model's prediction higher (At-Risk) or lower (Not At-Risk).")

    # Construct dataframe for Plotly waterfall or bar chart
    factors = []
    for f in result.get('risk_factors', []):
        factors.append({"Feature": f["feature"], "Contribution": f["value"], "Type": "Increased Risk"})
    for f in result.get('protective_factors', []):
        factors.append({"Feature": f["feature"], "Contribution": f["value"], "Type": "Decreased Risk"})

    if factors:
        df = pd.DataFrame(factors)
        df = df.sort_values(by="Contribution", ascending=True)
        
        fig = px.bar(
            df, 
            y="Feature", 
            x="Contribution", 
            color="Type",
            color_discrete_map={"Increased Risk": "#ff4b4b", "Decreased Risk": "#00cc96"},
            orientation='h',
            title="Local SHAP Explanation"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Plain-English Explanation")
        for f in result.get('risk_factors', []):
            st.write(f"- **{f['feature']}** contributed positively to the model's predicted risk.")
        for f in result.get('protective_factors', []):
            st.write(f"- **{f['feature']}** contributed negatively to the model's predicted risk, acting as a protective factor.")
    else:
        st.write("No SHAP values available for this prediction.")
