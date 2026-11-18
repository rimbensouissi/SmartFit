import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, date
import json
import os
import cv2
from PIL import Image, ImageTk
import threading
import mediapipe as mp
import time

# Modern color palette - Professional blue theme
PRIMARY_DARK = '#0f172a'       # Deep navy
PRIMARY_BLUE = '#1e40af'       # Rich blue
ACCENT_BLUE = '#3b82f6'        # Bright blue
ACCENT_CYAN = '#06b6d4'        # Cyan accent
LIGHT_BG = '#f8fafc'           # Light background
CARD_BG = '#ffffff'            # Card background
TEXT_DARK = '#1e293b'          # Dark texti need a button
TEXT_LIGHT = '#64748b'         # Light text
SUCCESS_GREEN = '#10b981'      # Success green
WARNING_ORANGE = '#f59e0b'     # Warning orange
ERROR_RED = '#ef4444'          # Error red

# Modern font configuration
FONT_PRIMARY = 'Segoe UI'
FONT_SECONDARY = 'Arial'

def get_haar_cascade_path(filename='haarcascade_frontalface_default.xml'):
    """Return a usable path to the Haar cascade XML file."""
    try:
        base = cv2.data.haarcascades
        path = os.path.join(base, filename)
        if os.path.exists(path):
            return path
    except Exception:
        pass

    candidates = [
        os.path.join(os.getcwd(), filename),
        os.path.join(os.path.dirname(__file__), filename),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    ]

    try:
        if hasattr(cv2, '__file__'):
            candidates.append(os.path.join(os.path.dirname(cv2.__file__), 'data', 'haarcascades', filename))
    except Exception:
        pass

    for p in candidates:
        if p and os.path.exists(p):
            return p

    return filename

class ModernButton(tk.Button):
    """Bouton moderne avec effets de survol"""
    def __init__(self, master=None, **kwargs):
        self.original_bg = kwargs.get('bg', ACCENT_BLUE)
        self.hover_bg = self.lighten_color(self.original_bg, 20)
        self.active_bg = self.lighten_color(self.original_bg, -10)
       
        kwargs.update({
            'font': (FONT_PRIMARY, 11, 'bold'),
            'relief': 'flat',
            'bd': 0,
            'cursor': 'hand2',
            'padx': 20,
            'pady': 12
        })
       
        super().__init__(master, **kwargs)
       
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<ButtonPress-1>', self.on_press)
        self.bind('<ButtonRelease-1>', self.on_release)
   
    def lighten_color(self, color, percent):
        """Éclaircit ou assombrit une couleur hexadécimale"""
        color = color.lstrip('#')
        r, g, b = [int(color[i:i+2], 16) for i in (0, 2, 4)]
       
        r = max(0, min(255, r + int(r * percent / 100)))
        g = max(0, min(255, g + int(g * percent / 100)))
        b = max(0, min(255, b + int(b * percent / 100)))
       
        return f'#{r:02x}{g:02x}{b:02x}'
   
    def on_enter(self, e):
        self.configure(bg=self.hover_bg)
   
    def on_leave(self, e):
        self.configure(bg=self.original_bg)
   
    def on_press(self, e):
        self.configure(bg=self.active_bg)
   
    def on_release(self, e):
        self.configure(bg=self.hover_bg)

class CardFrame(tk.Frame):
    """Frame avec style de carte moderne"""
    def __init__(self, master=None, **kwargs):
        kwargs.update({
            'bg': CARD_BG,
            'relief': 'flat',
            'bd': 1,
            'highlightbackground': '#e2e8f0',
            'highlightthickness': 1
        })
        super().__init__(master, **kwargs)

class InnoversApp:
    def __init__(self, root):
        self.root = root
        self.root.title("INNOVERSE - Fitness Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg=PRIMARY_DARK)
       
        # Style configuration
        self.setup_styles()
       
        self.center_window()
        self.create_widgets()
   
    def setup_styles(self):
        """Configure les styles modernes pour l'application"""
        style = ttk.Style()
        style.theme_use('clam')
       
        # Configure notebook style
        style.configure('Modern.TNotebook', background=PRIMARY_DARK)
        style.configure('Modern.TNotebook.Tab',
                       font=(FONT_PRIMARY, 11, 'bold'),
                       padding=[20, 10],
                       background=PRIMARY_BLUE,
                       foreground='white')
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', ACCENT_BLUE),
                           ('active', ACCENT_CYAN)])
   
    def center_window(self):
        """Centrer la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = 1200
        height = 800
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
   
    def get_real_stats(self):
        """Récupère les statistiques réelles depuis le fichier JSON"""
        members_file = "members_data.json"
        today = date.today().strftime("%Y-%m-%d")
       
        if not os.path.exists(members_file):
            return {
                'total_members': 0,
                'today_sessions': 0,
                'active_this_week': 0
            }
       
        try:
            with open(members_file, 'r', encoding='utf-8') as f:
                members_data = json.load(f)
           
            total_members = len(members_data)
            today_sessions = 0
            active_this_week = 0
           
            for member_id, member in members_data.items():
                # Compter les séances d'aujourd'hui
                if 'training_sessions' in member:
                    for session in member['training_sessions']:
                        if today in session:
                            today_sessions += 1
               
                # Compter les membres actifs cette semaine
                if 'last_activity' in member:
                    last_activity = datetime.strptime(member['last_activity'], "%Y-%m-%d").date()
                    days_since_activity = (date.today() - last_activity).days
                    if days_since_activity <= 7:
                        active_this_week += 1
                else:
                    # Si pas de dernière activité, considérer comme inactif
                    pass
           
            return {
                'total_members': total_members,
                'today_sessions': today_sessions,
                'active_this_week': active_this_week
            }
           
        except Exception:
            return {
                'total_members': 0,
                'today_sessions': 0,
                'active_this_week': 0
            }
   
    def create_widgets(self):
        # Main container with modern background
        main_container = tk.Frame(self.root, bg=PRIMARY_DARK)
        main_container.pack(fill='both', expand=True)
       
        # Header avec navigation moderne
        header = tk.Frame(main_container, bg=PRIMARY_DARK, height=80)
        header.pack(fill='x', padx=40, pady=20)
        header.pack_propagate(False)
       
        # Logo et titre
        logo_frame = tk.Frame(header, bg=PRIMARY_DARK)
        logo_frame.pack(side='left')
       
        title = tk.Label(logo_frame,
                        text="INNOVERSE",
                        font=(FONT_PRIMARY, 28, 'bold'),
                        fg='white',
                        bg=PRIMARY_DARK)
        title.pack(anchor='w')
       
        subtitle = tk.Label(logo_frame,
                          text="Institut Supérieur - SmartFit",
                          font=(FONT_PRIMARY, 12),
                          fg=ACCENT_CYAN,
                          bg=PRIMARY_DARK)
        subtitle.pack(anchor='w')
       
        # Navigation buttons
        nav_frame = tk.Frame(header, bg=PRIMARY_DARK)
        nav_frame.pack(side='right')
       
        coach_btn = ModernButton(nav_frame,
                               text="🏋️‍♂️ Espace Coach",
                               bg=ACCENT_BLUE,
                               fg='white',
                               command=self.open_coach_login)
        coach_btn.pack(side='left', padx=10)
       
        member_btn = ModernButton(nav_frame,
                                text="👤 Espace Membre",
                                bg=ACCENT_CYAN,
                                fg='white',
                                command=self.open_member_space)
        member_btn.pack(side='left', padx=10)
       
        # Hero Section avec statistiques
        hero_frame = CardFrame(main_container)
        hero_frame.pack(fill='both', expand=True, padx=40, pady=20)
       
        # Content grid
        content_grid = tk.Frame(hero_frame, bg=CARD_BG)
        content_grid.pack(fill='both', expand=True, padx=40, pady=40)
       
        # Left side - Welcome message and stats
        left_panel = tk.Frame(content_grid, bg=CARD_BG)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 40))
       
        welcome_title = tk.Label(left_panel,
                               text="Bienvenue à INNOVERSE",
                               font=(FONT_PRIMARY, 32, 'bold'),
                               fg=TEXT_DARK,
                               bg=CARD_BG)
        welcome_title.pack(anchor='w', pady=(0, 20))
       
        welcome_text = tk.Label(left_panel,
                              text="""Système intelligent de gestion fitness intégrant reconnaissance faciale et suivi des performances en temps réel.

• 🤖 Authentification biométrique avancée
• 📊 Tableaux de bord personnalisés
• 🏃‍♂️ Suivi automatique des exercices
• 👥 Gestion complète des membres
• 📈 Analytics et rapports détaillés""",
                              font=(FONT_PRIMARY, 14),
                              fg=TEXT_LIGHT,
                              bg=CARD_BG,
                              justify='left')
        welcome_text.pack(anchor='w', pady=(0, 40))
       
        # Statistiques réelles
        stats = self.get_real_stats()
        stats_frame = tk.Frame(left_panel, bg=CARD_BG)
        stats_frame.pack(anchor='w')
       
        stats_data = [
            (f"{stats['total_members']}+", "Membres inscrits", ACCENT_BLUE),
            (f"{stats['today_sessions']}", "Séances aujourd'hui", SUCCESS_GREEN),
            (f"{stats['active_this_week']}+", "Actifs cette semaine", WARNING_ORANGE)
        ]
       
        for i, (number, text, color) in enumerate(stats_data):
            stat_frame = tk.Frame(stats_frame, bg=CARD_BG)
            stat_frame.pack(side='left', padx=(0, 30))
           
            num_label = tk.Label(stat_frame,
                               text=number,
                               font=(FONT_PRIMARY, 24, 'bold'),
                               fg=color,
                               bg=CARD_BG)
            num_label.pack(anchor='w')
           
            text_label = tk.Label(stat_frame,
                                text=text,
                                font=(FONT_PRIMARY, 11),
                                fg=TEXT_LIGHT,
                                bg=CARD_BG)
            text_label.pack(anchor='w')
       
        # Right side - Feature cards
        right_panel = tk.Frame(content_grid, bg=CARD_BG)
        right_panel.pack(side='right', fill='y')
       
        features = [
            ("🔐 Sécurité Avancée", "Authentification par reconnaissance faciale et gestion d'accès sécurisée"),
            ("📱 Interface Moderne", "Design responsive et expérience utilisateur optimisée"),
            ("📊 Analytics Temps Réel", "Suivi des performances et rapports détaillés"),
            ("🤖 IA Intégrée", "Détection automatique des exercices et comptage intelligent")
        ]
       
        for i, (title, desc) in enumerate(features):
            feature_card = CardFrame(right_panel)
            feature_card.pack(fill='x', pady=10)
           
            tk.Label(feature_card,
                    text=title,
                    font=(FONT_PRIMARY, 14, 'bold'),
                    fg=TEXT_DARK,
                    bg=CARD_BG).pack(anchor='w', padx=20, pady=(15, 5))
           
            tk.Label(feature_card,
                    text=desc,
                    font=(FONT_PRIMARY, 11),
                    fg=TEXT_LIGHT,
                    bg=CARD_BG,
                    wraplength=300,
                    justify='left').pack(anchor='w', padx=20, pady=(0, 15))
       
        # Footer
        footer = tk.Frame(main_container, bg=PRIMARY_DARK, height=60)
        footer.pack(fill='x', side='bottom')
        footer.pack_propagate(False)
       
        footer_text = tk.Label(footer,
                             text="INNOVERSE © 2025 - Système de Gestion Fitness Intelligent. Tous droits réservés.",
                             font=(FONT_PRIMARY, 10),
                             fg=TEXT_LIGHT,
                             bg=PRIMARY_DARK)
        footer_text.pack(expand=True)
   
    def open_coach_login(self):
        """Ouvre la fenêtre de connexion coach moderne"""
        login_window = tk.Toplevel(self.root)
        login_window.title("INNOVERSE - Connexion Coach")
        login_window.geometry("450x500")
        login_window.configure(bg=LIGHT_BG)
        login_window.resizable(False, False)
        login_window.transient(self.root)
        login_window.grab_set()
       
        self.center_child_window(login_window, 450, 500)
       
        # Header du login
        header_frame = tk.Frame(login_window, bg=PRIMARY_BLUE, height=120)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
       
        tk.Label(header_frame,
                text="🏋️‍♂️",
                font=(FONT_PRIMARY, 32),
                bg=PRIMARY_BLUE,
                fg='white').pack(expand=True)
       
        tk.Label(header_frame,
                text="Espace Coach",
                font=(FONT_PRIMARY, 20, 'bold'),
                bg=PRIMARY_BLUE,
                fg='white').pack(expand=True)
       
        # Formulaire de connexion
        form_frame = CardFrame(login_window)
        form_frame.pack(fill='both', expand=True, padx=40, pady=30)
       
        tk.Label(form_frame,
                text="Connexion sécurisée",
                font=(FONT_PRIMARY, 16, 'bold'),
                fg=TEXT_DARK,
                bg=CARD_BG).pack(pady=(30, 10))
       
        tk.Label(form_frame,
                text="Accédez à votre tableau de bord coach",
                font=(FONT_PRIMARY, 11),
                fg=TEXT_LIGHT,
                bg=CARD_BG).pack(pady=(0, 30))
       
        # Champs de saisie
        input_frame = tk.Frame(form_frame, bg=CARD_BG)
        input_frame.pack(fill='x', padx=40, pady=20)
       
        tk.Label(input_frame,
                text="Nom d'utilisateur",
                font=(FONT_PRIMARY, 11, 'bold'),
                fg=TEXT_DARK,
                bg=CARD_BG).pack(anchor='w', pady=(10, 5))
       
        username_entry = tk.Entry(input_frame,
                                font=(FONT_PRIMARY, 12),
                                bg='#f8fafc',
                                relief='flat',
                                bd=1,
                                highlightbackground='#e2e8f0',
                                highlightthickness=1,
                                highlightcolor=ACCENT_BLUE)
        username_entry.pack(fill='x', pady=(0, 20),)
       
        tk.Label(input_frame,
                text="Mot de passe",
                font=(FONT_PRIMARY, 11, 'bold'),
                fg=TEXT_DARK,
                bg=CARD_BG).pack(anchor='w', pady=(10, 5))
       
        password_entry = tk.Entry(input_frame,
                                show='•',
                                font=(FONT_PRIMARY, 12),
                                bg='#f8fafc',
                                relief='flat',
                                bd=1,
                                highlightbackground='#e2e8f0',
                                highlightthickness=1,
                                highlightcolor=ACCENT_BLUE)
        password_entry.pack(fill='x', pady=(0, 10),ipady=8)
       
        # Bouton de connexion
        login_btn = ModernButton(form_frame,
                               text="🔐 Se Connecter",
                               bg=ACCENT_BLUE,
                               fg='white',
                               command=lambda: self.verify_coach_login(
                                   username_entry.get(),
                                   password_entry.get(),
                                   login_window))
        login_btn.pack(pady=30)
       
        # Informations de connexion
        info_text = tk.Label(form_frame,
                           text="Identifiants de test:\nNom d'utilisateur: admin | Mot de passe: admin",
                           font=(FONT_PRIMARY, 9),
                           fg=TEXT_LIGHT,
                           bg=CARD_BG)
        info_text.pack(pady=(0, 20))
       
        # Bind Enter key
        password_entry.bind('<Return>',
                          lambda e: self.verify_coach_login(
                              username_entry.get(),
                              password_entry.get(),
                              login_window))
       
        username_entry.focus()

    def center_child_window(self, window, width, height):
        """Centre une fenêtre enfant"""
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def verify_coach_login(self, username, password, login_window):
        """Vérifie les identifiants du coach"""
        if username == "admin" and password == "admin":
            login_window.destroy()
            self.open_coach_dashboard()
        else:
            messagebox.showerror(
                "Erreur de Connexion",
                "Identifiants incorrects!\n\nUtilisez:\nNom d'utilisateur: admin\nMot de passe: admin",
                parent=login_window
            )

    def open_coach_dashboard(self):
        """Tableau de bord moderne pour les coachs"""
        coach_window = tk.Toplevel(self.root)
        coach_window.title("INNOVERSE - Tableau de Bord Coach")
        coach_window.geometry("1400x900")
        coach_window.configure(bg=LIGHT_BG)
       
        self.center_child_window(coach_window, 1400, 900)
       
        # Header moderne
        header = tk.Frame(coach_window, bg=PRIMARY_DARK, height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
       
        tk.Label(header,
                text="📊 Tableau de Bord Coach",
                font=(FONT_PRIMARY, 20, 'bold'),
                fg='white',
                bg=PRIMARY_DARK).pack(side='left', padx=40, expand=True)
       
        back_btn = ModernButton(header,
                              text="← Retour",
                              bg=ERROR_RED,
                              fg='white',
                              command=coach_window.destroy)
        back_btn.pack(side='right', padx=40)
       
        # Contenu principal
        main_content = tk.Frame(coach_window, bg=LIGHT_BG)
        main_content.pack(fill='both', expand=True, padx=40, pady=30)
       
        # Cartes de statistiques réelles
        stats_frame = tk.Frame(main_content, bg=LIGHT_BG)
        stats_frame.pack(fill='x', pady=(0, 30))
       
        real_stats = self.get_real_stats()
        stats_cards = [
            ("👥 Membres Inscrits", f"{real_stats['total_members']}", ACCENT_BLUE, "Total des membres"),
            ("🏋️‍♂️ Séances Aujourd'hui", f"{real_stats['today_sessions']}", SUCCESS_GREEN, "Séances ce jour"),
            ("📈 Actifs Cette Semaine", f"{real_stats['active_this_week']}", WARNING_ORANGE, "Membres actifs")
        ]
       
        for i, (title, value, color, subtitle) in enumerate(stats_cards):
            card = CardFrame(stats_frame)
            card.pack(side='left', fill='both', expand=True, padx=(0, 20))
           
            tk.Label(card,
                    text=title,
                    font=(FONT_PRIMARY, 12),
                    fg=TEXT_LIGHT,
                    bg=CARD_BG).pack(anchor='w', padx=20, pady=(20, 5))
           
            tk.Label(card,
                    text=value,
                    font=(FONT_PRIMARY, 24, 'bold'),
                    fg=color,
                    bg=CARD_BG).pack(anchor='w', padx=20, pady=(0, 5))
           
            tk.Label(card,
                    text=subtitle,
                    font=(FONT_PRIMARY, 10),
                    fg=TEXT_LIGHT,
                    bg=CARD_BG).pack(anchor='w', padx=20, pady=(0, 20))
       
        # Fonctionnalités principales
        features_title = tk.Label(main_content,
                                text="Fonctionnalités Principales",
                                font=(FONT_PRIMARY, 18, 'bold'),
                                fg=TEXT_DARK,
                                bg=LIGHT_BG)
        features_title.pack(anchor='w', pady=(0, 20))
       
        features_grid = tk.Frame(main_content, bg=LIGHT_BG)
        features_grid.pack(fill='both', expand=True)
       
        features = [
            ("👥 Gestion des Membres", self.open_member_management,
             "Gérez les profils, suivez les progrès et consultez l'historique des membres", PRIMARY_BLUE),
            ("📈 Suivi des Poids", self.open_weight_tracking,
             "Sélectionnez un adhérent et consultez sa courbe de poids au fil du temps", SUCCESS_GREEN),
            ("📊 Suivi des Performances", self.open_performance_tracking,
             "Analysez les performances et générez des rapports détaillés", ACCENT_CYAN),
            ("📅 Planification des Séances", self.open_session_planning,
             "Organisez et planifiez les séances d'entraînement", WARNING_ORANGE)
        ]
       
        for i, (title, command, description, color) in enumerate(features):
            row = i // 2
            col = i % 2
           
            feature_card = CardFrame(features_grid)
            feature_card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
           
            # Icon and title
            title_frame = tk.Frame(feature_card, bg=CARD_BG)
            title_frame.pack(fill='x', padx=20, pady=(20, 10))
           
            tk.Label(title_frame,
                    text=title.split()[0],  # Emoji
                    font=(FONT_PRIMARY, 20),
                    bg=CARD_BG).pack(side='left')
           
            tk.Label(title_frame,
                    text=' '.join(title.split()[1:]),  # Text
                    font=(FONT_PRIMARY, 14, 'bold'),
                    fg=TEXT_DARK,
                    bg=CARD_BG).pack(side='left', padx=(10, 0))
           
            # Description
            tk.Label(feature_card,
                    text=description,
                    font=(FONT_PRIMARY, 11),
                    fg=TEXT_LIGHT,
                    bg=CARD_BG,
                    wraplength=300,
                    justify='left').pack(fill='x', padx=20, pady=(0, 20))
           
            # Action button
            action_btn = ModernButton(feature_card,
                                    text="Accéder →",
                                    bg=color,
                                    fg='white',
                                    command=command)
            action_btn.pack(padx=20, pady=(0, 20))
           
            features_grid.grid_columnconfigure(col, weight=1)
            features_grid.grid_rowconfigure(row, weight=1)

    def open_member_space(self):
        """Ouvre l'espace membre avec design moderne"""
        self.member_auth_camera = FacialRecognitionCamera(self.root, self.on_member_photo_captured)
        self.member_auth_camera.open_camera()

    def on_member_photo_captured(self, success, image):
        """Callback quand un membre capture sa photo pour authentification."""
        if not success or image is None:
            messagebox.showwarning("Authentification", "Aucune photo capturée. Authentification annulée.", parent=self.root)
            return

        matched = self.authenticate_member_by_photo(image)
        if matched is None:
            messagebox.showerror("Authentification échouée", "Aucun membre correspondant trouvé.", parent=self.root)
        else:
            cin, member = matched
            self.open_member_dashboard(cin, member)

    def authenticate_member_by_photo(self, captured_image):
        """Compare la photo capturée avec les photos enregistrées des membres."""
        members_file = "members_data.json"
        photos_dir = "member_photos"

        if not os.path.exists(members_file):
            return None

        try:
            with open(members_file, 'r', encoding='utf-8') as f:
                members = json.load(f)
        except Exception:
            return None

        face_cascade = cv2.CascadeClassifier(get_haar_cascade_path())

        try:
            cap_bgr = cv2.cvtColor(captured_image, cv2.COLOR_RGB2BGR)
        except Exception:
            cap_bgr = captured_image

        gray_cap = cv2.cvtColor(cap_bgr, cv2.COLOR_BGR2GRAY)
        faces_cap = face_cascade.detectMultiScale(gray_cap, 1.3, 5)

        if len(faces_cap) == 0:
            return None

        x, y, w, h = faces_cap[0]
        face_cap = gray_cap[y:y+h, x:x+w]

        try:
            face_cap = cv2.resize(face_cap, (100, 100))
        except Exception:
            return None

        for cin, member in members.items():
            photo_path = member.get('photo_path')
            if not photo_path:
                continue

            if not os.path.exists(photo_path):
                alt = os.path.join(photos_dir, os.path.basename(photo_path))
                if os.path.exists(alt):
                    photo_path = alt
                else:
                    continue

            try:
                stored = cv2.imread(photo_path)
                if stored is None:
                    continue
                gray_stored = cv2.cvtColor(stored, cv2.COLOR_BGR2GRAY)
                faces_stored = face_cascade.detectMultiScale(gray_stored, 1.3, 5)
                if len(faces_stored) == 0:
                    continue

                xs, ys, ws, hs = faces_stored[0]
                face_stored = gray_stored[ys:ys+hs, xs:xs+ws]
                face_stored = cv2.resize(face_stored, (100, 100))

                try:
                    res = cv2.matchTemplate(face_stored, face_cap, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                    score = max_val
                except Exception:
                    diff = (face_stored.astype('float') - face_cap.astype('float'))
                    mse = (diff ** 2).mean()
                    score = 1.0 / (1.0 + mse)

                if score >= 0.45:
                    return (cin, member)
            except Exception:
                continue

        return None

    def open_member_dashboard(self, cin, member):
        """Ouvre une interface moderne pour le membre authentifié"""
        dash = tk.Toplevel(self.root)
        dash.title(f"Espace Membre - {member.get('first_name','')} {member.get('last_name','')}")
        dash.geometry("700x650")
        dash.configure(bg=LIGHT_BG)

        # Header moderne
        header = tk.Frame(dash, bg=PRIMARY_BLUE, height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
       
        tk.Label(header,
                text=f"👤 Bienvenue, {member.get('first_name','')} {member.get('last_name','')}",
                font=(FONT_PRIMARY, 18, 'bold'),
                fg='white',
                bg=PRIMARY_BLUE).pack(expand=True)

        # Main content frame
        content_frame = tk.Frame(dash, bg=LIGHT_BG)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Member info card
        info_card = CardFrame(content_frame)
        info_card.pack(fill='x', pady=(0, 20))
       
        tk.Label(info_card,
                text=f"📋 Informations du membre",
                font=(FONT_PRIMARY, 14, 'bold'),
                fg=TEXT_DARK,
                bg=CARD_BG).pack(anchor='w', padx=20, pady=(15, 5))
       
        tk.Label(info_card,
                text=f"CIN: {cin} | 📞 Téléphone: {member.get('phone','')}",
                font=(FONT_PRIMARY, 11),
                fg=TEXT_LIGHT,
                bg=CARD_BG).pack(anchor='w', padx=20, pady=(0, 15))

        # Exercise selection section
        exercise_frame = CardFrame(content_frame)
        exercise_frame.pack(fill='x', pady=10)

        tk.Label(exercise_frame,
                text="🏃‍♂️ Sélectionner un Exercice",
                font=(FONT_PRIMARY, 12, 'bold'),
                fg=TEXT_DARK,
                bg=CARD_BG).pack(anchor='w', padx=20, pady=(15, 5))

        exercises = ["Pompes (Push-ups)", "Abdominaux (Sit-ups)", "Squats", "Tapis (Tapis Roulant)",
                    "Jogging", "Cyclisme", "Natation", "Marche", "Autre"]
        exercise_var = tk.StringVar(value=exercises[0])
        exercise_combo = ttk.Combobox(exercise_frame, textvariable=exercise_var,
                                     values=exercises, state='readonly',
                                     font=(FONT_PRIMARY, 11))
        exercise_combo.pack(padx=20, pady=(0, 15), fill='x')

        # Weight input section
        weight_frame = CardFrame(content_frame)
        weight_frame.pack(fill='x', pady=10)

        tk.Label(weight_frame,
                text="⚖️ Enregistrer le Poids",
                font=(FONT_PRIMARY, 12, 'bold'),
                fg=TEXT_DARK,
                bg=CARD_BG).pack(anchor='w', padx=20, pady=(15, 5))

        weight_entry = tk.Entry(weight_frame, font=(FONT_PRIMARY, 11))
        weight_entry.pack(padx=20, pady=(0, 15), fill='x')

        # Buttons frame
        buttons_frame = tk.Frame(content_frame, bg=LIGHT_BG)
        buttons_frame.pack(fill='x', pady=20)

        def save_session():
            exercise = exercise_var.get()
            weight_str = weight_entry.get().strip()

            if not exercise or not weight_str:
                messagebox.showwarning("Attention", "Veuillez sélectionner un exercice et entrer le poids.", parent=dash)
                return

            try:
                weight_val = float(weight_str)
            except ValueError:
                messagebox.showerror("Erreur", "Le poids doit être un nombre valide.", parent=dash)
                return

            if "Pompes" in exercise or "Push-ups" in exercise:
                dash.withdraw()
                counter = HandPushupCounter(dash, lambda count: on_pushup_count_complete(count, exercise, weight_val, cin, dash))
                counter.open_camera()
            else:
                save_exercise_directly(exercise, weight_val, cin, dash)

        def on_pushup_count_complete(count, exercise, weight_val, cin, dash):
            if count is None:
                messagebox.showwarning("Comptage annulé", "Le comptage des pompes a été annulé.", parent=dash)
                dash.deiconify()
                return
           
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            session_data = f"[{current_time}]\nExercise: {exercise}\nWeight: {weight_val} kg\nPompes: {count}"

            members_file = "members_data.json"
            try:
                if os.path.exists(members_file):
                    with open(members_file, 'r', encoding='utf-8') as f:
                        members_data = json.load(f)
                else:
                    members_data = {}

                if cin in members_data:
                    if 'training_sessions' not in members_data[cin]:
                        members_data[cin]['training_sessions'] = []
                    if 'weights' not in members_data[cin]:
                        members_data[cin]['weights'] = []

                    members_data[cin]['training_sessions'].append(session_data)
                    members_data[cin]['weights'].append(f"[{current_time}] {weight_val} kg")
                    members_data[cin]['last_activity'] = date.today().strftime("%Y-%m-%d")

                    with open(members_file, 'w', encoding='utf-8') as f:
                        json.dump(members_data, f, ensure_ascii=False, indent=4)

                    messagebox.showinfo("Succès", f"Séance enregistrée!\n\nExercice: {exercise}\nPoids: {weight_val} kg\nPompes comptées: {count}", parent=dash)
                    dash.destroy()
                else:
                    messagebox.showerror("Erreur", "Membre non trouvé dans les données.", parent=dash)
                    dash.deiconify()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {e}", parent=dash)
                dash.deiconify()

        def save_exercise_directly(exercise, weight_val, cin, dash):
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            session_data = f"[{current_time}]\nExercise: {exercise}\nWeight: {weight_val} kg"

            members_file = "members_data.json"
            try:
                if os.path.exists(members_file):
                    with open(members_file, 'r', encoding='utf-8') as f:
                        members_data = json.load(f)
                else:
                    members_data = {}

                if cin in members_data:
                    if 'training_sessions' not in members_data[cin]:
                        members_data[cin]['training_sessions'] = []
                    if 'weights' not in members_data[cin]:
                        members_data[cin]['weights'] = []

                    members_data[cin]['training_sessions'].append(session_data)
                    members_data[cin]['weights'].append(f"[{current_time}] {weight_val} kg")
                    members_data[cin]['last_activity'] = date.today().strftime("%Y-%m-%d")

                    with open(members_file, 'w', encoding='utf-8') as f:
                        json.dump(members_data, f, ensure_ascii=False, indent=4)

                    messagebox.showinfo("Succès", f"Séance enregistrée!\n\nExercice: {exercise}\nPoids: {weight_val} kg", parent=dash)
                    dash.destroy()
                else:
                    messagebox.showerror("Erreur", "Membre non trouvé dans les données.", parent=dash)
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {e}", parent=dash)

        save_btn = ModernButton(buttons_frame,
                              text="💾 Enregistrer la Séance",
                              bg=SUCCESS_GREEN,
                              fg='white',
                              command=save_session)
        save_btn.pack(side='left', padx=10)

        close_btn = ModernButton(buttons_frame,
                               text="❌ Fermer",
                               bg=ERROR_RED,
                               fg='white',
                               command=dash.destroy)
        close_btn.pack(side='left', padx=10)

    def open_member_management(self):
        """Ouvre la gestion moderne des membres"""
        member_mgmt_window = tk.Toplevel(self.root)
        MemberManagement(member_mgmt_window)

    def open_performance_tracking(self):
        """Ouvre le suivi moderne des performances"""
        member_mgmt_window = tk.Toplevel(self.root)
        app = MemberManagement(member_mgmt_window)
        app.notebook.select(2)

    def open_session_planning(self):
        messagebox.showinfo("Planification", "Module de planification moderne en développement")

    def open_communication(self):
        messagebox.showinfo("Communication", "Module de communication moderne en développement")

    def open_weight_tracking(self):
        """Ouvre l'interface de suivi des poids avec sélection d'adhérent et courbe"""
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import matplotlib.dates as mdates
       
        weight_window = tk.Toplevel(self.root)
        weight_window.title("📈 Suivi des Poids")
        weight_window.geometry("1000x600")
       
        # Header
        header = tk.Frame(weight_window, bg=SUCCESS_GREEN, height=50)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="📈 Suivi des Poids par Adhérent",
                font=(FONT_PRIMARY, 14, 'bold'), fg='white', bg=SUCCESS_GREEN).pack(expand=True)
       
        # Control frame avec sélecteur d'adhérent
        control_frame = tk.Frame(weight_window, bg=LIGHT_BG)
        control_frame.pack(fill='x', padx=10, pady=10)
       
        tk.Label(control_frame, text="Sélectionner un adhérent:", font=(FONT_PRIMARY, 10), bg=LIGHT_BG).pack(side='left', padx=5)
       
        try:
            with open('members_data.json', 'r', encoding='utf-8') as f:
                members_data = json.load(f)
        except:
            members_data = {}
       
        member_names = []
        member_map = {}
        for mid, m in members_data.items():
            name = m.get('name') or f"{m.get('first_name', '')} {m.get('last_name', '')}".strip()
            if not name:
                name = str(mid)
            member_names.append(name)
            member_map[name] = (mid, m)
       
        member_var = tk.StringVar(value=member_names[0] if member_names else "")
        member_combo = ttk.Combobox(control_frame, textvariable=member_var,
                                   values=member_names, state='readonly', width=30)
        member_combo.pack(side='left', padx=5, fill='x', expand=True)
       
        # Frame pour le graphique
        canvas_frame = tk.Frame(weight_window)
        canvas_frame.pack(fill='both', expand=True, padx=10, pady=10)
       
        def update_chart(event=None):
            # Nettoyer le canvas
            for widget in canvas_frame.winfo_children():
                widget.destroy()
           
            # Créer la figure
            fig = Figure(figsize=(12, 5), dpi=80, facecolor='white')
            ax = fig.add_subplot(111)
           
            selected_name = member_var.get()
            if selected_name not in member_map:
                ax.set_title('Aucun adhérent sélectionné')
                canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill='both', expand=True)
                return
           
            mid, member = member_map[selected_name]
            weight_history = member.get('weight_history', [])
           
            if not weight_history:
                ax.set_title(f'Aucune donnée de poids pour {selected_name}')
                canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill='both', expand=True)
                return
           
            # Parser les données de poids
            dates = []
            weights = []
            for entry in weight_history:
                try:
                    if isinstance(entry, dict):
                        date_str = entry.get('date', '')
                        weight = entry.get('weight', 0)
                    elif isinstance(entry, (tuple, list)):
                        date_str, weight = entry[0], entry[1]
                    else:
                        continue
                   
                    if isinstance(date_str, str) and '] ' in date_str:
                        date_str = date_str.split('] ')[0].replace('[', '')
                   
                    date_obj = datetime.strptime(date_str.strip(), '%Y-%m-%d')
                    dates.append(date_obj)
                    weights.append(float(weight))
                except:
                    continue
           
            if dates and weights:
                ax.plot(dates, weights, marker='o', color=SUCCESS_GREEN, linewidth=2.5, markersize=8)
                ax.set_title(f'Progression du Poids - {selected_name}', fontsize=14, fontweight='bold')
                ax.set_xlabel('Date', fontsize=11, fontweight='bold')
                ax.set_ylabel('Poids (kg)', fontsize=11, fontweight='bold')
                ax.grid(True, alpha=0.3)
               
                # Formatage des dates
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                fig.autofmt_xdate(rotation=45)
            else:
                ax.set_title(f'Pas de données valides pour {selected_name}')
           
            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
       
        # Bind la sélection du combo
        member_combo.bind('<<ComboboxSelected>>', update_chart)
       
        # Afficher le premier graphique
        if member_names:
            update_chart()

# Les classes FacialRecognitionCamera et HandPushupCounter restent similaires
# mais seraient stylisées avec le même design moderne

class FacialRecognitionCamera:
    def __init__(self, parent_window, callback):
        self.parent = parent_window
        self.callback = callback
        self.camera_window = None
        self.cap = None
        self.running = False
        self.photo_captured = False
        self.captured_image = None
       
    def open_camera(self):
        """Ouvre la fenêtre de capture photo avec reconnaissance faciale moderne"""
        self.camera_window = tk.Toplevel(self.parent)
        self.camera_window.title("INNOVERSE - Reconnaissance Faciale")
        self.camera_window.geometry("800x600")
        self.camera_window.configure(bg=PRIMARY_DARK)
        self.camera_window.protocol("WM_DELETE_WINDOW", self.close_camera)
       
        self.center_window(800, 600)
       
        # Header moderne
        header = tk.Frame(self.camera_window, bg=PRIMARY_BLUE, height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
       
        tk.Label(header,
                text="🔍 Reconnaissance Faciale",
                font=(FONT_PRIMARY, 18, 'bold'),
                fg='white',
                bg=PRIMARY_BLUE).pack(expand=True)
       
        # Frame pour la webcam
        camera_frame = CardFrame(self.camera_window)
        camera_frame.pack(pady=20, padx=50, fill='both', expand=True)
       
        self.camera_label = tk.Label(camera_frame, bg='#f8fafc')
        self.camera_label.pack(pady=20, padx=20, fill='both', expand=True)
       
        # Frame pour les boutons
        buttons_frame = tk.Frame(self.camera_window, bg=PRIMARY_DARK)
        buttons_frame.pack(pady=20)
       
        capture_button = ModernButton(buttons_frame,
                                    text="📸 Capturer la Photo",
                                    bg=SUCCESS_GREEN,
                                    fg='white',
                                    command=self.capture_photo)
        capture_button.pack(side='left', padx=10)
       
        cancel_button = ModernButton(buttons_frame,
                                   text="❌ Annuler",
                                   bg=ERROR_RED,
                                   fg='white',
                                   command=self.close_camera)
        cancel_button.pack(side='left', padx=10)
       
        # Instructions
        instructions = tk.Label(self.camera_window,
                               text="Positionnez votre visage dans le cadre et cliquez sur 'Capturer la Photo'",
                               font=(FONT_PRIMARY, 10),
                               fg=TEXT_LIGHT,
                               bg=PRIMARY_DARK)
        instructions.pack(pady=10)
       
        self.start_camera()
   
    def center_window(self, width, height):
        """Centre la fenêtre"""
        self.camera_window.update_idletasks()
        x = (self.camera_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.camera_window.winfo_screenheight() // 2) - (height // 2)
        self.camera_window.geometry(f'{width}x{height}+{x}+{y}')
   
    def start_camera(self):
        """Démarre la webcam dans un thread séparé"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Erreur", "Impossible d'accéder à la webcam")
            self.camera_window.destroy()
            return
       
        self.running = True
        haar_path = get_haar_cascade_path()
        self.face_cascade = cv2.CascadeClassifier(haar_path)
       
        self.camera_thread = threading.Thread(target=self.update_camera, daemon=True)
        self.camera_thread.start()
   
    def update_camera(self):
        """Met à jour l'affichage de la webcam en temps réel"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
               
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
               
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame_rgb, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame_rgb, 'Visage detecte', (x, y-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
               
                frame_resized = cv2.resize(frame_rgb, (640, 480))
                img = Image.fromarray(frame_resized)
                imgtk = ImageTk.PhotoImage(image=img)
               
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)
               
                self.current_frame = frame.copy()
           
            time.sleep(0.02)
   
    def capture_photo(self):
        """Capture la photo actuelle"""
        if hasattr(self, 'current_frame'):
            frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            self.captured_image = frame_rgb
           
            gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
           
            if len(faces) > 0:
                self.photo_captured = True
                messagebox.showinfo("Succès", "Photo capturée avec succès!\nVisage détecté.", parent=self.camera_window)
                self.close_camera()
            else:
                messagebox.showwarning("Attention", "Aucun visage détecté!\nVeuillez vous positionner face à la caméra.", parent=self.camera_window)
        else:
            messagebox.showerror("Erreur", "Impossible de capturer la photo", parent=self.camera_window)
   
    def close_camera(self):
        """Ferme la caméra et la fenêtre"""
        self.running = False
        if self.cap:
            self.cap.release()
        if self.camera_window:
            self.camera_window.destroy()
       
        if hasattr(self, 'photo_captured') and self.photo_captured:
            self.callback(True, self.captured_image)
        else:
            self.callback(False, None)

class HandPushupCounter:
    """Classe moderne pour compter les pompes via détection des mains avec MediaPipe."""
   
    def __init__(self, parent_window, callback):
        self.parent = parent_window
        self.callback = callback
        self.camera_window = None
        self.cap = None
        self.running = False
        self.pushup_count = 0
       
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
       
        # State tracking for push-up counting
        self.wrist_heights = []
        self.in_down_position = False
        self.in_up_position = False
   
    def open_camera(self):
        """Ouvre la fenêtre de capture moderne pour compter les pompes."""
        self.camera_window = tk.Toplevel(self.parent)
        self.camera_window.title("INNOVERSE - Comptage des Pompes")
        self.camera_window.geometry("900x700")
        self.camera_window.configure(bg=PRIMARY_DARK)
        self.camera_window.protocol("WM_DELETE_WINDOW", self.close_camera)
       
        self.center_window(900, 700)
       
        # Header moderne
        header = tk.Frame(self.camera_window, bg=PRIMARY_BLUE, height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
       
        tk.Label(header,
                text="🏋️‍♂️ Comptage des Pompes",
                font=(FONT_PRIMARY, 16, 'bold'),
                fg='white',
                bg=PRIMARY_BLUE).pack(side='left', padx=20)
       
        # Counter display
        self.counter_label = tk.Label(header,
                                     text="Pompes: 0",
                                     font=(FONT_PRIMARY, 18, 'bold'),
                                     fg=SUCCESS_GREEN,
                                     bg=PRIMARY_BLUE)
        self.counter_label.pack(side='right', padx=20)
       
        # Caméra frame
        camera_frame = CardFrame(self.camera_window)
        camera_frame.pack(pady=20, padx=20, fill='both', expand=True)
       
        self.camera_label = tk.Label(camera_frame, bg='#f8fafc')
        self.camera_label.pack(pady=15, padx=15, fill='both', expand=True)
       
        # Instructions
        instructions = tk.Label(self.camera_window,
                               text="Instructions: Positionnez-vous face à la caméra et faites des pompes. Les mains seront détectées automatiquement.",
                               font=(FONT_PRIMARY, 10),
                               fg=TEXT_LIGHT,
                               bg=PRIMARY_DARK,
                               wraplength=850)
        instructions.pack(pady=10)
       
        # Buttons
        buttons_frame = tk.Frame(self.camera_window, bg=PRIMARY_DARK)
        buttons_frame.pack(pady=20)
       
        finish_button = ModernButton(buttons_frame,
                                   text="✓ Terminer et Sauvegarder",
                                   bg=SUCCESS_GREEN,
                                   fg='white',
                                   command=self.finish_counting)
        finish_button.pack(side='left', padx=10)
       
        cancel_button = ModernButton(buttons_frame,
                                   text="❌ Annuler",
                                   bg=ERROR_RED,
                                   fg='white',
                                   command=self.close_camera)
        cancel_button.pack(side='left', padx=10)
       
        self.start_camera()
   
    def center_window(self, width, height):
        """Centre la fenêtre"""
        self.camera_window.update_idletasks()
        x = (self.camera_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.camera_window.winfo_screenheight() // 2) - (height // 2)
        self.camera_window.geometry(f'{width}x{height}+{x}+{y}')
   
    def start_camera(self):
        """Démarre la caméra dans un thread séparé."""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Erreur", "Impossible d'accéder à la webcam")
            self.camera_window.destroy()
            return
       
        self.running = True
        self.camera_thread = threading.Thread(target=self.update_camera, daemon=True)
        self.camera_thread.start()
   
    def update_camera(self):
        """Met à jour l'affichage de la caméra en temps réel avec détection des mains."""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_rgb.flags.writeable = False
               
                results = self.hands.process(frame_rgb)
                frame_rgb.flags.writeable = True
               
                if results.multi_hand_landmarks and len(results.multi_hand_landmarks) >= 2:
                    hand1 = results.multi_hand_landmarks[0]
                    hand2 = results.multi_hand_landmarks[1]
                   
                    wrist1 = hand1.landmark[0]
                    wrist2 = hand2.landmark[0]
                   
                    hand_distance = ((wrist1.x - wrist2.x) ** 2 + (wrist1.y - wrist2.y) ** 2) ** 0.5
                   
                    self.wrist_heights.append(hand_distance)
                   
                    if len(self.wrist_heights) > 15:
                        self.wrist_heights.pop(0)
                   
                    if len(self.wrist_heights) >= 10:
                        recent_distances = self.wrist_heights[-10:]
                        max_distance = max(recent_distances)
                        min_distance = min(recent_distances)
                       
                        if (max_distance - min_distance) > 0.15:
                            if hand_distance <= min_distance + 0.05 and not self.in_down_position:
                                self.in_down_position = True
                                self.in_up_position = False
                           
                            elif hand_distance >= max_distance - 0.08 and self.in_down_position:
                                self.in_down_position = False
                                self.in_up_position = True
                                self.pushup_count += 1
                   
                    self.mp_drawing.draw_landmarks(frame_rgb, hand1, self.mp_hands.HAND_CONNECTIONS)
                    self.mp_drawing.draw_landmarks(frame_rgb, hand2, self.mp_hands.HAND_CONNECTIONS)
                   
                    cv2.putText(frame_rgb, f"Distance: {hand_distance:.2f}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    self.wrist_heights = []
                    self.in_down_position = False
                    self.in_up_position = False
               
                frame_rgb = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                frame_resized = cv2.resize(frame_rgb, (880, 550))
               
                img = Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB))
                imgtk = ImageTk.PhotoImage(image=img)
               
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)
               
                self.counter_label.config(text=f"Pompes: {self.pushup_count}")
           
            cv2.waitKey(1)
   
    def finish_counting(self):
        """Termine le comptage et retourne le nombre de pompes."""
        self.running = False
        if self.cap:
            self.cap.release()
        if self.camera_window:
            self.camera_window.destroy()
       
        self.callback(self.pushup_count)
   
    def close_camera(self):
        """Ferme la caméra sans enregistrer."""
        self.running = False
        if self.cap:
            self.cap.release()
        if self.camera_window:
            self.camera_window.destroy()
       
        self.callback(None)

class MemberManagement:
    def __init__(self, root):
        self.root = root
        self.root.title("INNOVERSE - Gestion des Membres")
        self.root.geometry("1400x900")
        self.root.configure(bg=LIGHT_BG)
       
        # Fichier de stockage des membres
        self.members_file = "members_data.json"
        self.photos_dir = "member_photos"
        self.load_members_data()
        self.create_photos_directory()
       
        self.create_widgets()
   
    def create_photos_directory(self):
        """Crée le dossier pour stocker les photos des membres"""
        if not os.path.exists(self.photos_dir):
            os.makedirs(self.photos_dir)
   
    def load_members_data(self):
        """Charge les données des membres depuis le fichier JSON"""
        if os.path.exists(self.members_file):
            try:
                with open(self.members_file, 'r', encoding='utf-8') as f:
                    self.members_data = json.load(f)
            except:
                self.members_data = {}
        else:
            self.members_data = {}
   
    def save_members_data(self):
        """Sauvegarde les données des membres dans le fichier JSON"""
        try:
            with open(self.members_file, 'w', encoding='utf-8') as f:
                json.dump(self.members_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {e}")
   
    def create_widgets(self):
        # Header moderne
        header_frame = tk.Frame(self.root, bg=PRIMARY_BLUE, height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
       
        header_label = tk.Label(
            header_frame,
            text="👥 Gestion des Membres - INNOVERSE",
            font=(FONT_PRIMARY, 20, 'bold'),
            fg='white',
            bg=PRIMARY_BLUE
        )
        header_label.pack(expand=True)
       
        # Bouton retour
        back_button = ModernButton(
            header_frame,
            text="← Retour au Dashboard",
            bg=ERROR_RED,
            fg='white',
            command=self.root.destroy
        )
        back_button.pack(side='right', padx=20)
       
        # Notebook moderne
        self.notebook = ttk.Notebook(self.root, style='Modern.TNotebook')
        self.notebook.pack(expand=True, fill='both', padx=20, pady=20)
       
        # Onglet 1: Ajouter un nouveau membre
        self.create_add_member_tab(self.notebook)
       
        # Onglet 2: Liste des membres et suivi
        self.create_member_list_tab(self.notebook)
       
        # Onglet 3: Suivi des performances
        self.create_performance_tab(self.notebook)
   
    def create_add_member_tab(self, notebook):
        """Onglet moderne pour ajouter un nouveau membre"""
        add_frame = ttk.Frame(notebook)
        notebook.add(add_frame, text="➕ Nouveau Membre")
       
        # Titre
        title_label = tk.Label(
            add_frame,
            text="Ajouter un Nouveau Membre",
            font=(FONT_PRIMARY, 24, 'bold'),
            fg=TEXT_DARK,
            bg=LIGHT_BG
        )
        title_label.pack(pady=30)
       
        # Formulaire dans une carte
        form_card = CardFrame(add_frame)
        form_card.pack(expand=True, fill='both', padx=100, pady=20)
       
        # Grid pour les champs
        form_grid = tk.Frame(form_card, bg=CARD_BG)
        form_grid.pack(expand=True, fill='both', padx=40, pady=40)
       
        # CIN
        tk.Label(form_grid, text="CIN *", font=(FONT_PRIMARY, 11, 'bold'),
                bg=CARD_BG, fg=TEXT_DARK).grid(row=0, column=0, sticky='w', pady=10)
        self.cin_entry = tk.Entry(form_grid, font=(FONT_PRIMARY, 11), width=30)
        self.cin_entry.grid(row=0, column=1, sticky='ew', pady=10, padx=(20, 0))
       
        # Prénom
        tk.Label(form_grid, text="Prénom *", font=(FONT_PRIMARY, 11, 'bold'),
                bg=CARD_BG, fg=TEXT_DARK).grid(row=1, column=0, sticky='w', pady=10)
        self.first_name_entry = tk.Entry(form_grid, font=(FONT_PRIMARY, 11), width=30)
        self.first_name_entry.grid(row=1, column=1, sticky='ew', pady=10, padx=(20, 0))
       
        # Nom
        tk.Label(form_grid, text="Nom *", font=(FONT_PRIMARY, 11, 'bold'),
                bg=CARD_BG, fg=TEXT_DARK).grid(row=2, column=0, sticky='w', pady=10)
        self.last_name_entry = tk.Entry(form_grid, font=(FONT_PRIMARY, 11), width=30)
        self.last_name_entry.grid(row=2, column=1, sticky='ew', pady=10, padx=(20, 0))
       
        # Date de naissance
        tk.Label(form_grid, text="Date de naissance", font=(FONT_PRIMARY, 11, 'bold'),
                bg=CARD_BG, fg=TEXT_DARK).grid(row=3, column=0, sticky='w', pady=10)
        self.dob_entry = tk.Entry(form_grid, font=(FONT_PRIMARY, 11), width=30)
        self.dob_entry.grid(row=3, column=1, sticky='ew', pady=10, padx=(20, 0))
       
        # Téléphone
        tk.Label(form_grid, text="Téléphone", font=(FONT_PRIMARY, 11, 'bold'),
                bg=CARD_BG, fg=TEXT_DARK).grid(row=4, column=0, sticky='w', pady=10)
        self.phone_entry = tk.Entry(form_grid, font=(FONT_PRIMARY, 11), width=30)
        self.phone_entry.grid(row=4, column=1, sticky='ew', pady=10, padx=(20, 0))
       
        form_grid.columnconfigure(1, weight=1)
       
        # Section photo
        photo_section = tk.Frame(form_card, bg=CARD_BG)
        photo_section.pack(fill='x', padx=40, pady=20)
       
        self.photo_status = tk.Label(
            photo_section,
            text="📷 Aucune photo capturée",
            font=(FONT_PRIMARY, 11),
            bg=CARD_BG,
            fg=TEXT_LIGHT
        )
        self.photo_status.pack(anchor='w', pady=(0, 10))
       
        photo_button = ModernButton(photo_section,
                                  text="📸 Capture Photo avec Reconnaissance Faciale",
                                  bg=ACCENT_BLUE,
                                  fg='white',
                                  command=self.open_facial_recognition)
        photo_button.pack(pady=10)
       
        self.captured_photo = None
       
        # Boutons
        buttons_frame = tk.Frame(form_card, bg=CARD_BG)
        buttons_frame.pack(pady=30)
       
        save_button = ModernButton(buttons_frame,
                                 text="💾 Enregistrer le Membre",
                                 bg=SUCCESS_GREEN,
                                 fg='white',
                                 command=self.save_member)
        save_button.pack(side='left', padx=10)
       
        clear_button = ModernButton(buttons_frame,
                                  text="🗑️ Effacer le Formulaire",
                                  bg=ERROR_RED,
                                  fg='white',
                                  command=self.clear_form)
        clear_button.pack(side='left', padx=10)
   
    def open_facial_recognition(self):
        """Ouvre la caméra avec reconnaissance faciale"""
        self.facial_camera = FacialRecognitionCamera(self.root, self.on_photo_captured)
        self.facial_camera.open_camera()
   
    def on_photo_captured(self, success, image):
        """Callback appelé quand une photo est capturée"""
        if success and image is not None:
            self.captured_photo = image
            self.photo_status.config(
                text="✅ Photo capturée avec reconnaissance faciale",
                fg=SUCCESS_GREEN
            )
           
            try:
                img_pil = Image.fromarray(image)
                self.temp_photo_path = os.path.join(self.photos_dir, f"temp_photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
                img_pil.save(self.temp_photo_path)
            except Exception as e:
                print(f"Erreur sauvegarde photo: {e}")
        else:
            self.captured_photo = None
            self.photo_status.config(
                text="📷 Aucune photo capturée",
                fg=TEXT_LIGHT
            )
   
    def create_member_list_tab(self, notebook):
        """Onglet moderne pour la liste des membres et détails"""
        list_frame = ttk.Frame(notebook)
        notebook.add(list_frame, text="👥 Liste des Membres")
       
        # Frame principal avec split view
        main_split = tk.Frame(list_frame, bg=LIGHT_BG)
        main_split.pack(fill='both', expand=True, padx=20, pady=20)
       
        # Left panel - Liste des membres
        left_panel = CardFrame(main_split)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
       
        tk.Label(left_panel,
                text="Liste des Membres",
                font=(FONT_PRIMARY, 16, 'bold'),
                fg=TEXT_DARK,
                bg=CARD_BG).pack(pady=20)
       
        # Liste avec scrollbar
        listbox_frame = tk.Frame(left_panel, bg=CARD_BG)
        listbox_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
       
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')
       
        self.members_listbox = tk.Listbox(
            listbox_frame,
            font=(FONT_PRIMARY, 11),
            yscrollcommand=scrollbar.set,
            selectmode='single',
            relief='flat',
            bd=0,
            highlightthickness=0
        )
        self.members_listbox.pack(fill='both', expand=True)
        self.members_listbox.bind('<<ListboxSelect>>', self.show_member_details)
       
        scrollbar.config(command=self.members_listbox.yview)
       
        # Right panel - Détails du membre
        right_panel = CardFrame(main_split)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
       
        tk.Label(right_panel,
                text="Détails du Membre",
                font=(FONT_PRIMARY, 16, 'bold'),
                fg=TEXT_DARK,
                bg=CARD_BG).pack(pady=20)
       
        self.details_text = scrolledtext.ScrolledText(
            right_panel,
            font=(FONT_PRIMARY, 11),
            bg='#f8fafc',
            fg=TEXT_DARK,
            relief='flat',
            bd=1,
            highlightbackground='#e2e8f0'
        )
        self.details_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))
       
        self.refresh_members_list()
   
    def create_performance_tab(self, notebook):
        """Onglet moderne pour le suivi des performances"""
        perf_frame = ttk.Frame(notebook)
        notebook.add(perf_frame, text="📊 Suivi des Performances")
       
        # Titre
        title_label = tk.Label(
            perf_frame,
            text="Suivi des Performances des Membres",
            font=(FONT_PRIMARY, 20, 'bold'),
            fg=TEXT_DARK,
            bg=LIGHT_BG
        )
        title_label.pack(pady=30)
       
        # Frame principal
        main_frame = tk.Frame(perf_frame, bg=LIGHT_BG)
        main_frame.pack(expand=True, fill='both', padx=40, pady=20)
       
        # Sélection du membre
        select_card = CardFrame(main_frame)
        select_card.pack(fill='x', pady=(0, 20))
       
        tk.Label(select_card,
                text="Sélectionner un membre:",
                font=(FONT_PRIMARY, 12, 'bold'),
                fg=TEXT_DARK,
                bg=CARD_BG).pack(anchor='w', padx=20, pady=15)
       
        self.member_var = tk.StringVar()
        self.member_combobox = ttk.Combobox(
            select_card,
            textvariable=self.member_var,
            font=(FONT_PRIMARY, 11),
            state='readonly'
        )
        self.member_combobox.pack(fill='x', padx=20, pady=(0, 15))
        self.member_combobox.bind('<<ComboboxSelected>>', self.show_member_performance)
       
        # Frame pour les performances
        perf_split = tk.Frame(main_frame, bg=LIGHT_BG)
        perf_split.pack(fill='both', expand=True)
       
        # Séances d'entraînement
        training_card = CardFrame(perf_split)
        training_card.pack(side='left', fill='both', expand=True, padx=(0, 10))
       
        tk.Label(training_card,
                text="📈 Séances d'entraînement",
                font=(FONT_PRIMARY, 14, 'bold'),
                fg=TEXT_DARK,
                bg=CARD_BG).pack(pady=15)
       
        self.training_text = scrolledtext.ScrolledText(
            training_card,
            font=(FONT_PRIMARY, 10),
            bg='#f8fafc'
        )
        self.training_text.pack(fill='both', expand=True, padx=15, pady=(0, 15))
       
        # Poids enregistrés
        weights_card = CardFrame(perf_split)
        weights_card.pack(side='right', fill='both', expand=True, padx=(10, 0))
       
        tk.Label(weights_card,
                text="⚖️ Poids enregistrés",
                font=(FONT_PRIMARY, 14, 'bold'),
                fg=TEXT_DARK,
                bg=CARD_BG).pack(pady=15)
       
        self.weights_text = scrolledtext.ScrolledText(
            weights_card,
            font=(FONT_PRIMARY, 10),
            bg='#f8fafc'
        )
        self.weights_text.pack(fill='both', expand=True, padx=15, pady=(0, 15))
       
        # Charger la liste des membres
        self.refresh_members_combobox()
   
    def save_member(self):
        """Sauvegarde un nouveau membre"""
        cin = self.cin_entry.get().strip()
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        dob = self.dob_entry.get().strip()
        phone = self.phone_entry.get().strip()
       
        if not cin or not first_name or not last_name:
            messagebox.showerror("Erreur", "Veuillez remplir les champs obligatoires (*)")
            return
       
        if cin in self.members_data:
            messagebox.showerror("Erreur", "Un membre avec ce CIN existe déjà")
            return
       
        photo_path = None
        if self.captured_photo is not None:
            try:
                photo_filename = f"{cin}_{first_name}_{last_name}.jpg"
                photo_path = os.path.join(self.photos_dir, photo_filename)
                img_pil = Image.fromarray(self.captured_photo)
                img_pil.save(photo_path)
            except Exception as e:
                print(f"Erreur sauvegarde photo: {e}")
                photo_path = None
       
        self.members_data[cin] = {
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': dob,
            'phone': phone,
            'photo_path': photo_path,
            'registration_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'training_sessions': [],
            'weights': [],
            'last_activity': date.today().strftime("%Y-%m-%d")
        }
       
        self.save_members_data()
        messagebox.showinfo("Succès", f"Membre {first_name} {last_name} ajouté avec succès!")
        self.clear_form()
        self.refresh_members_list()
        self.refresh_members_combobox()
   
    def clear_form(self):
        """Efface le formulaire"""
        self.cin_entry.delete(0, tk.END)
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.dob_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.captured_photo = None
        self.photo_status.config(
            text="📷 Aucune photo capturée",
            fg=TEXT_LIGHT
        )
   
    def refresh_members_list(self):
        """Rafraîchit la liste des membres"""
        self.members_listbox.delete(0, tk.END)
        for cin, data in self.members_data.items():
            display_text = f"{data['first_name']} {data['last_name']} (CIN: {cin})"
            self.members_listbox.insert(tk.END, display_text)
   
    def refresh_members_combobox(self):
        """Rafraîchit la combobox des membres"""
        members = []
        for cin, data in self.members_data.items():
            members.append(f"{data['first_name']} {data['last_name']} - {cin}")
        self.member_combobox['values'] = members
        if members:
            self.member_combobox.set(members[0])
   
    def show_member_details(self, event):
        """Affiche les détails du membre sélectionné"""
        selection = self.members_listbox.curselection()
        if not selection:
            return
       
        index = selection[0]
        member_text = self.members_listbox.get(index)
        cin = member_text.split("CIN: ")[1].strip(")")
       
        if cin in self.members_data:
            member = self.members_data[cin]
           
            details = f"""CIN: {cin}
Nom: {member['last_name']}
Prénom: {member['first_name']}
Date de naissance: {member['date_of_birth']}
Téléphone: {member['phone']}
Date d'inscription: {member['registration_date']}
Dernière activité: {member.get('last_activity', 'Jamais')}
Photo: {'✅ Oui' if member.get('photo_path') else '❌ Non'}

Historique des séances:"""
           
            for session in member['training_sessions']:
                details += f"\n{session}"
           
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, details)
   
    def show_member_performance(self, event):
        """Affiche les performances du membre sélectionné"""
        member_text = self.member_var.get()
        if not member_text:
            return
       
        cin = member_text.split(" - ")[1]
       
        if cin in self.members_data:
            member = self.members_data[cin]
           
            self.training_text.delete(1.0, tk.END)
            training_info = f"Membre: {member['first_name']} {member['last_name']}\n\n"
           
            for i, session in enumerate(member['training_sessions'], 1):
                training_info += f"Séance {i}:\n"
                training_info += f"  {session}\n\n"
           
            self.training_text.insert(1.0, training_info)
           
            self.weights_text.delete(1.0, tk.END)
            weights_info = f"Poids enregistrés:\n\n"
           
            for i, weight_data in enumerate(member['weights'], 1):
                weights_info += f"Enregistrement {i}:\n"
                weights_info += f"  {weight_data}\n\n"
           
            self.weights_text.insert(1.0, weights_info)

def main():
    root = tk.Tk()
    app = InnoversApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

