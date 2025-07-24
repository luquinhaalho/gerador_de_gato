# ui.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO
import threading

# Importa nossos módulos customizados
import api_service
from config import MAX_IMG_WIDTH, INITIAL_WINDOW_GEOMETRY, FONT_SIZES, FONT_COLORS

class CatViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Gatos Organizado")
        self.root.geometry(INITIAL_WINDOW_GEOMETRY)

        self.all_tags = []
        self._build_ui()
        self.start_fetching_tags()

    def _build_ui(self):
        """Constrói todos os widgets da interface gráfica."""
        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Seção de Filtros (Tag e Texto)
        self._build_filter_section()

        # Estrutura de Rolagem
        self._build_scrollable_area()
        
        # Ativa rolagem com a roda do mouse
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _build_filter_section(self):
        """Constrói a parte superior da UI com os filtros."""
        tag_frame = ttk.Frame(self.main_frame)
        tag_frame.pack(pady=5, fill=tk.X)
        ttk.Label(tag_frame, text="Filtrar por Tag:").pack(side=tk.LEFT, padx=(0, 10))
        self.tag_combobox = ttk.Combobox(tag_frame)
        self.tag_combobox.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.tag_combobox.set("Carregando tags...")
        self.tag_combobox.bind('<KeyRelease>', self.on_keyrelease)
        
        text_frame = ttk.LabelFrame(self.main_frame, text="Adicionar Texto na Imagem", padding="10")
        text_frame.pack(pady=15, fill=tk.X)
        ttk.Label(text_frame, text="Texto:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.text_entry = ttk.Entry(text_frame)
        self.text_entry.grid(row=0, column=1, columnspan=3, sticky="we", padx=5, pady=5)
        ttk.Label(text_frame, text="Tamanho:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.size_combobox = ttk.Combobox(text_frame, state="readonly", width=10, values=FONT_SIZES)
        self.size_combobox.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.size_combobox.set(FONT_SIZES[2]) # Pega o terceiro valor como padrão
        ttk.Label(text_frame, text="Cor:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.color_combobox = ttk.Combobox(text_frame, state="readonly", width=10, values=FONT_COLORS)
        self.color_combobox.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        self.color_combobox.set(FONT_COLORS[0]) # Pega o primeiro valor como padrão
        text_frame.columnconfigure(1, weight=1)
        text_frame.columnconfigure(3, weight=1)
        
    def _build_scrollable_area(self):
        """Constrói a área rolável que contém a imagem e os botões."""
        self.canvas = tk.Canvas(self.main_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, pady=(10,0))
        self.scrollbar.pack(side="right", fill="y", pady=(10,0))

        self.image_label = ttk.Label(self.scrollable_frame, text="Buscando lista de tags...")
        self.image_label.pack(pady=10, padx=10, expand=True)

        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.pack(pady=20)
        self.next_button = ttk.Button(button_frame, text="Próximo Gato", command=self.start_fetching_image, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=15, ipady=5)
        self.close_button = ttk.Button(button_frame, text="Fechar", command=self.root.destroy)
        self.close_button.pack(side=tk.LEFT, padx=15, ipady=5)

    def start_fetching_tags(self):
        threading.Thread(target=self._fetch_and_setup_tags, daemon=True).start()

    def _fetch_and_setup_tags(self):
        try:
            self.all_tags = api_service.fetch_tags()
            self.tag_combobox['values'] = self.all_tags
            self.tag_combobox.set("Aleatório")
            self._set_controls_state(loading=False)
            self.image_label.config(text="Pronto! Personalize seu gato e clique no botão.")
        except Exception as e:
            self.image_label.config(text=f"Erro ao carregar tags: {e}")
            self.tag_combobox.set("Falha ao carregar")

    def start_fetching_image(self):
        threading.Thread(target=self._fetch_and_display_image, daemon=True).start()

    def _fetch_and_display_image(self):
        self._set_controls_state(loading=True)
        self.image_label.config(text="Montando sua imagem de gato...")
        try:
            url = api_service.build_image_url(
                tag=self.tag_combobox.get(),
                text=self.text_entry.get(),
                size=self.size_combobox.get(),
                color=self.color_combobox.get()
            )
            image_data = api_service.fetch_image_data(url)
            
            img = Image.open(BytesIO(image_data))
            if img.width > MAX_IMG_WIDTH:
                ratio = MAX_IMG_WIDTH / img.width
                new_height = int(img.height * ratio)
                img = img.resize((MAX_IMG_WIDTH, new_height), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo
        except Exception as e:
            self.image_label.config(text=f"Erro ao buscar imagem: {e}", image=None)
        finally:
            self._set_controls_state(loading=False)

    def _set_controls_state(self, loading: bool):
        state = tk.DISABLED if loading else tk.NORMAL
        self.next_button.config(state=state)
        self.tag_combobox.config(state=state)
        self.text_entry.config(state=state)
        self.size_combobox.config(state="readonly" if not loading else tk.DISABLED)
        self.color_combobox.config(state="readonly" if not loading else tk.DISABLED)
        self.root.update_idletasks()
        
    def on_keyrelease(self, event):
        typed_text = self.tag_combobox.get().lower()
        if not typed_text:
            self.tag_combobox['values'] = self.all_tags
            return
        self.tag_combobox['values'] = [tag for tag in self.all_tags if tag.lower().startswith(typed_text)]
        
    def _on_mousewheel(self, event):
        delta = -1 * (event.delta // 120) if event.delta != 0 else (1 if event.num == 5 else -1)
        self.canvas.yview_scroll(delta, "units")