import streamlit as st


def apply_styles():
    st.markdown(

        """

        <style>

        /* Main app background and default text */

        .stApp {

            background: #f5f8f6;

            color: #17251d;

        }



        .main .block-container {

            max-width: 1450px;

            padding-top: 2rem;

            padding-bottom: 2.5rem;

        }



        /* Main text visibility */

        html, body, [class*="css"] {

            color: #17251d;

        }



        p, li, label, .stMarkdown, .stCaption {

            color: #26372d;

        }



        h1, h2, h3, h4, h5 {

            color: #123b27 !important;

            font-weight: 750 !important;

            letter-spacing: -0.3px;

        }



        /* Sidebar */

        [data-testid="stSidebar"] {

            background: #102e20;

            border-right: 2px solid #1d5b3b;

        }



        [data-testid="stSidebar"] * {

            color: #ffffff !important;

        }



        [data-testid="stSidebar"] hr {

            border-color: #3e6d52;

        }



        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {

            color: #ffffff;

        }



        /* Main app title */

        .main-title {

            color: #146c43;

            font-size: clamp(2rem, 4vw, 3rem);

            font-weight: 850;

            line-height: 1.2;

            letter-spacing: -1px;

            margin-bottom: 10px;

        }



        .subtitle {

            color: #45584b;

            font-size: 1.05rem;

            line-height: 1.7;

            margin-bottom: 1.5rem;

        }



        /* Cards and containers */

        [data-testid="stVerticalBlockBorderWrapper"] {

            background: #ffffff;

            border: 1px solid #d4e3d8;

            border-radius: 16px;

        }



        div[data-testid="stMetric"] {

            background: #ffffff;

            border: 1px solid #d4e3d8;

            border-left: 5px solid #198754;

            border-radius: 12px;

            padding: 18px 16px;

            box-shadow: 0 3px 10px rgba(16, 46, 32, 0.05);

        }



        [data-testid="stMetricLabel"] {

            color: #42574a !important;

            font-weight: 650 !important;

        }



        [data-testid="stMetricValue"] {

            color: #123b27 !important;

            font-weight: 800 !important;

        }



        [data-testid="stMetricDelta"] {

            color: #146c43 !important;

        }



        /* Text inputs, number inputs, select boxes */

        div[data-baseweb="input"],

        div[data-baseweb="textarea"],

        div[data-baseweb="select"] > div {

            background: #ffffff !important;

            border: 1px solid #a9c6b3 !important;

            border-radius: 9px !important;

        }



        div[data-baseweb="input"] input,

        div[data-baseweb="textarea"] textarea,

        div[data-baseweb="select"] * {

            color: #17251d !important;

            -webkit-text-fill-color: #17251d;

            background-color: transparent;

        }



        input::placeholder,

        textarea::placeholder {

            color: #68796e !important;

            -webkit-text-fill-color: #68796e !important;

            opacity: 1 !important;

        }



        div[data-baseweb="input"]:focus-within,

        div[data-baseweb="textarea"]:focus-within,

        div[data-baseweb="select"]:focus-within {

            border-color: #198754 !important;

            box-shadow: 0 0 0 2px rgba(25, 135, 84, 0.16);

        }



        /* Dropdown menu */

        [data-baseweb="popover"],

        [data-baseweb="menu"],

        [role="listbox"] {

            background: #ffffff !important;

            border: 1px solid #d4e3d8 !important;

        }



        [role="option"] {

            color: #17251d !important;

            background: #ffffff !important;

        }



        [role="option"]:hover {

            background: #e6f4eb !important;

        }



        /* Checkboxes and radio buttons */

        [data-testid="stCheckbox"] label,

        [data-testid="stRadio"] label {

            color: #17251d !important;

        }



        [data-testid="stCheckbox"] label p,

        [data-testid="stRadio"] label p {

            color: #17251d !important;

        }



        /* Buttons */

        div.stButton > button,

        div.stDownloadButton > button {

            background: #198754 !important;

            color: #ffffff !important;

            border: 1px solid #146c43 !important;

            border-radius: 10px !important;

            font-weight: 700 !important;

            padding: 0.65rem 1rem !important;

            min-height: 44px;

            transition: all 0.2s ease;

        }



        div.stButton > button *,

        div.stDownloadButton > button * {

            color: #ffffff !important;

        }



        div.stButton > button:hover,

        div.stDownloadButton > button:hover {

            background: #146c43 !important;

            border-color: #0f5132 !important;

            box-shadow: 0 4px 12px rgba(20, 108, 67, 0.2);

            transform: translateY(-1px);

        }



        div.stButton > button:focus,

        div.stDownloadButton > button:focus {

            outline: 3px solid #9ed5b4 !important;

            outline-offset: 2px;

        }



        /* Progress bar */

        [data-testid="stProgressBar"] > div {

            background: #dcebe1;

            border-radius: 10px;

        }



        [data-testid="stProgressBar"] > div > div {

            background: #198754 !important;

            border-radius: 10px;

        }



        /* Information, success, warning, and error messages */

        [data-testid="stAlert"] {

            border-radius: 10px;

            border: 1px solid #d4e3d8;

        }



        [data-testid="stAlert"] p {

            color: #17251d !important;

        }



        /* Data tables */

        [data-testid="stDataFrame"] {

            border: 1px solid #d4e3d8;

            border-radius: 10px;

            overflow: hidden;

            background: #ffffff;

        }



        [data-testid="stDataFrame"] * {

            --gdg-bg-cell: #ffffff;

            --gdg-bg-cell-medium: #f1f7f3;

            --gdg-text-dark: #17251d;

            --gdg-text-medium: #34483a;

            --gdg-border-color: #d4e3d8;

        }



        /* Charts and captions */

        [data-testid="stCaptionContainer"] p {

            color: #52665a !important;

        }



        /* Dividers */

        hr {

            border-color: #d4e3d8 !important;

        }



        /* Slider */

        [data-testid="stSlider"] [role="slider"] {

            background: #198754 !important;

            border-color: #146c43 !important;

        }



        /* Footer */

        .app-footer {

            text-align: center;

            color: #52665a;

            font-size: 0.9rem;

            padding: 18px 0;

            border-top: 1px solid #d4e3d8;

            margin-top: 20px;

        }



        /* Responsive spacing */

        @media (max-width: 768px) {

            .main .block-container {

                padding: 1rem 1rem 2rem 1rem;

            }



            .main-title {

                font-size: 2rem;

            }



            .subtitle {

                font-size: 0.95rem;

            }

        }

        </style>

        """,

        unsafe_allow_html=True,

    )
