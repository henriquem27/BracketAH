import streamlit as st

def load_css():
    st.markdown("""
        <style>
        /* --- GLOBAL THEME --- */
        .stApp { 
            background-color: #18191a; /* Darker background like Challonge */
            color: #e4e6eb;
        }
        .block-container { 
            padding-top: 1rem; 
            padding-left: 2rem; 
            padding-right: 2rem; 
            max-width: 100%;
        }

        /* --- BRACKET CARD --- */
        .match-card {
            background-color: #242526;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.5);
            margin-bottom: 0px; /* Spacing handled by Python spacers now */
            position: relative;
            border: 1px solid #3a3b3c;
            font-family: 'Roboto', sans-serif;
            font-size: 14px;
        }

        /* --- PLAYER ROW --- */
        .player-row {
            display: flex;
            justify-content: space-between; /* Pushes Name to left, Box to right */
            align-items: center;
            padding: 0;
            height: 30px;
        }
        
        /* The Name Text */
        .player-name {
            padding-left: 10px;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 130px;
        }

        /* The Checkbox/Score Box */
        .score-box {
            width: 30px;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            border-left: 1px solid #3a3b3c;
            font-weight: bold;
        }

        /* WINNER STYLES */
        .winner-row {
            background-color: #242526; /* Row background stays dark */
        }
        .winner-text {
            color: #fff; /* Highlight name text */
        }
        .winner-box {
            background-color: #f47920; /* ORANGE BOX */
            color: white;
        }

        /* DIVIDER */
        .divider {
            height: 1px;
            background-color: #3a3b3c;
        }

        /* --- CONNECTORS (The Lines) --- */
        /* This draws a line to the right of the card */
        .connector-r {
            position: absolute;
            top: 50%;
            right: -20px;
            width: 20px;
            height: 2px;
            background-color: #555;
            z-index: 0;
        }
        /* Vertical line for the 'bracket' shape - applied to specific cards via Python */
        .bracket-arm-top {
            position: absolute;
            right: -20px;
            top: 50%;
            height: 50%; /* Goes down */
            width: 2px;
            border-right: 2px solid #555;
        }
        .bracket-arm-bottom {
            position: absolute;
            right: -20px;
            top: 0;
            height: 50%; /* Goes up */
            width: 2px;
            border-right: 2px solid #555;
        }

        /* HEADERS */
        h1, h2, h3, h4 { color: #b0b3b8 !important; font-size: 1.2rem; text-align: center; }
        </style>
    """, unsafe_allow_html=True)