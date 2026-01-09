import streamlit as st
import base64
import random
import os

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

def set_bg_hack(main_bg):
    '''
    A function to unpack an image from root folder and set as bg.
    The bg will be static and strictly lower than other objects
    '''
    bin_str = get_base64_of_bin_file(main_bg)
    if bin_str:
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)

LOCATIONS = {
    "Iki Island": {
        "description": "A hidden gem in the Tsushima Strait, known for its pristine beaches, fresh uni (sea urchin), and ancient shrines.",
        "detail_text": "Iki Island allows you to disconnect from the modern world. Visit the Monkey Rock for a sunset view that defies belief, or walk through the Kojima Shrine during low tide when the path is revealed. The seafood here is legendary—specifically the Uni (sea urchin) and Iki beef.",
        "image": "assets/iki_hero.png",
        "gallery": ["assets/iki_hero.png"], # In real app, would have multiple diff images
        "highlights": ["Saruiwa (Monkey Rock)", "Kojima Shrine", "Tatsunoshima Beach"],
        "price": "¥15,000 / night",
        "rating": 4.8
    },
    "Yakushima": {
        "description": "An ancient island forest covered in cedar trees and moss. Inspiration for Studio Ghibli's Princess Mononoke.",
        "detail_text": "Yakushima is a wonderland for hikers and nature studiers. The Jomon Sugi, a cedar tree estimated to be up to 7,000 years old, awaits those willing to trek. The moss-covered rocks and misty atmosphere make you feel like you've stepped into another world.",
        "image": "assets/yakushima_hero.png",
        "gallery": ["assets/yakushima_hero.png"],
        "highlights": ["Jomon Sugi", "Shiratani Unsuikyo", "Sea Turtle nesting"],
        "price": "¥22,000 / night",
        "rating": 4.9
    },
    "Shirakawa-go": {
        "description": "A UNESCO World Heritage site famous for its traditional gassho-zukuri farmhouses.",
        "detail_text": "Step back in time at Shirakawa-go. These traditional farmhouses are built to withstand heavy snowfall. In winter, the village is illuminated, creating a fairytale-like scene. Stay in a minshuku (family-run guesthouse) for a truly authentic experience.",
        "image": "assets/shirakawa_hero.png", 
        "gallery": ["assets/shirakawa_hero.png"],
        "highlights": ["Wada House", "Shiroyama Viewpoint", "Doburoku Festival"],
        "price": "¥30,000 / night",
        "rating": 4.7
    },
    "Iya Valley": {
        "description": "A remote, mountainous valley in Tokushima Prefecture, known for its vine bridges and dramatic gorges.",
        "detail_text": "One of Japan's Three Hidden Regions. The vine bridges (Kazurabashi) were originally created by samurai refugees to be easily cut down if enemies approached. Today, they offer a thrilling crossing over the river below.",
        "image": "assets/iya_valley_hero.png",
        "gallery": ["assets/iya_valley_hero.png"],
        "highlights": ["Kazurabashi Bridge", "Oboke Gorge", "Scarecrow Village"],
        "price": "¥18,000 / night",
        "rating": 4.6
    }
}

COMMENTS = [
    "Absolutely breathtaking! The nature was untouched.",
    "Best food I've ever had. unique local ingredients.",
    "A bit hard to get to, but totally worth the journey.",
    "The people were so welcoming. Felt like home.",
    "Magical atmosphere, especially in the early morning.",
    "Would recommend renting a car to see everything."
]

USERS = ["SakuraTraveler", "NatureLover99", "TokyoDrifter", "RuralEscapist", "OnsenHunter"]

def generate_ratings(num=5):
    ratings = []
    for _ in range(num):
        ratings.append({
            "user": random.choice(USERS),
            "location": random.choice(list(LOCATIONS.keys())),
            "score": random.randint(3, 5),
            "comment": random.choice(COMMENTS),
            "date": f"2025-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        })
    return ratings
