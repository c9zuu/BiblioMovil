import streamlit as st
import pandas as pd
from scraper_utils import scrape_website
import base64
from PIL import Image
import io
import requests

# Set page config for better mobile experience
st.set_page_config(
    page_title="BiblioMóvil - Catálogo de Libros",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Customize app appearance for mobile
st.markdown(
    """
    <style>
    .main > div {
        padding-top: 1rem;
    }
    .stButton button {
        width: 100%;
        border-radius: 10px;
        height: 3rem;
        font-size: 1rem;
        margin-top: 0.5rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .book-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s;
    }
    .book-card:hover {
        transform: translateY(-5px);
    }
    .book-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.3rem;
    }
    .book-author {
        font-size: 0.9rem;
        color: #555;
        margin-bottom: 0.5rem;
    }
    @media (max-width: 768px) {
        .main > div {
            padding: 0.5rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'book_info' not in st.session_state:
    st.session_state.book_info = {}

# Books catalog data
books = [
    {
        "id": 1,
        "title": "1984",
        "author": "George Orwell",
        "year": 1949,
        "genre": "Ficción distópica",
        "description": "Una inquietante distopía que presenta un futuro totalitario donde el gobierno, encabezado por el omnipresente Gran Hermano, controla cada aspecto de la vida de los ciudadanos, incluyendo sus pensamientos.",
        "cover_url": "https://m.media-amazon.com/images/I/71kxa1-0mfL._AC_UF1000,1000_QL80_.jpg"
    },
    {
        "id": 2,
        "title": "El Octavo Clan",
        "author": "Justine Evans",
        "year": 2015,
        "genre": "Ciencia ficción juvenil",
        "description": "En un mundo postapocalíptico, la humanidad se ha dividido en clanes. Una joven descubre que pertenece a un misterioso octavo clan cuya existencia se ha mantenido en secreto.",
        "cover_url": "https://m.media-amazon.com/images/I/81HKcvLn15L._AC_UF1000,1000_QL80_.jpg"
    },
    {
        "id": 3,
        "title": "Viaje al Centro de la Tierra",
        "author": "Julio Verne",
        "year": 1864,
        "genre": "Aventura",
        "description": "Un profesor de mineralogía descubre un manuscrito antiguo que revela un pasaje secreto hacia el centro de la Tierra. Junto a su sobrino y un guía, emprende una expedición llena de peligros y descubrimientos asombrosos.",
        "cover_url": "https://imagessl2.casadellibro.com/a/l/t7/72/9788467756272.jpg"
    },
    {
        "id": 4,
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "genre": "Ciencia ficción",
        "description": "Ambientada en un futuro lejano, esta saga épica narra la batalla por el control del planeta desértico Arrakis, único lugar donde se encuentra la especia melange, sustancia que permite el viaje espacial.",
        "cover_url": "https://m.media-amazon.com/images/I/81ym3QUd3KL._AC_UF1000,1000_QL80_.jpg"
    },
    {
        "id": 5,
        "title": "La Chica del Tren",
        "author": "Paula Hawkins",
        "year": 2015,
        "genre": "Thriller psicológico",
        "description": "Rachel toma el mismo tren todos los días y pasa por la misma casa donde vive una pareja aparentemente perfecta. Un día, Rachel es testigo de algo impactante y se ve involucrada en un misterio que cambiará su vida.",
        "cover_url": "https://m.media-amazon.com/images/I/61zzWCFCbmL._AC_UF1000,1000_QL80_.jpg"
    },
    {
        "id": 6,
        "title": "El Código Da Vinci",
        "author": "Dan Brown",
        "year": 2003,
        "genre": "Misterio",
        "description": "Cuando el conservador del Louvre es asesinado, Robert Langdon, profesor de simbología, se ve envuelto en una intrincada conspiración relacionada con obras de Leonardo da Vinci y un secreto que podría cambiar la historia del cristianismo.",
        "cover_url": "https://m.media-amazon.com/images/I/91Q5dCnPg5L._AC_UF1000,1000_QL80_.jpg"
    },
    {
        "id": 7,
        "title": "El Señor de los Anillos",
        "author": "J.R.R. Tolkien",
        "year": 1954,
        "genre": "Fantasía épica",
        "description": "En la Tierra Media, Frodo Bolsón recibe la misión de destruir un poderoso anillo en los fuegos del Monte del Destino. Su viaje épico, junto a la Comunidad del Anillo, define el destino de su mundo frente al oscuro poder de Sauron.",
        "cover_url": "https://m.media-amazon.com/images/I/71jLBXtWJWL._AC_UF1000,1000_QL80_.jpg"
    },
    {
        "id": 8,
        "title": "Harry Potter y la Piedra Filosofal",
        "author": "J.K. Rowling",
        "year": 1997,
        "genre": "Fantasía",
        "description": "Harry Potter descubre en su undécimo cumpleaños que es hijo de magos y es invitado a estudiar en el Colegio Hogwarts de Magia y Hechicería, donde se enfrenta por primera vez a su nemesis, Lord Voldemort.",
        "cover_url": "https://m.media-amazon.com/images/I/81RfuxQbDOL._AC_UF1000,1000_QL80_.jpg"
    },
    {
        "id": 9,
        "title": "El Principito",
        "author": "Antoine de Saint-Exupéry",
        "year": 1943,
        "genre": "Fábula",
        "description": "Un piloto se encuentra perdido en el desierto del Sahara, donde conoce a un pequeño príncipe que viene de un asteroide lejano. A través de conversaciones filosóficas, el niño le enseña importantes lecciones sobre la vida.",
        "cover_url": "https://m.media-amazon.com/images/I/71lLj2XN0YL._AC_UF1000,1000_QL80_.jpg"
    },
    {
        "id": 10,
        "title": "Cien Años de Soledad",
        "author": "Gabriel García Márquez",
        "year": 1967,
        "genre": "Realismo mágico",
        "description": "Esta obra maestra narra la historia de la familia Buendía a lo largo de siete generaciones en el pueblo ficticio de Macondo, mezclando elementos reales con fantásticos en un retrato de la sociedad latinoamericana.",
        "cover_url": "https://m.media-amazon.com/images/I/71KN4YvL8rL._AC_UF1000,1000_QL80_.jpg"
    }
]

# Function to get book information from the web
def get_book_info(title, author):
    search_query = f"{title} {author} libro sinopsis"
    try:
        # This would typically search for more info about the book
        # For this demo, we'll just return the existing info
        for book in books:
            if book["title"].lower() == title.lower():
                return book
        return None
    except:
        return None

# Function to load image from URL
def load_image_from_url(url):
    try:
        response = requests.get(url)
        img = Image.open(io.BytesIO(response.content))
        return img
    except:
        # Return a default image if the URL doesn't work
        return None

# Function to create book card
def book_card(book):
    col1, col2 = st.columns([1, 3])
    with col1:
        try:
            st.image(book["cover_url"], width=100)
        except:
            st.write("📚")
    
    with col2:
        st.markdown(f"<div class='book-title'>{book['title']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='book-author'>Por: {book['author']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div>{book['genre']} ({book['year']})</div>", unsafe_allow_html=True)
        
        if st.button(f"Ver detalles", key=f"btn_{book['id']}"):
            st.session_state.current_page = 'detail'
            st.session_state.book_info = book
            st.rerun()

# Function to show book details
def show_book_details(book):
    # Back button
    if st.button("← Regresar al catálogo"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.title(book["title"])
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        try:
            st.image(book["cover_url"], width=250)
        except:
            st.write("📚 Imagen no disponible")
    
    with col2:
        st.subheader("Detalles del libro")
        st.write(f"**Autor:** {book['author']}")
        st.write(f"**Año de publicación:** {book['year']}")
        st.write(f"**Género:** {book['genre']}")
        st.write("**Descripción:**")
        st.markdown(f"<div style='background-color:#f8f9fa; padding:10px; border-radius:5px;'>{book['description']}</div>", unsafe_allow_html=True)
    
    # Try to get more information about the book online
    st.subheader("Información adicional")
    try:
        # This would typically get more information from a web scraper
        # For this demo, we'll just show a placeholder
        st.info("La información adicional no está disponible en este momento.")
    except:
        st.warning("No se pudo obtener información adicional.")

# Main application
st.title("📚 BiblioMóvil")
st.write("Explora nuestra colección de libros clásicos y contemporáneos")

# Show different pages based on session state
if st.session_state.current_page == 'home':
    # Search box
    search_query = st.text_input("Buscar libro por título o autor")
    
    # Filter books based on search query
    filtered_books = books
    if search_query:
        filtered_books = [book for book in books if 
                         search_query.lower() in book["title"].lower() or 
                         search_query.lower() in book["author"].lower()]
    
    # Display books catalog
    st.subheader(f"Catálogo de Libros ({len(filtered_books)} resultados)")
    
    if not filtered_books:
        st.write("No se encontraron resultados para tu búsqueda.")
    
    for book in filtered_books:
        with st.container():
            st.markdown("<div class='book-card'>", unsafe_allow_html=True)
            book_card(book)
            st.markdown("</div>", unsafe_allow_html=True)
            st.write("")
    
elif st.session_state.current_page == 'detail':
    show_book_details(st.session_state.book_info)