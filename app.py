import os
import streamlit as st
import opengradient as og

st.set_page_config(page_title="Whitepaper Simplifier (OpenGradient)", page_icon="🧠", layout="centered")

st.title("🧠 AI Whitepaper Simplifier (Powered by OpenGradient)")
st.caption("Paste a crypto/AI whitepaper section and get a clean summary, glossary, and risk notes.")

OG_PRIVATE_KEY = os.getenv("OG_PRIVATE_KEY")
if not OG_PRIVATE_KEY:
    st.warning("Missing OG_PRIVATE_KEY. Add it in Replit Secrets (lock icon).")
    st.stop()

client = og.Client(private_key=OG_PRIVATE_KEY)

# Permit2 approval (only transacts if needed)
with st.spinner("Checking $OPG Permit2 approval..."):
    try:
        # Approve at least 2 OPG for Permit2 spending (only sends tx if allowance is too low)
        client.llm.ensure_opg_approval(opg_amount=2.0)
    except Exception as e:
        st.error(f"Approval failed: {e}")
        st.info("Make sure you have Base Sepolia ETH for gas + $OPG tokens in the wallet.")
        st.stop()

whitepaper_text = st.text_area(
    "Paste whitepaper text here (try 1–4 pages):",
    height=240,
    placeholder="Paste tokenomics / architecture / roadmap section here..."
)

tone = st.selectbox("Output style:", ["Beginner-friendly", "Investor-friendly", "Technical but clear"])
audience = st.selectbox("Audience:", ["General public", "Crypto natives", "Builders/devs"])

col1, col2 = st.columns(2)
with col1:
    max_tokens = st.slider("Output length", 300, 1400, 900, 50)
with col2:
    temperature = st.slider("Creativity", 0.0, 1.0, 0.2, 0.05)

run = st.button("Simplify ✨", use_container_width=True)

if run:
    if len(whitepaper_text.strip()) < 200:
        st.error("Paste more content (at least a few paragraphs).")
        st.stop()

    system = "You simplify crypto/AI whitepapers accurately and clearly. No hype. No fake claims."
    user_prompt = f"""
STYLE: {tone}
AUDIENCE: {audience}

Return in this format:

1) Plain-English Summary (5–10 bullets)
2) What problem it solves (2–4 bullets)
3) How it works (5–10 bullets, concrete)
4) Token / Incentives (if mentioned) (bullets)
5) Risks / Red flags (5–10 bullets, fair & specific)
6) Glossary (10–20 terms with simple definitions)
7) 3 smart questions to ask the team (bullets)

WHITEPAPER TEXT:
\"\"\"{whitepaper_text}\"\"\"
"""

    with st.spinner("Running verified inference on OpenGradient..."):
        try:
            result = client.llm.chat(
                model=og.TEE_LLM.GPT_4O,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=int(max_tokens),
                temperature=float(temperature),
            )

            output = result.chat_output["content"]
            payment_hash = getattr(result, "payment_hash", None)

            st.success("Done ✅")
            st.markdown(output)

            if payment_hash:
                st.caption(f"Payment hash: {payment_hash}")

        except Exception as e:
            st.error(f"Inference failed: {e}")
            st.info("If this fails, double-check: wallet has $OPG on Base Sepolia + enough Base Sepolia ETH for gas.")
