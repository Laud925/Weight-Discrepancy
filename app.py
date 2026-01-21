import pandas as pd
import streamlit as st

from logic import invoice_allowed_band, target_band_for_new_invoice_from_gr, run_analysis

st.title("📦 Weight Discrepancy Checker")
st.markdown(
    "<p style='color:#cccccc;'>"
    "Pre-check calculator used to determine whether a weight discrepancy exists "
    "before uploading documents."
    "</p>",
    unsafe_allow_html=True
)

gr_val = st.number_input("GR (kg):", min_value=0.0, value=0.0, step=0.1)
inv_val = st.number_input("Invoice (kg):", min_value=0.0, value=0.0, step=0.1)

calc = st.button("Calculate")

if calc:
    if gr_val <= 0 or inv_val <= 0:
        st.error("⚠️ Enter values > 0 for GR and Invoice.")
    else:
        low_allowed, high_allowed = invoice_allowed_band(inv_val)
        in_tol = (low_allowed <= gr_val <= high_allowed)

        target_low, target_high = target_band_for_new_invoice_from_gr(gr_val)

        st.markdown(
            "<div style='padding:10px;border:1px solid #ddd;border-radius:8px;'>"
            "<h3 style='margin:0;color:#c00000;'>Weight discrepancy</h3>"
            "<div style='margin-top:6px;'><b>Tolerancia:</b> ±10% (banda permitida sobre el total de la invoice)</div>"
            "</div>",
            unsafe_allow_html=True
        )

        df_main = pd.DataFrame([{
            "-10.00% (LOW)": round(low_allowed, 3),
            "Commercial invoice weight -->": round(inv_val, 2),
            "+10.00% (HIGH)": round(high_allowed, 3),
            "enter GXD weight here -->": round(gr_val, 2),
        }])
        st.dataframe(df_main, use_container_width=True)

        st.markdown(
            "<div style='margin-top:10px;padding:10px;border:1px solid #ddd;border-radius:8px;'>"
            "<b>Target band para el NUEVO total de Invoice (basado en GR):</b><br>"
            "Si hay discrepancy, el ajuste buscará que el nuevo total de la factura quede dentro de este rango."
            "</div>",
            unsafe_allow_html=True
        )

        df_target = pd.DataFrame([{
            "Target NEW Invoice LOW (GR/1.10)": round(target_low, 3),
            "Target NEW Invoice HIGH (GR/0.90)": round(target_high, 3),
        }])
        st.dataframe(df_target, use_container_width=True)

        if in_tol:
            st.markdown(
                "<div style='margin-top:10px;padding:10px;border-radius:8px;"
                "background:#e7f7e7;border:1px solid #6bbf6b;'>"
                "<b style='color:#1b5e20'>✅ NO hay weight discrepancy.</b><br>"
                "No necesitas subir documentos."
                "</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div style='margin-top:10px;padding:10px;border-radius:8px;"
                "background:#fff4e5;border:1px solid #ffb74d;'>"
                "<b style='color:#e65100'>⚠️ SÍ hay weight discrepancy.</b><br>"
                "Si quieres, sube los PDFs para hacer la corrección (se ajusta la factura)."
                "</div>",
                unsafe_allow_html=True
            )

uploaded_files = st.file_uploader(
    "Upload the shipment PDF files (1 GR + 1 or more invoices)."
    " The system will automatically check for discrepancies.",
    type=["pdf"],
    accept_multiple_files=True
)

run_btn = st.button("🔎 Run Analysis")

if run_btn:
    if not uploaded_files or len(uploaded_files) < 2:
        st.error("⚠️ You must upload at least 2 PDFs: 1 GR and 1 or more invoices.")
    else:
        uploaded = {f.name: f.read() for f in uploaded_files}

        with st.spinner("Analyzing PDFs, please wait…"):
            summary, df_full, df_adjusted, validation_df = run_analysis(uploaded, tol=0.10)

        st.success("✅ Analysis completed")

        st.subheader("📊 Shipment summary")
        st.caption(
        st.dataframe(summary, use_container_width=True)

        st.subheader("📦 Full table (CAT)")
        st.dataframe(df_full, use_container_width=True)

        st.write(f"🔹 Sum of NEW WEIGHT lbs: {round(df_full['NEW WEIGHT lbs'].sum(), 2)} lbs")
        st.write(f"🔹 Sum of NEW WEIGHT kgs: {round(df_full['NEW WEIGHT kgs'].sum(), 2)} kg")

        st.subheader("📦 Adjusted pieces only (CAT)")
        st.dataframe(df_adjusted, use_container_width=True)

        if validation_df is not None:
            st.subheader("📊 Validation – Invoice vs GR vs New Weight")
            st.dataframe(validation_df, use_container_width=True)










