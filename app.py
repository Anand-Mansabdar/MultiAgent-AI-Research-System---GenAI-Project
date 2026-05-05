import streamlit as st
from agents import build_search_agent, build_scrape_agent, writer_chain, critic_chain

ACCENT_COLOR = "#1E90FF"
ROSE_COLOR = "#FF66B2"

st.set_page_config(
    page_title="MultiAgent AI Research System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
    <style>
    .main-header {{ color: {ACCENT_COLOR}; font-size: 3rem; font-weight: 900; letter-spacing: -0.03em; }}
    .website-name {{ color: {ROSE_COLOR}; font-size: 1.35rem; font-weight: 700; margin-top: 6px; }}
    .section-header {{ color: {ROSE_COLOR}; }}
    .step-card {{ border-radius: 18px; padding: 18px; margin-bottom: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }}
    .step-label {{ font-size: 1rem; font-weight: 700; margin-bottom: 6px; }}
    .step-status {{ font-size: 0.95rem; font-weight: 700; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-header">ResearchFlow AI</div>', unsafe_allow_html=True)
st.markdown('<div class="website-name">MultiAgent AI Research System — intelligent research, scraping, writing, and critique</div>', unsafe_allow_html=True)
st.markdown(
    """
    <p style='font-size:1.05rem; color:#333333;'>
    Launch a beautiful research workflow with search, scraping, report composition, and critique. Use the step tracker to follow the pipeline as it advances from ready to completed.
    </p>
    """,
    unsafe_allow_html=True,
)

if "pipeline_status" not in st.session_state:
    st.session_state.pipeline_status = [False, False, False, False]
    st.session_state.pipeline_started = False

if "result" not in st.session_state:
    st.session_state.result = None

if "pipeline_started" not in st.session_state:
    st.session_state.pipeline_started = False

steps = [
    "Search agent active",
    "Scraping agent active",
    "Writer chain drafting report",
    "Critic chain reviewing report",
]


def render_step(step_name: str, completed: bool, started: bool) -> str:
    if not started:
        status_color = "#888888"
        background = "rgba(136, 136, 136, 0.08)"
        icon = "⚪"
        step_text = "Ready"
    elif completed:
        status_color = "#34C759"
        background = "rgba(52, 199, 89, 0.09)"
        icon = "✅"
        step_text = "Completed"
    else:
        status_color = "#FF4B4B"
        background = "rgba(255, 75, 75, 0.1)"
        icon = "⏳"
        step_text = "Pending"

    return (
        f"<div class='step-card' style='background:{background}; border: 1px solid {status_color};'>"
        f"<div class='step-label'>{step_name}</div>"
        f"<div class='step-status' style='color:{status_color};'>{icon} {step_text}</div>"
        f"</div>"
    )


def update_pipeline_status(index: int):
    status = [False, False, False, False]
    for i in range(index + 1):
        status[i] = True
    st.session_state.pipeline_status = status


def execute_research_pipeline_ui(topic: str) -> dict:
    state = {}

    st.session_state.pipeline_started = True
    st.session_state.pipeline_status = [False, False, False, False]

    with st.spinner("Running search agent..."):
        search_agent = build_search_agent()
        search_agent_result = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
        })
        state["search_results"] = search_agent_result["messages"][-1].content
        if isinstance(state["search_results"], list):
            state["search_results"] = "".join([item["text"] for item in state["search_results"] if item.get("type") == "text"])
        update_pipeline_status(0)

    with st.spinner("Running scraping agent..."):
        scrape_agent = build_scrape_agent()
        scrape_agent_result = scrape_agent.invoke({
            "messages": [
                (
                    "user",
                    f"Based on the following search results about '{topic}', pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{state['search_results'][:800]}"
                )
            ]
        })
        state["scrape_content"] = scrape_agent_result["messages"][-1].content
        update_pipeline_status(1)

    with st.spinner("Drafting the report..."):
        combined_research = (
            f"SEARCH RESULTS : \n {state['search_results']} \n\n",
            f"SCRAPED CONTENT : \n {state['scrape_content']} \n\n",
        )
        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": combined_research,
        })
        update_pipeline_status(2)

    with st.spinner("Creating critic review..."):
        state["critic_report"] = critic_chain.invoke({
            "report": state["report"]
        })
        update_pipeline_status(3)

    return state

with st.sidebar:
    st.header("How it works")
    st.markdown(
        """
        1. **Search agent** finds recent, reliable information on your topic.
        2. **Scraping agent** extracts deeper content from a relevant web page.
        3. **Writer chain** composes a structured research report.
        4. **Critic chain** evaluates the report and provides honest feedback.
        """
    )
    st.markdown("---")
    st.markdown(
        f"<div style='color:{ROSE_COLOR}; font-weight:700;'>Pro Tip</div>\n"
        "Use focused research topics and watch the progress tracker update in real time."
        , unsafe_allow_html=True
    )

col1, col2 = st.columns([2, 1])
with col1:
    topic = st.text_area(
        "Research Topic",
        value="Recent advances in open source AI research ecosystems",
        height=150,
        help="Enter the topic you want the research pipeline to explore.",
    )
    run_pipeline = st.button("Run Research Pipeline", key="run_pipeline")

with col2:
    st.markdown(f"<div class='section-header'>Live Progress</div>", unsafe_allow_html=True)
    for idx, step_name in enumerate(steps):
        st.markdown(
            render_step(step_name, st.session_state.pipeline_status[idx], st.session_state.pipeline_started),
            unsafe_allow_html=True,
        )
    st.markdown("---")
    st.markdown("### Example prompts")
    st.write("• Latest trends in AI safety and alignment")
    st.write("• Market analysis for autonomous vehicles")
    st.write("• Research summary on climate change adaptation")

if run_pipeline:
    if not topic.strip():
        st.warning("Please enter a topic before running the pipeline.")
    else:
        st.session_state.result = None
        try:
            st.session_state.result = execute_research_pipeline_ui(topic=topic.strip())
        except Exception as exc:
            st.session_state.pipeline_status = [False, False, False, False]
            st.session_state.pipeline_started = False
            st.error("An error occurred while executing the pipeline.")
            st.exception(exc)

st.markdown("---")

if st.session_state.result:
    result = st.session_state.result
    st.subheader("Pipeline Output")
    st.markdown("<div style='font-size:1rem; color:#333333;'>Expand each stage to review the outputs from the agents and writer.</div>", unsafe_allow_html=True)

    with st.expander("Search Agent Output", expanded=True):
        st.write(result["search_results"])
    with st.expander("Scraping Agent Output", expanded=False):
        st.write(result["scrape_content"])
    with st.expander("Research Report", expanded=True):
        st.write(result["report"])
    with st.expander("Critic Review", expanded=False):
        st.write(result["critic_report"])

    st.markdown("---")
    st.markdown(
        f"<div class='section-header'>Research Pipeline Summary</div>",
        unsafe_allow_html=True,
    )
    st.write(
        "This dashboard executed all pipeline stages using the pipeline logic inside the UI. The step tracker above shows each stage as completed in green once finished."
    )
else:
    st.markdown("<div style='color:#555; font-size:1rem;'>Enter a topic and click <strong>Run Research Pipeline</strong> to start the flow.</div>", unsafe_allow_html=True)
