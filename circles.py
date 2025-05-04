import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from scipy.optimize import minimize
import math

def find_circle_intersections(circles):
    """Znajduje punkty przecięcia okręgów"""
    
    # Funkcja do minimalizacji - odległość od wszystkich okręgów
    def distance_from_all_circles(point):
        total_distance = 0
        for center_x, center_y, radius in circles:
            # Obliczamy odległość od punktu do okręgu
            dist_to_center = math.sqrt((point[0] - center_x)**2 + (point[1] - center_y)**2)
            dist_to_circle = abs(dist_to_center - radius)
            total_distance += dist_to_circle**2
        return total_distance
    
    # Sprawdzamy, czy okręgi się przecinają
    if len(circles) < 2:
        return []
    
    # Szukamy punktów przecięcia dla każdej pary okręgów
    intersection_points = []
    
    # Dla każdej pary okręgów
    for i in range(len(circles)):
        for j in range(i+1, len(circles)):
            x1, y1, r1 = circles[i]
            x2, y2, r2 = circles[j]
            
            # Obliczamy odległość między środkami
            d = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            # Sprawdzamy, czy okręgi się przecinają
            if d > r1 + r2 or d < abs(r1 - r2):
                continue  # Okręgi nie mają punktów przecięcia
            
            # Obliczamy punkty przecięcia
            a = (r1**2 - r2**2 + d**2) / (2 * d)
            h = math.sqrt(r1**2 - a**2)
            
            x3 = x1 + a * (x2 - x1) / d
            y3 = y1 + a * (y2 - y1) / d
            
            # Dwa punkty przecięcia
            x4_1 = x3 + h * (y2 - y1) / d
            y4_1 = y3 - h * (x2 - x1) / d
            
            x4_2 = x3 - h * (y2 - y1) / d
            y4_2 = y3 + h * (x2 - x1) / d
            
            # Dodajemy punkty przecięcia
            intersection_points.append((x4_1, y4_1))
            intersection_points.append((x4_2, y4_2))
    
    # Jeśli mamy więcej niż 2 okręgi, szukamy punktów wspólnych dla wszystkich
    if len(circles) > 2:
        common_points = []
        
        # Sprawdzamy każdy punkt przecięcia
        for point in intersection_points:
            is_common = True
            
            # Sprawdzamy, czy punkt leży na wszystkich okręgach
            for center_x, center_y, radius in circles:
                dist = math.sqrt((point[0] - center_x)**2 + (point[1] - center_y)**2)
                if abs(dist - radius) > 1e-10:  # Tolerancja numeryczna
                    is_common = False
                    break
            
            if is_common:
                common_points.append(point)
        
        # Jeśli nie znaleźliśmy punktów wspólnych, próbujemy znaleźć je numerycznie
        if not common_points and intersection_points:
            # Używamy punktów przecięcia jako punktów startowych
            for point in intersection_points:
                result = minimize(distance_from_all_circles, point, method='Nelder-Mead')
                
                if result.fun < 1e-10:  # Jeśli znaleźliśmy punkt blisko wszystkich okręgów
                    common_points.append(tuple(result.x))
            
            # Usuwamy duplikaty (punkty bardzo blisko siebie)
            if common_points:
                filtered_points = [common_points[0]]
                for point in common_points[1:]:
                    if all(math.sqrt((point[0] - p[0])**2 + (point[1] - p[1])**2) > 1e-6 for p in filtered_points):
                        filtered_points.append(point)
                common_points = filtered_points
        
        return common_points
    
    return intersection_points

def draw_circles_and_intersections():
    st.title("Wizualizacja okręgów i ich punktów przecięcia")
    
    # Dodajemy kolumny do wprowadzania danych
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dodaj okręgi")
        num_circles = st.number_input("Liczba okręgów", min_value=2, max_value=10, value=3)
    
    # Tworzymy listę okręgów
    circles = []
    
    # Interfejs do wprowadzania danych okręgów
    for i in range(num_circles):
        st.markdown(f"### Okrąg {i+1}")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            center_x = st.number_input(f"Środek X okręgu {i+1}", value=float(i*2))
        
        with col2:
            center_y = st.number_input(f"Środek Y okręgu {i+1}", value=float(i))
        
        with col3:
            radius = st.number_input(f"Promień okręgu {i+1}", min_value=0.1, value=float(i+2))
        
        circles.append((center_x, center_y, radius))
    
    # Rysujemy okręgi i punkty przecięcia
    if st.button("Rysuj okręgi i znajdź punkty przecięcia"):
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Rysujemy okręgi
        for i, (center_x, center_y, radius) in enumerate(circles):
            circle = Circle((center_x, center_y), radius, fill=False, 
                           edgecolor=f'C{i}', linewidth=2, alpha=0.7, label=f'Okrąg {i+1}')
            ax.add_patch(circle)
            ax.text(center_x, center_y, f'O{i+1}', fontsize=12, ha='center', va='center')
        
        # Znajdujemy punkty przecięcia
        intersection_points = find_circle_intersections(circles)
        
        # Rysujemy punkty przecięcia
        if intersection_points:
            intersection_x = [p[0] for p in intersection_points]
            intersection_y = [p[1] for p in intersection_points]
            ax.scatter(intersection_x, intersection_y, color='red', s=100, zorder=5, label='Punkty przecięcia')
            
            # Wyświetlamy współrzędne punktów przecięcia
            for i, (x, y) in enumerate(intersection_points):
                ax.text(x + 0.1, y + 0.1, f'P{i+1}({x:.2f}, {y:.2f})', fontsize=10)
            
            st.success(f"Znaleziono {len(intersection_points)} punktów przecięcia.")
            
            # Wyświetlamy współrzędne w tabeli
            st.subheader("Współrzędne punktów przecięcia:")
            for i, (x, y) in enumerate(intersection_points):
                st.write(f"P{i+1}: ({x:.4f}, {y:.4f})")
        else:
            st.warning("Nie znaleziono punktów przecięcia dla wszystkich okręgów.")
        
        # Ustawiamy równe osie i dodajemy legendę
        ax.set_aspect('equal')
        ax.legend()
        ax.grid(True)
        
        # Ustawiamy limity osi
        all_x = [c[0] for c in circles]
        all_y = [c[1] for c in circles]
        all_r = [c[2] for c in circles]
        
        max_range = max(all_r) * 2
        min_x, max_x = min(all_x) - max_range, max(all_x) + max_range
        min_y, max_y = min(all_y) - max_range, max(all_y) + max_range
        
        ax.set_xlim(min_x, max_x)
        ax.set_ylim(min_y, max_y)
        
        # Dodajemy tytuły
        ax.set_title("Okręgi i ich punkty przecięcia")
        ax.set_xlabel("Oś X")
        ax.set_ylabel("Oś Y")
        
        # Wyświetlamy wykres
        st.pyplot(fig)

if __name__ == "__main__":
    draw_circles_and_intersections()
